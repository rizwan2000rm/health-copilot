import type { ChatService } from "@/types/chat";

const AGENT_URL = process.env.EXPO_PUBLIC_AGENT_URL || "http://127.0.0.1:8000";

class HttpChatService implements ChatService {
  async reply(prompt: string): Promise<string> {
    const text = prompt.trim();
    if (!text) return "Could you share a bit more about your goal?";
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
}

export const chatService: ChatService = new HttpChatService();
