import { View } from "react-native";
import Chat from "@/components/Chat";

import "../global.css";

const Index = () => {
  return (
    <View className="flex-1 bg-black text-blue-400">
      <Chat />
    </View>
  );
};

export default Index;
