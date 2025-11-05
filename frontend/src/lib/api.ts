import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import axiosRetry from "axios-retry";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    "Content-Type": "application/json",
  },
});

axiosRetry(api, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    return (
      axiosRetry.isNetworkOrIdempotentRequestError(error) ||
      error.response?.status! >= 500
    );
  },
});

export async function request<T = any>(
  config: AxiosRequestConfig
): Promise<AxiosResponse<T>> {
  return api(config);
}

export default api;
