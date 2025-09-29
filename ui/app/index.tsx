import { View } from "react-native";
import Chat from "@/components/Chat";

import "../global.css";

interface IndexProps {
  currentChatId?: string | null;
  onChatSaved?: () => void;
}

const Index = ({ currentChatId, onChatSaved }: IndexProps) => {
  return (
    <View className="flex-1 bg-black">
      <Chat currentChatId={currentChatId} onChatSaved={onChatSaved} />
    </View>
  );
};

export default Index;
