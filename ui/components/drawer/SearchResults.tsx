import React from "react";
import { View, Text } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { ChatSession } from "@/types/chatHistory";
import ChatList from "./ChatList";

interface SearchResultsProps {
  query: string;
  results: ChatSession[];
  currentChatId?: string | null;
  isLoading?: boolean;
  onChatSelect: (chat: ChatSession) => void;
  onChatDelete?: (chatId: string) => void;
  onClearSearch?: () => void;
}

const SearchResults = ({
  query,
  results,
  currentChatId,
  isLoading = false,
  onChatSelect,
  onChatDelete,
  onClearSearch,
}: SearchResultsProps) => {
  if (!query.trim()) {
    return null;
  }

  if (isLoading) {
    return (
      <View className="flex-1 justify-center items-center">
        <Ionicons name="search" size={32} color="#6b7280" />
        <Text className="text-gray-400 mt-2">Searching...</Text>
      </View>
    );
  }

  if (results.length === 0) {
    return (
      <View className="flex-1 justify-center items-center px-8">
        <Ionicons name="search-outline" size={48} color="#6b7280" />
        <Text className="text-gray-400 text-lg font-medium mt-4 text-center">
          No results found
        </Text>
        <Text className="text-gray-500 text-sm mt-2 text-center">
          Try searching with different keywords
        </Text>
        {onClearSearch && (
          <Text
            className="text-[#a99be4] text-sm mt-4 underline"
            onPress={onClearSearch}
          >
            Clear search
          </Text>
        )}
      </View>
    );
  }

  return (
    <View className="flex-1">
      <View className="px-4 py-2 border-b border-gray-800">
        <Text className="text-gray-400 text-sm">
          {results.length} result{results.length !== 1 ? "s" : ""} for "{query}"
        </Text>
      </View>

      <ChatList
        chats={results}
        currentChatId={currentChatId}
        onChatSelect={onChatSelect}
        onChatDelete={onChatDelete}
      />
    </View>
  );
};

export default SearchResults;
