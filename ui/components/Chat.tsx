import React from "react";
import { KeyboardAvoidingView, Platform, ScrollView, View } from "react-native";
import MessageList from "@/components/chat/MessageList";
import InputBar from "@/components/chat/InputBar";
import { useChat } from "@/hooks/useChat";
import SuggestionChips from "@/components/chat/SuggestionChips";

interface ChatProps {
  currentChatId?: string | null;
  onChatSaved?: () => void;
}

const Chat = ({ currentChatId, onChatSaved }: ChatProps) => {
  const {
    messages,
    input,
    setInput,
    isTyping,
    canSend,
    handleSend,
    scrollRef,
    scrollToBottom,
    hasUserMessages,
  } = useChat(currentChatId || undefined, onChatSaved);

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      className="flex-1"
      keyboardVerticalOffset={Platform.OS === "ios" ? 80 : 20}
      style={{ backgroundColor: "black" }}
    >
      <View className="flex-1">
        <ScrollView
          ref={scrollRef}
          className="flex-1"
          contentContainerStyle={{
            flexGrow: 1,
            justifyContent: "flex-end",
            paddingTop: 8,
          }}
          keyboardShouldPersistTaps="handled"
          onContentSizeChange={scrollToBottom}
        >
          <MessageList messages={messages} isTyping={isTyping} />
        </ScrollView>
        {!hasUserMessages && <SuggestionChips onSend={handleSend} />}
      </View>
      <InputBar
        value={input}
        onChange={setInput}
        canSend={canSend}
        onSend={handleSend}
      />
    </KeyboardAvoidingView>
  );
};

export default Chat;
