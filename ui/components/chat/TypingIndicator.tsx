import React from "react";
import { Text, View } from "react-native";

const TypingIndicator = () => {
  return (
    <View className="w-full px-4 mt-1 mb-2 items-start">
      <Text className="text-[#8a8a8a]">Thinking...</Text>
    </View>
  );
};

export default React.memo(TypingIndicator);
