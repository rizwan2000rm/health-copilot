import React, { useState } from "react";
import { View, Text, Pressable, ScrollView, TextInput } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Toggle } from "./ui/toggle";
import clsx from "clsx";

interface CustomDrawerProps {
  navigation: any;
}

const CustomDrawer = ({ navigation }: CustomDrawerProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const insets = useSafeAreaInsets();

  const navigationItems = [
    {
      id: "health-coach",
      title: "Health Coach",
      icon: "chatbubble-outline",
      isActive: true,
    },
    {
      id: "settings",
      title: "Settings",
      icon: "settings-outline",
      isActive: false,
    },
  ];

  const recentChats = [
    "International driving license, International driving license",
    "Akbar travel flight discounts",
    "Makkah hotel recommendation",
    "Room upgrade explanation",
    "Grain calorie comparison",
    "Maximizing Amex points value",
  ];

  return (
    <View className="flex-1 bg-black px-4" style={{ paddingTop: insets.top }}>
      {/* Header with Search - Using InputBar styling */}
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
              onSubmitEditing={() => {
                // Handle search
                navigation.closeDrawer();
              }}
            />
          </View>
        </View>
      </View>

      {/* Recent Chats */}
      <ScrollView className="flex-1 mt-1">
        <View className="py-1">
          {recentChats.map((chat, index) => (
            <Pressable
              key={index}
              className="p-2"
              onPress={() => {
                // Handle chat selection
                navigation.closeDrawer();
              }}
            >
              <Text className="text-gray-300 text-lg line-clamp-1">{chat}</Text>
            </Pressable>
          ))}
        </View>
      </ScrollView>

      {/* Footer */}
      <View
        className="py-3 border-t border-gray-800"
        style={{ paddingBottom: insets.bottom + 12 }}
      >
        <View className="flex flex-row justify-center gap-2 items-center py-2 rounded-full">
          <Ionicons name="barbell-outline" size={18} color="#a99be4" />

          <Text className="text-[#a99be4] uppercase font-semibold">
            Health Coach
          </Text>
        </View>
      </View>
    </View>
  );
};

export default CustomDrawer;
