import React from "react";
import { View, Text, Pressable, ScrollView } from "react-native";

interface RecentChatsProps {
  chats: string[];
  onChatSelect?: (chat: string) => void;
  onCloseDrawer?: () => void;
}

const RecentChats = ({
  chats,
  onChatSelect,
  onCloseDrawer,
}: RecentChatsProps) => {
  const handleChatPress = (chat: string) => {
    if (onChatSelect) {
      onChatSelect(chat);
    }
    if (onCloseDrawer) {
      onCloseDrawer();
    }
  };

  return (
    <ScrollView className="flex-1 mt-1">
      <View className="py-1">
        {chats.map((chat, index) => (
          <Pressable
            key={index}
            className="p-2"
            onPress={() => handleChatPress(chat)}
          >
            <Text className="text-gray-300 text-lg line-clamp-1">{chat}</Text>
          </Pressable>
        ))}
      </View>
    </ScrollView>
  );
};

export default RecentChats;
