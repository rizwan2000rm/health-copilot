import React, { useEffect, useRef } from "react";
import { Animated, Easing, Text, View } from "react-native";
import type { ChatMessage } from "@/types/chat";

type Props = {
  message: ChatMessage;
};

const MessageBubble = ({ message }: Props) => {
  const isUser = message.role === "user";
  const translateY = useRef(new Animated.Value(8)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: 0,
        duration: 180,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.timing(opacity, {
        toValue: 1,
        duration: 180,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();
  }, [opacity, translateY]);

  return (
    <View
      className={`w-full px-4 mb-2 ${isUser ? "items-end" : "items-start"}`}
    >
      <Animated.View
        style={{ transform: [{ translateY }], opacity }}
        className={
          isUser
            ? "max-w-[86%] rounded-2xl px-4 py-3 bg-[#2d6cdf]"
            : "max-w-[90%]"
        }
      >
        <Text
          className={`text-base leading-6 ${
            isUser ? "text-white" : "text-[#eaeaea]"
          }`}
        >
          {message.text}
        </Text>
      </Animated.View>
    </View>
  );
};

export default React.memo(MessageBubble);
