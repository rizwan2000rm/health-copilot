import React, { useState, useEffect, useRef } from "react";
import { View, TextInput } from "react-native";
import { Ionicons } from "@expo/vector-icons";

interface SearchHeaderProps {
  onSearch?: (query: string) => void;
  onCloseDrawer?: () => void;
  debounceMs?: number;
}

const SearchHeader = ({
  onSearch,
  onCloseDrawer,
  debounceMs = 300,
}: SearchHeaderProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const debounceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Set new timeout for debounced search
    if (searchQuery.trim()) {
      debounceTimeoutRef.current = setTimeout(() => {
        if (onSearch) {
          onSearch(searchQuery);
        }
      }, debounceMs);
    } else if (onSearch) {
      // Clear search immediately when query is empty
      onSearch("");
    }

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [searchQuery, onSearch, debounceMs]);

  const handleSubmit = () => {
    if (onSearch) {
      onSearch(searchQuery);
    }
    if (onCloseDrawer) {
      onCloseDrawer();
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
  };

  return (
    <View className="pb-4">
      <View className="flex-row items-center gap-2">
        <View className="flex-1 min-h-12 py-2 pr-2 bg-[#1f1f1f] rounded-3xl border border-[#2a2a2a] flex-row justify-center items-center">
          <Ionicons
            name="search"
            size={16}
            color="#9c9a92"
            style={{ marginLeft: 12 }}
          />
          <TextInput
            placeholder="Search chats..."
            placeholderTextColor="#9c9a92"
            value={searchQuery}
            onChangeText={setSearchQuery}
            className="flex-1 mx-3 text-base leading-5 text-[#f8f7f3]"
            returnKeyType="search"
            onSubmitEditing={handleSubmit}
            autoCorrect={false}
            autoCapitalize="none"
          />
          {searchQuery.length > 0 && (
            <Ionicons
              name="close-circle"
              size={20}
              color="#9c9a92"
              style={{ marginRight: 12 }}
              onPress={clearSearch}
            />
          )}
        </View>
      </View>
    </View>
  );
};

export default SearchHeader;
