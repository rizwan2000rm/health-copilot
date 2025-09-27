import React from "react";
import { View, Text, Pressable, Linking } from "react-native";
import { Ionicons } from "@expo/vector-icons";

const AboutSection: React.FC = () => {
  const handleOpenLink = (url: string) => {
    Linking.openURL(url);
  };

  return (
    <View>
      <Text className="text-gray-400 text-sm mb-4">About</Text>

      <View className="bg-gray-900 rounded-lg p-4 space-y-4">
        <View className="flex flex-row items-center gap-3 mb-4">
          <Ionicons name="barbell-outline" size={24} color="#a99be4" />
          <View>
            <Text className="text-white font-semibold text-lg">
              Health Coach
            </Text>
          </View>
        </View>

        <Text className="text-gray-400 text-sm leading-5">
          Your AI-powered health coach that helps you live a healthly lifestyle
        </Text>
      </View>
    </View>
  );
};

export default AboutSection;
