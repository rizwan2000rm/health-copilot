import "react-native-get-random-values";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { createDrawerNavigator } from "@react-navigation/drawer";
import { DrawerActions } from "@react-navigation/native";
import { Pressable, Text, View } from "react-native";
import { Ionicons, MaterialCommunityIcons } from "@expo/vector-icons";
import "react-native-reanimated";
import "../global.css";
import Index from "./index";
import SettingsScreen from "./settings";
import React, { useState } from "react";
import { PortalHost } from "@rn-primitives/portal";
import CustomDrawer from "@/components/CustomDrawer";
import { ChatSession } from "@/types/chatHistory";
const Drawer = createDrawerNavigator();

const RootLayout = () => {
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [drawerRefreshKey, setDrawerRefreshKey] = useState(0);

  const handleChatSelect = (chat: ChatSession) => {
    setCurrentChatId(chat.id);
  };

  const handleNewChat = () => {
    setCurrentChatId(null);
  };

  const handleChatSaved = () => {
    // Trigger drawer refresh by updating the key
    setDrawerRefreshKey((prev) => prev + 1);
  };

  return (
    <SafeAreaProvider>
      <Drawer.Navigator
        drawerContent={(props) => (
          <CustomDrawer
            {...props}
            key={drawerRefreshKey}
            currentChatId={currentChatId}
            onChatSelect={handleChatSelect}
          />
        )}
        screenOptions={({ navigation }) => ({
          headerShown: true,
          headerStyle: {
            backgroundColor: "#000000",
          },
          headerTintColor: "#ffffff",
          headerTitle: () => (
            <View className="px-4 flex flex-row gap-2 items-center py-2 rounded-full">
              <Ionicons name="barbell-outline" size={18} color="#a99be4" />

              <Text className="text-[#a99be4] uppercase font-semibold">
                Health Coach
              </Text>
            </View>
          ),
          headerLeft: () => (
            <Pressable
              accessibilityLabel="Open menu"
              onPress={() => navigation.dispatch(DrawerActions.toggleDrawer())}
              className="h-9 w-9 items-center justify-center ml-2"
            >
              <Ionicons name="menu" size={24} color="#eaeaea" />
            </Pressable>
          ),
          headerRight: () => (
            <Pressable
              onPress={() => {
                handleNewChat();
                navigation.navigate("Home");
              }}
              accessibilityLabel="New chat"
              className="h-9 w-9 items-center justify-center mr-2"
            >
              <MaterialCommunityIcons
                name="chat-plus"
                size={24}
                color="#eaeaea"
              />
            </Pressable>
          ),
        })}
      >
        <Drawer.Screen
          name="Home"
          options={{
            title: "",
          }}
        >
          {(props) => (
            <Index
              {...props}
              currentChatId={currentChatId}
              onChatSaved={handleChatSaved}
            />
          )}
        </Drawer.Screen>
        <Drawer.Screen
          name="Settings"
          component={SettingsScreen}
          options={{
            title: "Settings",
          }}
        />
      </Drawer.Navigator>
      <PortalHost />
    </SafeAreaProvider>
  );
};

export default RootLayout;
