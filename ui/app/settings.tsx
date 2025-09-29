import React from "react";
import { View, Text, ScrollView, ActivityIndicator } from "react-native";
import { useSettings } from "@/hooks/useSettings";
import ApiKeysSection from "@/components/settings/ApiKeysSection";
import AboutSection from "@/components/settings/AboutSection";

const SettingsScreen = () => {
  const { isLoading, error } = useSettings();

  if (isLoading) {
    return (
      <View className="flex-1 bg-black justify-center items-center">
        <ActivityIndicator size="large" color="#a99be4" />
        <Text className="text-white mt-4">Loading settings...</Text>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-black">
      <ScrollView className="flex-1 px-4 py-6">
        {error && (
          <View className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-6">
            <Text className="text-red-400">{error}</Text>
          </View>
        )}

        <View className="space-y-8">
          <ApiKeysSection />
          <AboutSection />
        </View>
      </ScrollView>
    </View>
  );
};

export default SettingsScreen;
