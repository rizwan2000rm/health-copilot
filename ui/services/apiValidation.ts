import type { ApiValidationService } from "@/types/settings";

class ApiValidationServiceImpl implements ApiValidationService {
  async validateHevyKey(key: string): Promise<boolean> {
    try {
      const response = await fetch("https://api.hevyapp.com/v1/routines", {
        method: "GET",
        headers: {
          "api-key": key,
          "User-Agent": "Health-Copilot/1.0",
        },
      });
      return response.ok;
    } catch (error) {
      console.error("Hevy API key validation failed:", error);
      return false;
    }
  }

  async validateOpenAIKey(key: string): Promise<boolean> {
    try {
      const response = await fetch("https://api.openai.com/v1/models", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${key}`,
          "User-Agent": "Health-Copilot/1.0",
        },
      });
      return response.ok;
    } catch (error) {
      console.error("OpenAI API key validation failed:", error);
      return false;
    }
  }
}

export const apiValidationService = new ApiValidationServiceImpl();
