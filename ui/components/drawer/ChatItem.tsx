import React from "react";
import { View, Text, Pressable } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { ChatSession } from "@/types/chatHistory";

interface ChatItemProps {
  chat: ChatSession;
  isActive?: boolean;
  onPress: (chat: ChatSession) => void;
  onDelete?: (chatId: string) => void;
}

const ChatItem = ({
  chat,
  isActive = false,
  onPress,
  onDelete,
}: ChatItemProps) => {
  const formatTime = (date: Date) => {
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return "Just now";
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 168) {
      // 7 days
      return `${Math.floor(diffInHours / 24)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const handlePress = () => {
    onPress(chat);
  };

  const handleDelete = (e: any) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(chat.id);
    }
  };

  return (
    <Pressable
      onPress={handlePress}
      className={`p-3 mx-2 mb-2 rounded-lg ${
        isActive ? "bg-[#2a2a2a]" : "bg-transparent"
      } active:bg-[#1a1a1a]`}
    >
      <View className="flex-row items-start justify-between">
        <View className="flex-1 mr-2">
          <Text
            className={`text-base font-medium ${
              isActive ? "text-white" : "text-gray-200"
            }`}
            numberOfLines={1}
          >
            {chat.title}
          </Text>

          <Text className="text-sm text-gray-400 mt-1" numberOfLines={2}>
            {chat.metadata.lastMessagePreview}
          </Text>

          <View className="flex-row items-center mt-2">
            <Text className="text-xs text-gray-500">
              {formatTime(chat.updatedAt)}
            </Text>
            <Text className="text-xs text-gray-500 mx-2">•</Text>
            <Text className="text-xs text-gray-500">
              {chat.metadata.messageCount} messages
            </Text>
          </View>
        </View>

        {onDelete && (
          <Pressable
            onPress={handleDelete}
            className="p-1 rounded-full active:bg-gray-700"
          >
            <Ionicons name="trash-outline" size={16} color="#6b7280" />
          </Pressable>
        )}
      </View>
    </Pressable>
  );
};

export default ChatItem;
