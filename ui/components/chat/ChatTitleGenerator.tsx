import { ChatMessage } from "@/types/chatHistory";

export class ChatTitleGenerator {
  private static readonly MAX_TITLE_LENGTH = 50;
  private static readonly MIN_TITLE_LENGTH = 10;

  public static generateTitle(messages: ChatMessage[]): string {
    // Find the first user message
    const firstUserMessage = messages.find((msg) => msg.role === "user");

    if (!firstUserMessage) {
      return "New Chat";
    }

    let title = firstUserMessage.text.trim();

    // Clean up the title
    title = this.cleanTitle(title);

    // Truncate if too long
    if (title.length > this.MAX_TITLE_LENGTH) {
      title = title.substring(0, this.MAX_TITLE_LENGTH).trim();
      // Try to end at a word boundary
      const lastSpace = title.lastIndexOf(" ");
      if (lastSpace > this.MIN_TITLE_LENGTH) {
        title = title.substring(0, lastSpace);
      }
      title += "...";
    }

    // Ensure minimum length
    if (title.length < this.MIN_TITLE_LENGTH) {
      title = this.generateFallbackTitle(messages);
    }

    return title || "New Chat";
  }

  private static cleanTitle(title: string): string {
    // Remove common prefixes
    const prefixes = [
      "can you",
      "could you",
      "please",
      "help me",
      "i need",
      "i want",
      "how do i",
      "what is",
      "what are",
      "where is",
      "when is",
      "why is",
      "tell me",
      "explain",
      "show me",
      "give me",
    ];

    let cleaned = title.toLowerCase();

    for (const prefix of prefixes) {
      if (cleaned.startsWith(prefix + " ")) {
        cleaned = cleaned.substring(prefix.length + 1);
        break;
      }
    }

    // Capitalize first letter
    cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);

    // Remove trailing punctuation
    cleaned = cleaned.replace(/[.!?]+$/, "");

    return cleaned;
  }

  private static generateFallbackTitle(messages: ChatMessage[]): string {
    const messageCount = messages.length;
    const now = new Date();

    // Generate time-based title
    const timeStr = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    if (messageCount <= 1) {
      return `Chat at ${timeStr}`;
    } else if (messageCount <= 5) {
      return `Quick Chat (${messageCount} messages)`;
    } else {
      return `Chat Session (${messageCount} messages)`;
    }
  }

  public static generateTitleFromQuery(query: string): string {
    if (!query || query.trim().length === 0) {
      return "New Chat";
    }

    return this.generateTitle([
      {
        id: "temp",
        role: "user",
        text: query,
        timestamp: new Date(),
      },
    ]);
  }
}
