import Fuse from "fuse.js";
import { ChatSession } from "@/types/chatHistory";
import { chatStorage } from "./ChatStorage";
import { configManager } from "./ConfigManager";

export class SearchIndexManager {
  private static instance: SearchIndexManager;
  private fuse: Fuse<ChatSession> | null = null;
  private chats: ChatSession[] = [];
  private initialized = false;

  private constructor() {}

  public static getInstance(): SearchIndexManager {
    if (!SearchIndexManager.instance) {
      SearchIndexManager.instance = new SearchIndexManager();
    }
    return SearchIndexManager.instance;
  }

  public async initialize(): Promise<void> {
    if (this.initialized) return;

    await configManager.initialize();
    await this.rebuildIndex();
    this.initialized = true;
  }

  private async rebuildIndex(): Promise<void> {
    try {
      this.chats = await chatStorage.getChats(configManager.maxChatHistory);

      if (configManager.enableSearchIndexing) {
        this.fuse = new Fuse(this.chats, {
          keys: [
            { name: "title", weight: 0.4 },
            { name: "messages.text", weight: 0.3 },
            { name: "metadata.lastMessagePreview", weight: 0.3 },
          ],
          threshold: 0.4,
          includeScore: true,
        });
      }
    } catch (error) {
      console.error("Failed to rebuild search index:", error);
    }
  }

  public async search(query: string): Promise<ChatSession[]> {
    try {
      await this.initialize();

      if (!query.trim() || !this.fuse) {
        return [];
      }

      const results = this.fuse.search(query);
      return results.map((result) => result.item);
    } catch (error) {
      console.error("Search failed:", error);
      return [];
    }
  }

  public async refreshIndex(): Promise<void> {
    await this.rebuildIndex();
  }

  public getIndexSize(): number {
    return this.chats.length;
  }

  public isInitialized(): boolean {
    return this.initialized;
  }
}

export const searchIndexManager = SearchIndexManager.getInstance();
