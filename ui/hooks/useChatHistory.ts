import { useState, useEffect, useCallback } from "react";
import { ChatSession } from "@/types/chatHistory";
import { chatStorage } from "@/storage/ChatStorage";
import { searchIndexManager } from "@/storage/SearchIndex";

export function useChatHistory() {
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadChats = useCallback(async (limit?: number) => {
    try {
      setIsLoading(true);
      setError(null);

      await chatStorage.initialize();
      const loadedChats = await chatStorage.getChats(limit);
      setChats(loadedChats);
    } catch (err) {
      console.error("Failed to load chats:", err);
      setError("Failed to load chat history");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const searchChats = useCallback(
    async (query: string) => {
      try {
        setIsLoading(true);
        setError(null);

        if (!query.trim()) {
          await loadChats();
          return;
        }

        await searchIndexManager.initialize();
        const searchResults = await searchIndexManager.search(query);
        setChats(searchResults);
      } catch (err) {
        console.error("Failed to search chats:", err);
        setError("Search failed");
      } finally {
        setIsLoading(false);
      }
    },
    [loadChats]
  );

  const deleteChat = useCallback(async (chatId: string) => {
    try {
      await chatStorage.deleteChat(chatId);

      // Remove from local state
      setChats((prev) => prev.filter((chat) => chat.id !== chatId));
    } catch (err) {
      console.error("Failed to delete chat:", err);
      setError("Failed to delete chat");
    }
  }, []);

  const refreshChats = useCallback(async () => {
    await loadChats();
  }, [loadChats]);

  const clearAllChats = useCallback(async () => {
    try {
      await chatStorage.clearAllChats();
      await searchIndexManager.refreshIndex();
      setChats([]);
    } catch (err) {
      console.error("Failed to clear all chats:", err);
      setError("Failed to clear all chats");
    }
  }, []);

  // Load chats on mount
  useEffect(() => {
    loadChats();
  }, [loadChats]);

  return {
    chats,
    isLoading,
    error,
    loadChats,
    searchChats,
    deleteChat,
    refreshChats,
    clearAllChats,
  };
}
