import type { ChatService } from "@/types/chat";
import AsyncStorage from "@react-native-async-storage/async-storage";

const AGENT_URL = process.env.EXPO_PUBLIC_AGENT_URL || "http://127.0.0.1:8000";

class HttpChatService implements ChatService {
  async reply(prompt: string): Promise<string> {
    const text = prompt.trim();
    if (!text) return "Could you share a bit more about your goal?";

    // Check if this is a weekly plan request
    if (text.toLowerCase().includes("plan my next week workouts")) {
      return this.generateWeeklyPlan();
    }

    // Check sleep analysis request
    if (text.toLowerCase().includes("analyze my last 30 day sleep")) {
      return this.analyzeLast30DaySleep();
    }

    try {
      const res = await fetch(`${AGENT_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as { text?: string };
      return data.text || "(no response)";
    } catch (e) {
      return "Sorry, I couldn't reach the agent. Is it running?";
    }
  }

  async generateWeeklyPlan(): Promise<string> {
    try {
      const res = await fetch(`${AGENT_URL}/weekly-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as { text?: string };
      return data.text || "(no response)";
    } catch (e) {
      return "Sorry, I couldn't reach the agent to generate your weekly plan. Is it running?";
    }
  }

  private async analyzeLast30DaySleep(): Promise<string> {
    try {
      // Collect up to last 365 days of stored summaries to ensure 30 non-zero entries
      const today = new Date();
      const keys: string[] = [];
      for (let i = 0; i < 365; i++) {
        const d = new Date(today);
        d.setDate(today.getDate() - i);
        const y = d.getFullYear();
        const m = `${d.getMonth() + 1}`.padStart(2, "0");
        const day = `${d.getDate()}`.padStart(2, "0");
        keys.push(`health_daily:${y}-${m}-${day}`);
      }
      const result = await AsyncStorage.multiGet(keys);
      const rowsAll = result
        .map(([key, val]) => {
          if (!val) return null;
          try {
            const parsed = JSON.parse(val) as {
              steps: number;
              active_kcal: number;
              basal_kcal: number;
              sleep_minutes: number;
              sleep_start?: string | null;
              sleep_end?: string | null;
              sleep_source?: "asleep" | "in_bed" | null;
            };
            const date = key.replace("health_daily:", "");
            return { date, ...parsed };
          } catch {
            return null;
          }
        })
        .filter(Boolean) as Array<{
        date: string;
        steps: number;
        active_kcal: number;
        basal_kcal: number;
        sleep_minutes: number;
        sleep_start?: string | null;
        sleep_end?: string | null;
        sleep_source?: "asleep" | "in_bed" | null;
      }>;
      // Filter to non-zero sleep and take latest 30
      const rows = rowsAll
        .filter((r) => (r.sleep_minutes || 0) > 0)
        .sort((a, b) => (a.date < b.date ? -1 : 1));
      const last30 = rows.slice(-30);

      // Build payload for dedicated endpoint
      const days = last30.map((r) => ({
        date: r.date,
        steps: r.steps,
        active_kcal: r.active_kcal,
        basal_kcal: r.basal_kcal,
        sleep_minutes: r.sleep_minutes,
        sleep_start: r.sleep_start ?? null,
        sleep_end: r.sleep_end ?? null,
        sleep_source: r.sleep_source ?? null,
      }));

      const res = await fetch(`${AGENT_URL}/sleep-analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ days }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as { text?: string };
      return data.text || "(no response)";
    } catch (e) {
      return "Sorry, I couldn't analyze your sleep. Please try again after importing health data.";
    }
  }
}

export const chatService: ChatService = new HttpChatService();
