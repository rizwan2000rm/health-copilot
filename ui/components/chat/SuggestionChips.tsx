import React, { useMemo } from "react";
import { ScrollView, Text, View, TouchableOpacity } from "react-native";

type Props = {
  onSend: (text: string) => void;
};

const defaultSuggestions = ["Plan my next week workouts"];

const SuggestionChips = ({ onSend }: Props) => {
  const chips = useMemo(() => defaultSuggestions, []);
  return (
    <View className="w-full pb-2 pt-1">
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 16,
          gap: 12,
        }}
      >
        {chips.map((label) => (
          <TouchableOpacity
            key={label}
            className="px-4 py-3 bg-[#1a1a1a] rounded-2xl border border-[#2a2a2a] max-w-60"
            onPress={() => onSend(label)}
            activeOpacity={0.7}
          >
            <Text
              className="text-[#eaeaea] leading-5"
              numberOfLines={4}
              ellipsizeMode="tail"
            >
              {label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

export default React.memo(SuggestionChips);
