import React, { useState } from "react";
import { View, Text, Pressable, ScrollView, TextInput } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";

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
    "International driving licens...",
    "Akbar travel flight discounts",
    "Makkah hotel recommenda...",
    "Room upgrade explanation",
    "Grain calorie comparison",
    "Maximizing Amex points va...",
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

      {/* Navigation Items - Exact ChatGPT styling */}
      <View className="px-1 py-1">
        {navigationItems.map((item) => (
          <Pressable
            key={item.id}
            className={`flex-row items-center py-2 px-3 rounded-lg mb-1 ${
              item.isActive ? "bg-gray-800" : ""
            }`}
            onPress={() => {
              if (item.id === "chatgpt") {
                navigation.navigate("Home");
              }
              navigation.closeDrawer();
            }}
          >
            {item.id === "chatgpt" ? (
              <View className="w-5 h-5 bg-white rounded-sm items-center justify-center mr-3">
                <Text className="text-black font-bold text-xs">∞</Text>
              </View>
            ) : (
              <Ionicons
                name={item.icon as any}
                size={16}
                color={item.isActive ? "#fff" : "#666"}
                style={{ marginRight: 12 }}
              />
            )}
            <Text
              className={`text-sm ${
                item.isActive ? "text-white font-medium" : "text-gray-400"
              }`}
            >
              {item.title}
            </Text>
            {item.id === "gpts" && (
              <Ionicons
                name="chevron-forward"
                size={12}
                color="#666"
                style={{ marginLeft: "auto" }}
              />
            )}
          </Pressable>
        ))}
      </View>

      {/* Recent Chats - Exact ChatGPT styling */}
      <ScrollView className="flex-1 px-1 mt-1">
        <View className="py-1">
          {recentChats.map((chat, index) => (
            <Pressable
              key={index}
              className="py-2 px-3 rounded-lg"
              onPress={() => {
                // Handle chat selection
                navigation.closeDrawer();
              }}
            >
              <Text className="text-gray-300 text-sm">{chat}</Text>
            </Pressable>
          ))}
        </View>
      </ScrollView>

      {/* User Profile Section - Exact ChatGPT styling */}
      <View
        className="px-3 py-3 border-t border-gray-800"
        style={{ paddingBottom: insets.bottom + 12 }}
      >
        <Pressable className="flex-row items-center py-1">
          <View className="w-6 h-6 bg-red-500 rounded-full items-center justify-center mr-3">
            <Text className="text-white font-semibold text-xs">R</Text>
          </View>
          <Text className="text-white font-medium text-sm">Rizwan Memon</Text>
        </Pressable>
      </View>
    </View>
  );
};

export default CustomDrawer;
