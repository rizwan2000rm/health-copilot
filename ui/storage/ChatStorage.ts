import AsyncStorage from "@react-native-async-storage/async-storage";
import { v4 as uuidv4 } from "uuid";
import {
  ChatSession,
  ChatMessage,
  ChatStorage as IChatStorage,
  StorageError,
} from "@/types/chatHistory";
import { configManager } from "./ConfigManager";

const CHATS_KEY = "chat_sessions";
const CHAT_INDEX_KEY = "chat_index";
const CURRENT_CHAT_KEY = "current_chat_id";

// Using AsyncStorage for cross-platform compatibility with Expo Go

export class ChatStorage implements IChatStorage {
  private static instance: ChatStorage;
  private initialized = false;

  private constructor() {}

  public static getInstance(): ChatStorage {
    if (!ChatStorage.instance) {
      ChatStorage.instance = new ChatStorage();
    }
    return ChatStorage.instance;
  }

  public async initialize(): Promise<void> {
    if (this.initialized) return;
    await configManager.initialize();
    this.initialized = true;
  }

  private async getStorage(): Promise<typeof AsyncStorage> {
    // Use AsyncStorage for cross-platform compatibility with Expo Go
    return AsyncStorage;
  }

  private async saveToStorage(key: string, data: string): Promise<void> {
    try {
      const storage = await this.getStorage();
      await storage.setItem(key, data);
    } catch (error) {
      console.error("Storage save error:", error);
      throw this.createStorageError("Failed to save data", "STORAGE_FULL");
    }
  }

  private async loadFromStorage(key: string): Promise<string | null> {
    try {
      const storage = await this.getStorage();
      const data = await storage.getItem(key);

      if (!data) return null;
      return data;
    } catch (error) {
      console.error("Storage load error:", error);
      throw this.createStorageError("Failed to load data", "CORRUPTED_DATA");
    }
  }

  private createStorageError(
    message: string,
    code: StorageError["code"]
  ): StorageError {
    return {
      code,
      message,
      recoverable: code !== "CORRUPTED_DATA",
    };
  }

  private generateChatId(): string {
    return uuidv4();
  }

  private generateMessageId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private createChatSession(
    title: string,
    messages: ChatMessage[] = []
  ): ChatSession {
    const now = new Date();
    const lastMessage = messages[messages.length - 1];

    return {
      id: this.generateChatId(),
      title,
      createdAt: now,
      updatedAt: now,
      messages,
      metadata: {
        messageCount: messages.length,
        lastMessagePreview: lastMessage?.text.substring(0, 100) || "",
        tags: [],
      },
    };
  }

  public async saveChat(chat: ChatSession): Promise<void> {
    try {
      await this.initialize();

      // Update metadata
      const updatedChat: ChatSession = {
        ...chat,
        updatedAt: new Date(),
        metadata: {
          ...chat.metadata,
          messageCount: chat.messages.length,
          lastMessagePreview:
            chat.messages[chat.messages.length - 1]?.text.substring(0, 100) ||
            "",
        },
      };

      // Save individual chat
      await this.saveToStorage(
        `${CHATS_KEY}_${chat.id}`,
        JSON.stringify(updatedChat)
      );

      // Update chat index
      const index = await this.getChatIndex();
      if (!index.includes(chat.id)) {
        index.unshift(chat.id); // Add to beginning for most recent first
      } else {
        // Move to beginning if it exists
        const existingIndex = index.indexOf(chat.id);
        if (existingIndex > 0) {
          index.splice(existingIndex, 1);
          index.unshift(chat.id);
        }
      }

      // Limit the number of chats
      const maxChats = configManager.maxChatHistory;
      if (index.length > maxChats) {
        // Remove oldest chats
        const chatsToRemove = index.splice(maxChats);
        for (const chatId of chatsToRemove) {
          await this.deleteChat(chatId);
        }
      }

      await this.saveToStorage(CHAT_INDEX_KEY, JSON.stringify(index));
    } catch (error) {
      console.error("Failed to save chat:", error);
      throw error;
    }
  }

  public async getChats(limit?: number): Promise<ChatSession[]> {
    try {
      await this.initialize();

      const index = await this.getChatIndex();
      const limitToUse = limit || configManager.maxChatsInDrawer;
      const chatIds = index.slice(0, limitToUse);

      const chats: ChatSession[] = [];
      for (const chatId of chatIds) {
        const chat = await this.getChat(chatId);
        if (chat) {
          chats.push(chat);
        }
      }

      return chats;
    } catch (error) {
      console.error("Failed to get chats:", error);
      throw error;
    }
  }

  public async getChat(id: string): Promise<ChatSession | null> {
    try {
      await this.initialize();

      const data = await this.loadFromStorage(`${CHATS_KEY}_${id}`);
      if (!data) return null;

      const chat = JSON.parse(data) as ChatSession;

      // Convert date strings back to Date objects
      chat.createdAt = new Date(chat.createdAt);
      chat.updatedAt = new Date(chat.updatedAt);
      chat.messages = chat.messages.map((msg) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));

      return chat;
    } catch (error) {
      console.error("Failed to get chat:", error);

      // If the chat data is corrupted, remove it from storage and index
      try {
        await this.deleteChat(id);
        console.log(`Removed corrupted chat: ${id}`);
      } catch (deleteError) {
        console.error(`Failed to remove corrupted chat ${id}:`, deleteError);
      }

      return null;
    }
  }

  public async deleteChat(id: string): Promise<void> {
    try {
      await this.initialize();

      // Remove from storage
      const storage = await this.getStorage();
      await storage.removeItem(`${CHATS_KEY}_${id}`);

      // Remove from index
      const index = await this.getChatIndex();
      const updatedIndex = index.filter((chatId) => chatId !== id);
      await this.saveToStorage(CHAT_INDEX_KEY, JSON.stringify(updatedIndex));
    } catch (error) {
      console.error("Failed to delete chat:", error);
      throw error;
    }
  }

  public async searchChats(query: string): Promise<ChatSession[]> {
    try {
      await this.initialize();

      if (!query.trim()) return [];

      const allChats = await this.getChats(configManager.maxChatHistory);
      const searchTerm = query.toLowerCase();

      return allChats.filter((chat) => {
        // Search in title
        if (chat.title.toLowerCase().includes(searchTerm)) return true;

        // Search in messages
        return chat.messages.some((message) =>
          message.text.toLowerCase().includes(searchTerm)
        );
      });
    } catch (error) {
      console.error("Failed to search chats:", error);
      return [];
    }
  }

  public async clearAllChats(): Promise<void> {
    try {
      await this.initialize();

      const index = await this.getChatIndex();

      // Delete all individual chats
      for (const chatId of index) {
        const storage = await this.getStorage();
        await storage.removeItem(`${CHATS_KEY}_${chatId}`);
      }

      // Clear index
      await this.saveToStorage(CHAT_INDEX_KEY, JSON.stringify([]));
    } catch (error) {
      console.error("Failed to clear all chats:", error);
      throw error;
    }
  }

  private async getChatIndex(): Promise<string[]> {
    try {
      const data = await this.loadFromStorage(CHAT_INDEX_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error("Failed to get chat index:", error);

      // If the chat index is corrupted, clear it and start fresh
      try {
        const storage = await this.getStorage();
        await storage.removeItem(CHAT_INDEX_KEY);
        console.log("Cleared corrupted chat index");
      } catch (clearError) {
        console.error("Failed to clear corrupted chat index:", clearError);
      }

      return [];
    }
  }

  public async getCurrentChatId(): Promise<string | null> {
    try {
      await this.initialize();
      return await this.loadFromStorage(CURRENT_CHAT_KEY);
    } catch (error) {
      console.error("Failed to get current chat ID:", error);
      return null;
    }
  }

  public async setCurrentChatId(id: string | null): Promise<void> {
    try {
      await this.initialize();
      if (id) {
        await this.saveToStorage(CURRENT_CHAT_KEY, id);
      } else {
        const storage = await this.getStorage();
        await storage.removeItem(CURRENT_CHAT_KEY);
      }
    } catch (error) {
      console.error("Failed to set current chat ID:", error);
      throw error;
    }
  }

  public createNewChat(title: string = "New Chat"): ChatSession {
    return this.createChatSession(title);
  }

  public createMessage(role: "user" | "assistant", text: string): ChatMessage {
    return {
      id: this.generateMessageId(),
      role,
      text,
      timestamp: new Date(),
    };
  }
}

export const chatStorage = ChatStorage.getInstance();
