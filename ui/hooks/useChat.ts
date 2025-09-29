import { useCallback, useMemo, useRef, useState, useEffect } from "react";
import * as Haptics from "expo-haptics";
import { ScrollView } from "react-native";
import type { ChatMessage as OriginalChatMessage } from "@/types/chat";
import type { ChatSession, ChatMessage } from "@/types/chatHistory";
import { chatService } from "@/services/chatService";
import { chatStorage } from "@/storage/ChatStorage";
import { searchIndexManager } from "@/storage/SearchIndex";
import { ChatTitleGenerator } from "@/components/chat/ChatTitleGenerator";

export function useChat(initialChatId?: string, onChatSaved?: () => void) {
  const [currentChatId, setCurrentChatId] = useState<string | null>(
    initialChatId || null
  );
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: "welcome",
      role: "assistant",
      text: "Hi! I'm your AI fitness coach. Ask me anything to get started.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const scrollRef = useRef<ScrollView>(null);
  const autoSaveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync currentChatId with initialChatId changes
  useEffect(() => {
    setCurrentChatId(initialChatId || null);

    // Reset to welcome message when starting a new chat
    if (!initialChatId) {
      createNewChat();
    }
  }, [initialChatId]);

  // Initialize storage and load chat if ID provided
  useEffect(() => {
    const initializeChat = async () => {
      try {
        await chatStorage.initialize();
        await searchIndexManager.initialize();

        if (initialChatId) {
          await loadChat(initialChatId);
        } else {
          // Check if there's a current chat ID stored
          const storedChatId = await chatStorage.getCurrentChatId();
          if (storedChatId) {
            await loadChat(storedChatId);
          }
        }
      } catch (error) {
        console.error("Failed to initialize chat:", error);
      }
    };

    initializeChat();
  }, [initialChatId]);

  // Auto-save functionality
  useEffect(() => {
    if (hasUnsavedChanges && messages.length > 1) {
      // Clear existing timeout
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }

      // Set new timeout for auto-save
      autoSaveTimeoutRef.current = setTimeout(() => {
        saveCurrentChat();
      }, 2000); // Auto-save after 2 seconds of inactivity
    }

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [hasUnsavedChanges, messages]);

  const loadChat = useCallback(async (chatId: string) => {
    try {
      setIsLoading(true);
      const chat = await chatStorage.getChat(chatId);

      if (chat) {
        setCurrentChatId(chatId);
        setMessages(chat.messages);
        setHasUnsavedChanges(false);
        await chatStorage.setCurrentChatId(chatId);
      }
    } catch (error) {
      console.error("Failed to load chat:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const saveCurrentChat = useCallback(async () => {
    if (messages.length <= 1) return; // Don't save welcome message only

    try {
      const title = ChatTitleGenerator.generateTitle(messages);

      const chat: ChatSession = {
        id: currentChatId || chatStorage.createNewChat().id,
        title,
        createdAt: new Date(),
        updatedAt: new Date(),
        messages,
        metadata: {
          messageCount: messages.length,
          lastMessagePreview:
            messages[messages.length - 1]?.text.substring(0, 100) || "",
          tags: [],
        },
      };

      await chatStorage.saveChat(chat);

      if (!currentChatId) {
        setCurrentChatId(chat.id);
        await chatStorage.setCurrentChatId(chat.id);
      }

      setHasUnsavedChanges(false);

      // Notify parent component that chat was saved
      if (onChatSaved) {
        onChatSaved();
      }
    } catch (error) {
      console.error("Failed to save chat:", error);
    }
  }, [currentChatId, messages, onChatSaved]);

  const createNewChat = useCallback(async () => {
    try {
      // Save current chat if it has messages
      if (messages.length > 1) {
        await saveCurrentChat();
      }

      // Create new chat
      const newChat = chatStorage.createNewChat();
      setCurrentChatId(newChat.id);
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          text: "Hi! I'm your AI fitness coach. Ask me anything to get started.",
          timestamp: new Date(),
        },
      ]);
      setInput("");
      setHasUnsavedChanges(false);
      await chatStorage.setCurrentChatId(newChat.id);
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  }, [messages, saveCurrentChat]);

  const deleteCurrentChat = useCallback(async () => {
    if (!currentChatId) return;

    try {
      await chatStorage.deleteChat(currentChatId);

      // Create new chat
      await createNewChat();
    } catch (error) {
      console.error("Failed to delete chat:", error);
    }
  }, [currentChatId, createNewChat]);

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollToEnd({ animated: true });
    });
  }, []);

  const canSend = useMemo(
    () => input.trim().length > 0 && !isTyping && !isLoading,
    [input, isTyping, isLoading]
  );

  const hasUserMessages = useMemo(
    () => messages.some((message) => message.role === "user"),
    [messages]
  );

  const handleSend = useCallback(
    async (messageText?: string) => {
      const text = messageText || input.trim();
      if (!text || isTyping) return;

      setInput("");
      await Haptics.selectionAsync();

      const userMessage: ChatMessage = {
        id: `${Date.now()}-user`,
        role: "user",
        text,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setHasUnsavedChanges(true);
      setIsTyping(true);

      try {
        const aiText = await chatService.reply(text);
        const aiMessage: ChatMessage = {
          id: `${Date.now()}-ai`,
          role: "assistant",
          text: aiText,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);
        setHasUnsavedChanges(true);
      } catch (e) {
        const aiMessage: ChatMessage = {
          id: `${Date.now()}-aierr`,
          role: "assistant",
          text: "Sorry, I ran into a problem. Please try again.",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);
        setHasUnsavedChanges(true);
      } finally {
        setIsTyping(false);
      }
    },
    [input, isTyping]
  );

  // Manual save function
  const saveChat = useCallback(async () => {
    await saveCurrentChat();
  }, [saveCurrentChat]);

  return {
    // Existing properties
    messages,
    input,
    setInput,
    isTyping,
    canSend,
    handleSend,
    scrollRef,
    scrollToBottom,

    // New properties
    currentChatId,
    isLoading,
    hasUnsavedChanges,
    hasUserMessages,

    // New functions
    loadChat,
    createNewChat,
    deleteCurrentChat,
    saveChat,
  };
}
