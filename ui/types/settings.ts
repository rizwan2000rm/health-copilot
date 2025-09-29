export type ApiKeyService = "hevy" | "openai";

export interface ApiKeyConfig {
  service: ApiKeyService;
  key: string;
  isValid: boolean;
  lastValidated?: Date;
  label?: string; // User-defined label
}

export interface SettingsState {
  apiKeys: Record<string, ApiKeyConfig>;
  isLoading: boolean;
  error?: string;
}

export interface SettingsStorage {
  // Secure storage for API keys
  saveApiKey(service: string, key: string): Promise<void>;
  getApiKey(service: string): Promise<string | null>;
  deleteApiKey(service: string): Promise<void>;

  // Regular storage for settings
  saveSetting(key: string, value: any): Promise<void>;
  getSetting(key: string): Promise<any>;
  deleteSetting(key: string): Promise<void>;
}

export interface ApiValidationService {
  validateHevyKey(key: string): Promise<boolean>;
  validateOpenAIKey(key: string): Promise<boolean>;
}
