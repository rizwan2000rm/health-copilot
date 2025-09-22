export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
};

export interface ChatService {
  reply(prompt: string): Promise<string>;
}
