import { useCallback, useMemo, useRef, useState } from "react";
import * as Haptics from "expo-haptics";
import { ScrollView } from "react-native";
import type { ChatMessage } from "@/types/chat";
import { chatService } from "@/services/chatService";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: "welcome",
      role: "assistant",
      text: "Hi! I'm your AI fitness coach. Ask me anything to get started.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<ScrollView>(null);

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollToEnd({ animated: true });
    });
  }, []);

  const canSend = useMemo(
    () => input.trim().length > 0 && !isTyping,
    [input, isTyping]
  );

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isTyping) return;
    setInput("");
    await Haptics.selectionAsync();
    const userMessage: ChatMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      text,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    try {
      const aiText = await chatService.reply(text);
      const aiMessage: ChatMessage = {
        id: `${Date.now()}-ai`,
        role: "assistant",
        text: aiText,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (e) {
      const aiMessage: ChatMessage = {
        id: `${Date.now()}-aierr`,
        role: "assistant",
        text: "Sorry, I ran into a problem. Please try again.",
      };
      setMessages((prev) => [...prev, aiMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [input, isTyping]);

  return {
    messages,
    input,
    setInput,
    isTyping,
    canSend,
    handleSend,
    scrollRef,
    scrollToBottom,
  };
}
