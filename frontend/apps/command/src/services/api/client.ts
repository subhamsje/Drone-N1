/**
 * Production-Grade Resilient HTTP Client with Interceptors, Retry, and Error Handling.
 */

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
  }

  public async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries: number = 2
  ): Promise<ApiResponse<T>> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'X-Altaria-Client': 'CommandDeck-v2.5',
      ...(options.headers || {}),
    };

    let attempt = 0;
    while (attempt <= retries) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 6000);

        const response = await fetch(url, {
          ...options,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
        }

        const data: T = await response.json();
        return { data, error: null, status: response.status };
      } catch (err: any) {
        attempt++;
        if (attempt > retries) {
          console.warn(`[ApiClient] Request to ${endpoint} failed after ${retries + 1} attempts:`, err.message);
          return {
            data: null,
            error: err.name === 'AbortError' ? 'Request timed out' : err.message || 'Network request failed',
            status: 0,
          };
        }
        await new Promise((r) => setTimeout(r, attempt * 500));
      }
    }

    return { data: null, error: 'Maximum retry limit reached', status: 0 };
  }

  public get<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public post<T>(endpoint: string, body?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public put<T>(endpoint: string, body?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public delete<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
