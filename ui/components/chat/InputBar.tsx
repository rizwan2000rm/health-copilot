import React from "react";
import { View } from "react-native";
import SendButton from "@/components/chat/SendButton";
import { Textarea } from "../ui/textarea";

type Props = {
  value: string;
  onChange: (text: string) => void;
  canSend: boolean;
  onSend: () => void;
};

const InputBar = ({ value, onChange, canSend, onSend }: Props) => {
  return (
    <View className="w-full p-4 pb-6 flex-row items-center gap-2">
      <View className="flex-1 min-h-12 py-2 pr-2 bg-[#1f1f1f] rounded-3xl border border-[#2a2a2a] flex-row justify-center items-center">
        <Textarea
          value={value}
          onChangeText={onChange}
          placeholder="Ask your fitness coach..."
          className="flex-1 mx-3 !pt-0 text-base leading-5 text-[#f8f7f3]"
          placeholderTextColor="#9c9a92"
          returnKeyType="next"
          onSubmitEditing={() => onSend()}
          submitBehavior="blurAndSubmit"
          unstyled
        />

        <View className="self-end">
          <SendButton disabled={!canSend} onPress={() => onSend()} size={32} />
        </View>
      </View>
    </View>
  );
};

export default React.memo(InputBar);
