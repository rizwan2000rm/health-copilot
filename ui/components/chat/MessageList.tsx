import React from "react";
import { View } from "react-native";
import type { ChatMessage } from "@/types/chat";
import MessageBubble from "@/components/chat/MessageBubble";
import TypingIndicator from "@/components/chat/TypingIndicator";

type Props = {
  messages: ChatMessage[];
  isTyping: boolean;
};

const MessageList = ({ messages, isTyping }: Props) => {
  return (
    <View className="w-full">
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
      {isTyping && <TypingIndicator />}
    </View>
  );
};

export default React.memo(MessageList);
