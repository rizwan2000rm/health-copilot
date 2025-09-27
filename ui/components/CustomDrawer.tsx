import React from "react";
import { View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import SearchHeader from "./drawer/SearchHeader";
import RecentChats from "./drawer/RecentChats";
import DrawerFooter from "./drawer/DrawerFooter";

interface CustomDrawerProps {
  navigation: any;
}

const CustomDrawer = ({ navigation }: CustomDrawerProps) => {
  const insets = useSafeAreaInsets();

  const recentChats = [
    "International driving license, International driving license",
    "Akbar travel flight discounts",
    "Makkah hotel recommendation",
    "Room upgrade explanation",
    "Grain calorie comparison",
    "Maximizing Amex points value",
  ];

  const handleSearch = (query: string) => {
    // Handle search functionality
    console.log("Search query:", query);
  };

  const handleChatSelect = (chat: string) => {
    // Handle chat selection
    console.log("Selected chat:", chat);
  };

  return (
    <View className="flex-1 bg-black px-4" style={{ paddingTop: insets.top }}>
      <SearchHeader
        onSearch={handleSearch}
        onCloseDrawer={() => navigation.closeDrawer()}
      />

      <RecentChats
        chats={recentChats}
        onChatSelect={handleChatSelect}
        onCloseDrawer={() => navigation.closeDrawer()}
      />

      <DrawerFooter />
    </View>
  );
};

export default CustomDrawer;
