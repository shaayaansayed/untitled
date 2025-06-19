// API configuration
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export { API_BASE_URL };

export interface PriorAuth {
  id: string;
  patient_name: string;
  date: string;
  procedure: string;
  status: string;
  created_at: string;
  updated_at: string;
  auth_document?: {
    id: string;
    filename: string;
    original_name: string;
    url: string;
  };
  clinical_notes?: {
    id: string;
    filename: string;
    original_name: string;
    url: string;
  };
}

export interface CreatePriorAuthRequest {
  patient_name: string;
  procedure: string;
  auth_document_id: string;
  clinical_notes_id: string;
}

export interface UploadFileResponse {
  id: string;
  filename: string;
  original_name: string;
  mime_type: string;
  size: number;
  file_path: string;
  upload_date: string;
  url: string;
}

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
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // File upload methods
  async uploadFile(
    file: File,
    fileType: "prior_authorization" | "clinical_notes"
  ): Promise<UploadFileResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      `${this.baseUrl}/api/files/upload?file_type=${fileType}`,
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return response.json();
  }

  getFileUrl(fileId: string): string {
    return `${this.baseUrl}/api/files/${fileId}`;
  }

  // Prior Authorization methods
  async getPriorAuthorizations(): Promise<PriorAuth[]> {
    return this.request("/api/prior-authorizations");
  }

  async getPriorAuthorization(id: string): Promise<PriorAuth> {
    return this.request(`/api/prior-authorizations/${id}`);
  }

  async createPriorAuthorization(
    data: CreatePriorAuthRequest
  ): Promise<PriorAuth> {
    return this.request("/api/prior-authorizations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
  }

  async deletePriorAuthorization(id: string): Promise<void> {
    await this.request(`/api/prior-authorizations/${id}`, {
      method: "DELETE",
    });
  }

  // Health check
  async getHealth() {
    return this.request("/health");
  }
}

// Default export for easy usage
export const apiClient = new ApiClient();
