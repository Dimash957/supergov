/**
 * Advanced API client with proper error handling, validation, and retry logic
 */

import { getApiBase } from './apiBase';

interface ApiError {
  status: number;
  message: string;
  detail?: string;
  timestamp: string;
}

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
}

async function parseResponseBody<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return {} as T;
  }

  const raw = await response.text();
  if (!raw.trim()) {
    return {} as T;
  }

  try {
    return JSON.parse(raw) as T;
  } catch {
    throw {
      status: response.status,
      message: 'Invalid JSON response from server',
      timestamp: new Date().toISOString()
    } as ApiError;
  }
}

class ApiClient {
  private baseUrl: string;
  private timeout: number = 30000;

  constructor() {
    this.baseUrl = getApiBase();
  }

  /**
   * Fetch with proper error handling and JSON validation
   */
  private async fetchWithValidation<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (options.headers) {
        const normalized = new Headers(options.headers);
        normalized.forEach((value, key) => {
          headers[key] = value;
        });
      }

      // Add auth token if available
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}${url}`, {
        ...options,
        headers,
        signal: controller.signal
      });

      // Check if response is ok
      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        let errorMessage = `HTTP ${response.status}`;
        let detail: string | undefined;

        try {
          if (contentType?.includes('application/json')) {
            const errorData = await parseResponseBody<Record<string, any>>(response);
            errorMessage = errorData.detail || errorData.message || errorMessage;
            detail = errorData.detail;
          } else {
            const text = await response.text();
            errorMessage = text || errorMessage;
          }
        } catch {
          // If we can't parse error response, use generic message
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }

        throw {
          status: response.status,
          message: errorMessage,
          detail,
          timestamp: new Date().toISOString()
        } as ApiError;
      }

      const data = await parseResponseBody<T>(response);
      return data as T;
    } catch (error) {
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw {
          status: 0,
          message: 'Network error: Failed to connect to server',
          timestamp: new Date().toISOString()
        } as ApiError;
      }

      if (error instanceof DOMException && error.name === 'AbortError') {
        throw {
          status: 0,
          message: 'Request timeout: Server did not respond in time',
          timestamp: new Date().toISOString()
        } as ApiError;
      }

      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * GET request
   */
  async get<T = any>(url: string): Promise<T> {
    return this.fetchWithValidation<T>(url, {
      method: 'GET'
    });
  }

  /**
   * POST request with JSON body
   */
  async post<T = any>(url: string, data?: any): Promise<T> {
    return this.fetchWithValidation<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  /**
   * POST request with FormData (for file uploads)
   */
  async postFormData<T = any>(url: string, formData: FormData): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const headers: Record<string, string> = {};

      // Add auth token if available (don't set Content-Type with FormData)
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}${url}`, {
        method: 'POST',
        headers,
        body: formData,
        signal: controller.signal
      });

      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        let errorMessage = `HTTP ${response.status}`;

        try {
          if (contentType?.includes('application/json')) {
            const errorData = await parseResponseBody<Record<string, any>>(response);
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } else {
            const text = await response.text();
            errorMessage = text || errorMessage;
          }
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }

        throw {
          status: response.status,
          message: errorMessage,
          timestamp: new Date().toISOString()
        } as ApiError;
      }

      const data = await parseResponseBody<T>(response);
      return data as T;
    } catch (error) {
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw {
          status: 0,
          message: 'Network error: Failed to connect to server',
          timestamp: new Date().toISOString()
        } as ApiError;
      }

      if (error instanceof DOMException && error.name === 'AbortError') {
        throw {
          status: 0,
          message: 'Request timeout: Server did not respond in time',
          timestamp: new Date().toISOString()
        } as ApiError;
      }

      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * PUT request
   */
  async put<T = any>(url: string, data?: any): Promise<T> {
    return this.fetchWithValidation<T>(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(url: string): Promise<T> {
    return this.fetchWithValidation<T>(url, {
      method: 'DELETE'
    });
  }

  /**
   * Set custom timeout
   */
  setTimeout(ms: number) {
    this.timeout = ms;
  }
}

export const apiClient = new ApiClient();

// Error formatter for display
export function formatApiError(error: any): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (error?.message) {
    return error.message;
  }

  return 'An unknown error occurred';
}

export type { ApiError, ApiResponse };
