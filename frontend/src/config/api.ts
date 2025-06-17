// API configuration
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export { API_BASE_URL };

// API client utility
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // API methods
  async getHealth() {
    return this.request("/health");
  }

  async getUsers() {
    return this.request("/api/users");
  }

  async getUser(id: number) {
    return this.request(`/api/users/${id}`);
  }

  async getRoot() {
    return this.request("/");
  }
}

// Default export for easy usage
export const apiClient = new ApiClient();
