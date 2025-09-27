import React, { useState } from "react";
import { View, TextInput } from "react-native";
import { Ionicons } from "@expo/vector-icons";

interface SearchHeaderProps {
  onSearch?: (query: string) => void;
  onCloseDrawer?: () => void;
}

const SearchHeader = ({ onSearch, onCloseDrawer }: SearchHeaderProps) => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSubmit = () => {
    if (onSearch) {
      onSearch(searchQuery);
    }
    if (onCloseDrawer) {
      onCloseDrawer();
    }
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
            placeholder="Search"
            placeholderTextColor="#9c9a92"
            value={searchQuery}
            onChangeText={setSearchQuery}
            className="flex-1 mx-3 text-base leading-5 text-[#f8f7f3]"
            returnKeyType="search"
            onSubmitEditing={handleSubmit}
          />
        </View>
      </View>
    </View>
  );
};

export default SearchHeader;
