import React, { useMemo } from "react";
import { ScrollView, Text, View } from "react-native";

type Props = {
  onPick: (text: string) => void;
};

const defaultSuggestions = [
  "Create an illustration",
  "Suggest a recipe",
  "Plan a 20‑min workout",
  "Track my progress",
  "What should I train today?",
];

const SuggestionChips = ({ onPick }: Props) => {
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
          <View
            key={label}
            className="px-4 py-3 bg-[#1a1a1a] rounded-2xl border border-[#2a2a2a] max-w-60"
            onTouchEnd={() => onPick(label)}
          >
            <Text
              className="text-[#eaeaea] leading-5"
              numberOfLines={4}
              ellipsizeMode="tail"
            >
              {label}
            </Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

export default React.memo(SuggestionChips);
