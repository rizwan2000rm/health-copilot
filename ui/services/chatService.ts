import type { ChatService } from "@/types/chat";

class MockChatService implements ChatService {
  async reply(prompt: string): Promise<string> {
    await new Promise((r) => setTimeout(r, 650));
    const text = prompt.trim();
    if (!text) return "Could you share a bit more about your goal?";
    const lower = text.toLowerCase();
    if (lower.includes("workout") || lower.includes("plan")) {
      return "Here's a simple plan: 3x/week full-body. Day A: Squat, Push-up, Row. Day B: Hinge, Overhead Press, Pull. 2–3 sets of 6–10 reps.";
    }
    if (lower.includes("diet") || lower.includes("nutrition")) {
      return "Focus on protein at each meal, plenty of fruits/veggies, and consistent hydration. Track 1–2 habits, not everything.";
    }
    return `You said: "${text}". How often do you train per week?`;
  }
}

export const chatService: ChatService = new MockChatService();
