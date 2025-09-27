import React from "react";
import { View, Text } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";

const DrawerFooter = () => {
  const insets = useSafeAreaInsets();

  return (
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
  );
};

export default DrawerFooter;
