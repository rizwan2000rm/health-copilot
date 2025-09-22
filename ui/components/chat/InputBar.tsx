import React from "react";
import { TextInput, View } from "react-native";
import SendButton from "@/components/chat/SendButton";

type Props = {
  value: string;
  onChange: (text: string) => void;
  canSend: boolean;
  onSend: () => void;
};

const InputBar = ({ value, onChange, canSend, onSend }: Props) => {
  return (
    <View className="w-full p-4 pb-6 flex-row items-center gap-2">
      <View className="flex-1 flex-row items-center bg-[#1f1f1f] rounded-full px-4">
        <TextInput
          value={value}
          onChangeText={onChange}
          placeholder="Ask your fitness coach..."
          className="flex-1 py-3 text-[#f8f7f3] placeholder:text-[#9c9a92]"
          placeholderTextColor="#9c9a92"
          multiline={false}
          returnKeyType="send"
          onSubmitEditing={onSend}
          blurOnSubmit={false}
        />
      </View>
      <SendButton disabled={!canSend} onPress={onSend} />
    </View>
  );
};

export default React.memo(InputBar);
