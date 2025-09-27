import React from "react";
import { View, Text, Pressable } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";

const DrawerFooter = ({ navigation }: { navigation: any }) => {
  const insets = useSafeAreaInsets();

  const handleSettingsPress = () => {
    navigation.navigate("Settings");
    navigation.closeDrawer();
  };

  return (
    <>
      <View
        className="py-3 border-t border-gray-800"
        style={{ paddingBottom: insets.bottom + 12 }}
      >
        <Pressable
          onPress={handleSettingsPress}
          className="flex flex-row items-center gap-3 p-2"
        >
          <Ionicons name="settings-outline" size={20} color="#eaeaea" />
          <Text className="text-[#eaeaea] uppercase font-medium">Settings</Text>
        </Pressable>

        <View className="flex flex-row items-center gap-3 p-2">
          <Ionicons name="barbell-outline" size={20} color="#eaeaea" />
          <Text className="text-[#eaeaea] uppercase font-semibold">
            Health Coach
          </Text>
        </View>
      </View>
    </>
  );
};

export default DrawerFooter;
