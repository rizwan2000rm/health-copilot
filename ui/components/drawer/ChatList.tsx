import React from "react";
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { ChatSession } from "@/types/chatHistory";
import ChatItem from "./ChatItem";

interface ChatListProps {
  chats: ChatSession[];
  currentChatId?: string | null;
  isLoading?: boolean;
  onChatSelect: (chat: ChatSession) => void;
  onChatDelete?: (chatId: string) => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

const ChatList = ({
  chats,
  currentChatId,
  isLoading = false,
  onChatSelect,
  onChatDelete,
  onRefresh,
  isRefreshing = false,
}: ChatListProps) => {
  if (isLoading && chats.length === 0) {
    return (
      <View className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" color="#a99be4" />
        <Text className="text-gray-400 mt-4">Loading chats...</Text>
      </View>
    );
  }

  if (chats.length === 0) {
    return (
      <View className="flex-1 justify-center items-center px-8">
        <Ionicons name="chatbubbles-outline" size={64} color="#6b7280" />
        <Text className="text-gray-400 text-lg font-medium mt-4 text-center">
          No chats yet
        </Text>
        <Text className="text-gray-500 text-sm mt-2 text-center">
          Start a new conversation to see it here
        </Text>
      </View>
    );
  }

  return (
    <ScrollView
      className="flex-1"
      refreshControl={
        onRefresh ? (
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={onRefresh}
            tintColor="#a99be4"
            colors={["#a99be4"]}
          />
        ) : undefined
      }
      showsVerticalScrollIndicator={false}
    >
      <View className="py-2">
        {chats.map((chat) => (
          <ChatItem
            key={chat.id}
            chat={chat}
            isActive={chat.id === currentChatId}
            onPress={onChatSelect}
            onDelete={onChatDelete}
          />
        ))}
      </View>
    </ScrollView>
  );
};

export default ChatList;
