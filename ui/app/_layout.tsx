import { SafeAreaProvider } from "react-native-safe-area-context";
import { createDrawerNavigator } from "@react-navigation/drawer";
import { DrawerActions } from "@react-navigation/native";
import { Pressable, Text, View } from "react-native";
import { Ionicons, MaterialCommunityIcons } from "@expo/vector-icons";
import "react-native-reanimated";
import "../global.css";
import Index from "./index";
import React from "react";
import { PortalHost } from "@rn-primitives/portal";
import CustomDrawer from "@/components/CustomDrawer";
const Drawer = createDrawerNavigator();

const RootLayout = () => {
  return (
    <SafeAreaProvider>
      <Drawer.Navigator
        drawerContent={(props) => <CustomDrawer {...props} />}
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
              accessibilityLabel="Open camera"
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
          component={Index}
          options={{
            title: "",
          }}
        />
      </Drawer.Navigator>
      <PortalHost />
    </SafeAreaProvider>
  );
};

export default RootLayout;
