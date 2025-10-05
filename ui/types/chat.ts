export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
};

export type ChatHistoryTurn = {
  role: ChatRole;
  text: string;
};

export interface ChatService {
  reply(prompt: string, history?: ChatHistoryTurn[]): Promise<string>;
}
