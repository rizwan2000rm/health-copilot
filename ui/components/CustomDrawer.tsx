import React, { useState } from "react";
import { View, Alert } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ChatSession } from "@/types/chatHistory";
import { useChatHistory } from "@/hooks/useChatHistory";
import { configManager } from "@/storage/ConfigManager";
import SearchHeader from "./drawer/SearchHeader";
import ChatList from "./drawer/ChatList";
import SearchResults from "./drawer/SearchResults";
import DrawerFooter from "./drawer/DrawerFooter";

interface CustomDrawerProps {
  navigation: any;
  currentChatId?: string | null;
  onChatSelect?: (chat: ChatSession) => void;
}

const CustomDrawer = ({
  navigation,
  currentChatId,
  onChatSelect,
}: CustomDrawerProps) => {
  const insets = useSafeAreaInsets();
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  const { chats, isLoading, error, searchChats, deleteChat, refreshChats } =
    useChatHistory();

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      setIsSearching(true);
      await searchChats(query);
      setIsSearching(false);
    }
  };

  const handleChatSelect = (chat: ChatSession) => {
    if (onChatSelect) {
      onChatSelect(chat);
    }
    navigation.navigate("Home");
    navigation.closeDrawer();
  };

  const handleChatDelete = (chatId: string) => {
    Alert.alert(
      "Delete Chat",
      "Are you sure you want to delete this chat? This action cannot be undone.",
      [
        {
          text: "Cancel",
          style: "cancel",
        },
        {
          text: "Delete",
          style: "destructive",
          onPress: () => deleteChat(chatId),
        },
      ]
    );
  };

  const handleRefresh = async () => {
    await refreshChats();
  };

  const clearSearch = () => {
    setSearchQuery("");
    setIsSearching(false);
  };

  return (
    <View className="flex-1 bg-black px-4" style={{ paddingTop: insets.top }}>
      <SearchHeader
        onSearch={handleSearch}
        onCloseDrawer={() => navigation.closeDrawer()}
        debounceMs={configManager.searchDebounceMs}
      />

      {searchQuery.trim() ? (
        <SearchResults
          query={searchQuery}
          results={chats}
          currentChatId={currentChatId}
          isLoading={isSearching}
          onChatSelect={handleChatSelect}
          onChatDelete={handleChatDelete}
          onClearSearch={clearSearch}
        />
      ) : (
        <ChatList
          chats={chats}
          currentChatId={currentChatId}
          isLoading={isLoading}
          onChatSelect={handleChatSelect}
          onChatDelete={handleChatDelete}
          onRefresh={handleRefresh}
          isRefreshing={isLoading}
        />
      )}

      <DrawerFooter navigation={navigation} />
    </View>
  );
};

export default CustomDrawer;
