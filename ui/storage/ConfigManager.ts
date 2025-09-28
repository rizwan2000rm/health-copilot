import AsyncStorage from "@react-native-async-storage/async-storage";
import { ChatConfig, DEFAULT_CONFIG } from "@/types/chatHistory";

const CONFIG_KEY = "chat_config";

export class ConfigManager {
  private static instance: ConfigManager;
  private config: ChatConfig;
  private initialized = false;

  private constructor() {
    this.config = { ...DEFAULT_CONFIG };
  }

  public static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  public async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      const storedConfig = await AsyncStorage.getItem(CONFIG_KEY);
      if (storedConfig) {
        const parsedConfig = JSON.parse(storedConfig);
        this.config = { ...DEFAULT_CONFIG, ...parsedConfig } as ChatConfig;
      }
    } catch (error) {
      console.warn("Failed to load config, using defaults:", error);
      this.config = { ...DEFAULT_CONFIG };
    }

    this.initialized = true;
  }

  public getConfig(): ChatConfig {
    return { ...this.config };
  }

  public async updateConfig(updates: Partial<ChatConfig>): Promise<void> {
    this.config = { ...this.config, ...updates };

    try {
      await AsyncStorage.setItem(CONFIG_KEY, JSON.stringify(this.config));
    } catch (error) {
      console.error("Failed to save config:", error);
      throw new Error("Failed to save configuration");
    }
  }

  public async resetConfig(): Promise<void> {
    this.config = { ...DEFAULT_CONFIG };

    try {
      await AsyncStorage.setItem(CONFIG_KEY, JSON.stringify(this.config));
    } catch (error) {
      console.error("Failed to reset config:", error);
      throw new Error("Failed to reset configuration");
    }
  }

  // Convenience getters
  public get maxChatsInDrawer(): number {
    return this.config.maxChatsInDrawer;
  }

  public get maxChatHistory(): number {
    return this.config.maxChatHistory;
  }

  public get searchDebounceMs(): number {
    return this.config.searchDebounceMs;
  }

  public get autoSaveIntervalMs(): number {
    return this.config.autoSaveIntervalMs;
  }

  public get enableSearchIndexing(): boolean {
    return this.config.enableSearchIndexing;
  }
}

export const configManager = ConfigManager.getInstance();
