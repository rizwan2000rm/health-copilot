import * as SecureStore from "expo-secure-store";
import AsyncStorage from "@react-native-async-storage/async-storage";
import type { SettingsStorage } from "@/types/settings";

class SettingsStorageService implements SettingsStorage {
  private readonly API_KEY_PREFIX = "api_key_";
  private readonly SETTING_PREFIX = "setting_";

  // Secure storage for API keys
  async saveApiKey(service: string, key: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(`${this.API_KEY_PREFIX}${service}`, key);
    } catch (error) {
      console.error(`Failed to save API key for ${service}:`, error);
      throw new Error(`Failed to save API key for ${service}`);
    }
  }

  async getApiKey(service: string): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(`${this.API_KEY_PREFIX}${service}`);
    } catch (error) {
      console.error(`Failed to get API key for ${service}:`, error);
      return null;
    }
  }

  async deleteApiKey(service: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(`${this.API_KEY_PREFIX}${service}`);
    } catch (error) {
      console.error(`Failed to delete API key for ${service}:`, error);
      throw new Error(`Failed to delete API key for ${service}`);
    }
  }

  // Regular storage for settings
  async saveSetting(key: string, value: any): Promise<void> {
    try {
      const serializedValue = JSON.stringify(value);
      await AsyncStorage.setItem(
        `${this.SETTING_PREFIX}${key}`,
        serializedValue
      );
    } catch (error) {
      console.error(`Failed to save setting ${key}:`, error);
      throw new Error(`Failed to save setting ${key}`);
    }
  }

  async getSetting(key: string): Promise<any> {
    try {
      const serializedValue = await AsyncStorage.getItem(
        `${this.SETTING_PREFIX}${key}`
      );
      if (serializedValue === null) return null;
      return JSON.parse(serializedValue);
    } catch (error) {
      console.error(`Failed to get setting ${key}:`, error);
      return null;
    }
  }

  async deleteSetting(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(`${this.SETTING_PREFIX}${key}`);
    } catch (error) {
      console.error(`Failed to delete setting ${key}:`, error);
      throw new Error(`Failed to delete setting ${key}`);
    }
  }
}

export const settingsStorage = new SettingsStorageService();
