import React from "react";
import { KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import MessageList from "@/components/chat/MessageList";
import InputBar from "@/components/chat/InputBar";
import { useChat } from "@/hooks/useChat";

const Chat = () => {
  const {
    messages,
    input,
    setInput,
    isTyping,
    canSend,
    handleSend,
    scrollRef,
    scrollToBottom,
  } = useChat();

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      className="flex-1"
      keyboardVerticalOffset={Platform.OS === "ios" ? 80 : 20}
      style={{ backgroundColor: "black" }}
    >
      <ScrollView
        ref={scrollRef}
        className="flex-1"
        contentContainerStyle={{
          flexGrow: 1,
          justifyContent: "flex-end",
          paddingTop: 16,
        }}
        keyboardShouldPersistTaps="handled"
        onContentSizeChange={scrollToBottom}
      >
        <MessageList messages={messages} isTyping={isTyping} />
      </ScrollView>
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
