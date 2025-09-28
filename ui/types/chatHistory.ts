export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: Date;
  metadata?: {
    tokens?: number;
    model?: string;
  };
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages: ChatMessage[];
  metadata: {
    messageCount: number;
    lastMessagePreview: string;
    tags?: string[];
  };
}

export interface ChatConfig {
  maxChatsInDrawer: number; // Default: 20
  maxChatHistory: number; // Default: 100
  searchDebounceMs: number; // Default: 300
  autoSaveIntervalMs: number; // Default: 5000
  enableSearchIndexing: boolean; // Default: true
}

export interface StorageError {
  code:
    | "STORAGE_FULL"
    | "PERMISSION_DENIED"
    | "CORRUPTED_DATA"
    | "NETWORK_ERROR";
  message: string;
  recoverable: boolean;
}

export interface ChatStorage {
  saveChat(chat: ChatSession): Promise<void>;
  getChats(limit?: number): Promise<ChatSession[]>;
  getChat(id: string): Promise<ChatSession | null>;
  deleteChat(id: string): Promise<void>;
  searchChats(query: string): Promise<ChatSession[]>;
  clearAllChats(): Promise<void>;
}

export const DEFAULT_CONFIG: ChatConfig = {
  maxChatsInDrawer: 20,
  maxChatHistory: 100,
  searchDebounceMs: 300,
  autoSaveIntervalMs: 5000,
  enableSearchIndexing: true,
};
