import { SafeAreaProvider } from "react-native-safe-area-context";
import { createDrawerNavigator } from "@react-navigation/drawer";
import "react-native-reanimated";
import "../global.css";
import Index from "./index";

const Drawer = createDrawerNavigator();

const RootLayout = () => {
  return (
    <SafeAreaProvider>
      <Drawer.Navigator
        screenOptions={{
          headerShown: true,
          headerStyle: {
            backgroundColor: "#000000",
          },
          headerTintColor: "#ffffff",
          headerTitleStyle: {
            fontWeight: "bold",
            color: "#ffffff",
          },
          drawerStyle: {
            backgroundColor: "#000000",
          },
          drawerActiveTintColor: "#ffffff",
          drawerInactiveTintColor: "#666666",
          drawerLabelStyle: {
            color: "#ffffff",
          },
          drawerContentContainerStyle: {
            backgroundColor: "#000000",
          },
          drawerContentStyle: {
            backgroundColor: "#000000",
          },
        }}
      >
        <Drawer.Screen
          name="Home"
          component={Index}
          options={{
            title: "Health Coach",
          }}
        />
      </Drawer.Navigator>
    </SafeAreaProvider>
  );
};

export default RootLayout;
