import React, { useRef } from "react";
import { Animated, Pressable } from "react-native";
import { Ionicons } from "@expo/vector-icons";

type Props = {
  disabled?: boolean;
  onPress: () => void;
  size?: number; // px
};

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

const SendButton = ({ disabled, onPress, size = 24 }: Props) => {
  const scale = useRef(new Animated.Value(1)).current;

  const onPressIn = () => {
    Animated.spring(scale, { toValue: 0.94, useNativeDriver: true }).start();
  };
  const onPressOut = () => {
    Animated.spring(scale, {
      toValue: 1,
      useNativeDriver: true,
      friction: 4,
    }).start();
  };

  return (
    <AnimatedPressable
      accessibilityLabel="Send message"
      accessibilityRole="button"
      onPressIn={onPressIn}
      onPressOut={onPressOut}
      onPress={onPress}
      disabled={disabled}
      style={{ transform: [{ scale }], height: size, width: size }}
      className={`rounded-full items-center justify-center ${
        disabled ? "bg-[#2a2a2a]" : "bg-[#2d6cdf]"
      }`}
    >
      <Ionicons
        name="send"
        size={Math.max(16, Math.floor(size * 0.38))}
        color={disabled ? "#777777" : "#ffffff"}
      />
    </AnimatedPressable>
  );
};

export default React.memo(SendButton);
