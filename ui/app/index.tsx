import { View, Text } from "react-native";
import "../global.css";

const Index = () => {
  return (
    <View className="flex-1 bg-black text-blue-400">
      <View className="flex-1 justify-center items-center px-5">
        <Text className="text-3xl font-bold text-white text-center mb-2">
          Welcome to Health Coach
        </Text>
        <Text className="text-base text-gray-300 text-center leading-6">
          Your AI-powered fitness companion
        </Text>
      </View>
    </View>
  );
};

export default Index;
