import React, { useState } from "react";
import { View, Text, TextInput, Pressable, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSettings } from "@/hooks/useSettings";
import { supportedApiServices } from "@/lib/settingsDefaults";

interface ApiKeyCardProps {
  serviceName: string;
  description: string;
  icon: string;
  placeholder: string;
  currentKey?: string;
  isValid?: boolean;
  onSave: (key: string) => Promise<void>;
  onDelete: () => Promise<void>;
}

const ApiKeyCard: React.FC<ApiKeyCardProps> = ({
  serviceName,
  description,
  icon,
  placeholder,
  currentKey,
  isValid = false,
  onSave,
  onDelete,
}) => {
  const [key, setKey] = useState(currentKey || "");
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!key.trim()) return;

    setIsSaving(true);
    try {
      await onSave(key.trim());
    } catch {
      Alert.alert("Error", "Failed to save API key");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = () => {
    Alert.alert(
      "Delete API Key",
      `Are you sure you want to delete the ${serviceName} API key?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await onDelete();
              setKey("");
            } catch {
              Alert.alert("Error", "Failed to delete API key");
            }
          },
        },
      ]
    );
  };

  return (
    <View className="bg-gray-900 rounded-lg p-4 mb-4">
      <View className="flex flex-row items-center gap-3 mb-3">
        <Text className="text-2xl">{icon}</Text>
        <View className="flex-1">
          <View className="flex flex-row items-center justify-between gap-2">
            <Text className="text-white font-semibold">{serviceName}</Text>
            {currentKey && (
              <View className="flex flex-row items-center gap-2">
                <View
                  className={`w-2 h-2 rounded-full ${
                    isValid ? "bg-green-500" : "bg-gray-500"
                  }`}
                />
                <Text className="text-gray-400 text-xs">
                  {isValid ? "Valid" : "Unknown"}
                </Text>
              </View>
            )}
          </View>
          <Text className="text-gray-400 text-sm">{description}</Text>
        </View>
      </View>

      <View className="space-y-3">
        <TextInput
          value={key}
          onChangeText={setKey}
          placeholder={placeholder}
          placeholderTextColor="#6b7280"
          className="bg-gray-800 text-white rounded-lg px-3 py-3 border border-gray-700"
          secureTextEntry
          autoCapitalize="none"
          autoCorrect={false}
        />

        <View className="flex flex-row gap-2 mt-3">
          <Pressable
            onPress={handleSave}
            disabled={!key.trim() || isSaving}
            className={`flex-1 py-3 rounded-lg ${
              key.trim() && !isSaving ? "bg-[#a99be4]" : "bg-gray-700"
            }`}
          >
            <Text className="text-white text-center font-medium">
              {isSaving ? "Saving..." : "Save"}
            </Text>
          </Pressable>

          {currentKey && (
            <>
              <Pressable
                onPress={handleDelete}
                className="px-4 py-3 rounded-lg bg-red-600"
              >
                <Ionicons name="trash-outline" size={16} color="white" />
              </Pressable>
            </>
          )}
        </View>
      </View>
    </View>
  );
};

const ApiKeysSection: React.FC = () => {
  const { settings, saveApiKey, validateApiKey, deleteApiKey } = useSettings();

  return (
    <View>
      <Text className="text-gray-400 text-sm mb-4">
        Configure your API keys
      </Text>

      {supportedApiServices.map((service) => (
        <ApiKeyCard
          key={service.id}
          serviceName={service.name}
          description={service.description}
          icon={service.icon}
          placeholder={service.placeholder}
          currentKey={settings.apiKeys[service.id]?.key}
          isValid={settings.apiKeys[service.id]?.isValid}
          onSave={(key) => saveApiKey(service.id, key)}
          onDelete={() => deleteApiKey(service.id)}
        />
      ))}
    </View>
  );
};

export default ApiKeysSection;
