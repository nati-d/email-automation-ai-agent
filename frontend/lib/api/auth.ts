import { apiRequest } from '../axiosConfig';

const AUTH_URL = '/auth/google/login';

export async function getGoogleAuthUrl() {
  const response = await apiRequest<{ authorization_url: string }>({
    url: AUTH_URL,
    method: 'GET',
  });
  return response.data.authorization_url;
}

export function saveUserToStorage(user: any) {
  localStorage.setItem('user', JSON.stringify(user));
}

export function getUserFromStorage() {
  const stored = localStorage.getItem('user');
  return stored ? JSON.parse(stored) : null;
}

export function clearUserFromStorage() {
  localStorage.removeItem('user');
}

export interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
  message: string;
  session_id: string;
}

export async function refreshToken(sessionId: string): Promise<RefreshTokenResponse> {
  const response = await apiRequest<RefreshTokenResponse>({
    url: '/auth/refresh',
    method: 'POST',
    data: { session_id: sessionId },
  });
  return response.data;
} 