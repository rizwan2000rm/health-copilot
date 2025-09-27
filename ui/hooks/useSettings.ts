import { useCallback, useEffect, useState } from "react";
import type { SettingsState, ApiKeyConfig } from "@/types/settings";
import { settingsStorage } from "@/services/settingsStorage";
import { apiValidationService } from "@/services/apiValidation";
import { supportedApiServices } from "@/lib/settingsDefaults";

export function useSettings() {
  const [settings, setSettings] = useState<SettingsState>({
    apiKeys: {},
    isLoading: true,
  });

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = useCallback(async () => {
    try {
      setSettings((prev) => ({ ...prev, isLoading: true, error: undefined }));

      // Load API keys
      const apiKeys: Record<string, ApiKeyConfig> = {};
      for (const service of supportedApiServices) {
        const key = await settingsStorage.getApiKey(service.id);
        if (key) {
          apiKeys[service.id] = {
            service: service.id as "hevy" | "openai",
            key,
            isValid: false, // Will be validated separately
            lastValidated: undefined,
          };
        }
      }

      setSettings({
        apiKeys,
        isLoading: false,
        error: undefined,
      });
    } catch (error) {
      console.error("Failed to load settings:", error);
      setSettings((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to load settings",
      }));
    }
  }, []);

  const saveApiKey = useCallback(async (service: string, key: string) => {
    try {
      await settingsStorage.saveApiKey(service, key);

      // Update state
      setSettings((prev) => ({
        ...prev,
        apiKeys: {
          ...prev.apiKeys,
          [service]: {
            service: service as "hevy" | "openai",
            key,
            isValid: false,
            lastValidated: undefined,
          },
        },
        error: undefined,
      }));
    } catch (error) {
      console.error(`Failed to save API key for ${service}:`, error);
      setSettings((prev) => ({
        ...prev,
        error: `Failed to save API key for ${service}`,
      }));
    }
  }, []);

  const validateApiKey = useCallback(async (service: string, key: string) => {
    try {
      let isValid = false;

      if (service === "hevy") {
        isValid = await apiValidationService.validateHevyKey(key);
      } else if (service === "openai") {
        isValid = await apiValidationService.validateOpenAIKey(key);
      }

      // Update validation status
      setSettings((prev) => ({
        ...prev,
        apiKeys: {
          ...prev.apiKeys,
          [service]: {
            ...prev.apiKeys[service],
            isValid,
            lastValidated: new Date(),
          },
        },
        error: undefined,
      }));

      return isValid;
    } catch (error) {
      console.error(`Failed to validate API key for ${service}:`, error);
      setSettings((prev) => ({
        ...prev,
        error: `Failed to validate API key for ${service}`,
      }));
      return false;
    }
  }, []);

  const deleteApiKey = useCallback(async (service: string) => {
    try {
      await settingsStorage.deleteApiKey(service);

      // Update state
      setSettings((prev) => {
        const newApiKeys = { ...prev.apiKeys };
        delete newApiKeys[service];
        return {
          ...prev,
          apiKeys: newApiKeys,
          error: undefined,
        };
      });
    } catch (error) {
      console.error(`Failed to delete API key for ${service}:`, error);
      setSettings((prev) => ({
        ...prev,
        error: `Failed to delete API key for ${service}`,
      }));
    }
  }, []);

  const clearError = useCallback(() => {
    setSettings((prev) => ({ ...prev, error: undefined }));
  }, []);

  return {
    settings,
    saveApiKey,
    validateApiKey,
    deleteApiKey,
    clearError,
    isLoading: settings.isLoading,
    error: settings.error,
  };
}
