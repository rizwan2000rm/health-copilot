import React, { useState } from "react";
import { View, Text, Pressable, ActivityIndicator, Alert } from "react-native";
import { importHealthZip } from "@/services/healthImport";

const HealthImportSection = () => {
  const [busy, setBusy] = useState(false);

  const onImport = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const res = await importHealthZip();
      if ("error" in res) {
        Alert.alert("Import failed", res.error);
      } else {
        Alert.alert("Import complete", `Imported ${res.days} day(s) of data.`);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <Text className="text-gray-400 text-sm mb-4">Health Data</Text>
      <View className="bg-gray-900 rounded-lg p-4 mb-4">
        <Text className="text-gray-400 text-sm mb-4">
          Import your Apple Health export (.zip). We'll parse steps, active and
          basal energy, and sleep and store daily summaries locally.
        </Text>
        <Pressable
          onPress={onImport}
          className={`rounded-lg px-4 py-3 items-center justify-center ${busy ? "bg-gray-700" : "bg-[#a99be4]"}`}
          disabled={busy}
        >
          {busy ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="text-white font-medium">
              Import Health Export (.zip)
            </Text>
          )}
        </Pressable>
      </View>
    </>
  );
};

export default HealthImportSection;
