import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
import { refreshToken } from "./api/auth";

const API_BASE = 'https://backend-service-813842978116.us-central1.run.app/api';
// const API_BASE = "http://127.0.0.1:8000/api";

// Create an Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  withCredentials: false, // Set to true if you need cookies
});

// Add a request interceptor to include sessionId if available
apiClient.interceptors.request.use((config) => {
  console.log("🔍 Axios interceptor: Processing request to", config.url);

  if (typeof window !== "undefined") {
    const userStr = localStorage.getItem("user");
    console.log("🔍 Axios interceptor: userStr from localStorage:", userStr);

    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        console.log("🔍 Axios interceptor: Parsed user object:", user);

        // Accept both sessionId and session_id, but always use sessionId for header
        const sessionId = user.sessionId || user.session_id;
        console.log("🔍 Axios interceptor: Extracted sessionId:", sessionId);

        if (sessionId) {
          config.headers = config.headers || {};
          config.headers["Authorization"] = `Bearer ${sessionId}`;
          console.log("✅ Axios interceptor: Authorization header set");
        } else {
          console.log(
            "❌ Axios interceptor: No sessionId found in user object"
          );
        }
      } catch (parseError) {
        console.error(
          "❌ Axios interceptor: Failed to parse user object:",
          parseError
        );
      }
    } else {
      console.log("❌ Axios interceptor: No user found in localStorage");
    }
  } else {
    console.log("❌ Axios interceptor: Window not available (SSR)");
  }

  // Log the final Authorization header
  if (config.headers && config.headers["Authorization"]) {
    console.log(
      "✅ Final Authorization header:",
      config.headers["Authorization"]
    );
  } else {
    console.log("❌ Final Authorization header not set");
  }

  // Ensure correct Content-Type: let the browser set it for FormData
  const isFormData =
    typeof FormData !== "undefined" && config.data instanceof FormData;
  config.headers = config.headers || {};
  if (isFormData) {
    // Remove any preset content-type to allow boundary to be set
    delete (config.headers as any)["Content-Type"];
  } else {
    // Default to JSON for non-FormData requests
    (config.headers as any)["Content-Type"] = "application/json";
  }

  return config;
});

// Helper function for API requests
export async function apiRequest<T = any>(
  config: AxiosRequestConfig
): Promise<AxiosResponse<T>> {
  try {
    const response = await apiClient.request<T>(config);
    return response;
  } catch (error: any) {
    // If 401, try refresh token logic
    if (error.status === 401 && typeof window !== "undefined") {
      const userStr = localStorage.getItem("user");
      if (userStr) {
        const user = JSON.parse(userStr);
        const sessionId = user.sessionId || user.session_id;
        if (sessionId) {
          try {
            const refresh = await refreshToken(sessionId);
            // Update localStorage with new sessionId if changed
            const updatedUser = { ...user, sessionId: refresh.session_id };
            localStorage.setItem("user", JSON.stringify(updatedUser));
            // Retry the original request with new sessionId
            config.headers = config.headers || {};
            config.headers["Authorization"] = `Bearer ${refresh.session_id}`;
            return await apiClient.request<T>(config);
          } catch (refreshError) {
            // Refresh failed, log out user
            localStorage.removeItem("user");
            window.location.reload();
            throw new Error("Session expired. Please log in again.");
          }
        }
      }
    }
    if (error.response) {
      // Server responded with a status other than 2xx
      throw error.response;
    } else if (error.request) {
      // No response received
      throw new Error("No response from server");
    } else {
      // Something else happened
      throw new Error(error.message || "API request failed");
    }
  }
}

export default apiClient;
