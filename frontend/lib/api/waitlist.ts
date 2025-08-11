import { apiRequest } from '../axiosConfig';

export interface WaitlistEntry {
  email: string;
  name?: string;
  use_case?: string;
  referral_source?: string;
}

export interface WaitlistResponse {
  id?: string;
  email: string;
  name?: string;
  use_case?: string;
  referral_source?: string;
  created_at: string;
  updated_at: string;
  is_notified: boolean;
  position?: number;
}

export interface WaitlistJoinResponse {
  success: boolean;
  message: string;
  entry: WaitlistResponse;
  total_entries: number;
}

export async function joinWaitlist(data: WaitlistEntry): Promise<WaitlistJoinResponse> {
  try {
    console.log('🔍 Joining waitlist:', data.email);
    
    const response = await apiRequest<WaitlistJoinResponse>({
      url: '/waitlist/join',
      method: 'POST',
      data,
    });
    
    console.log('✅ Successfully joined waitlist:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to join waitlist:', error);
    throw error;
  }
}

export async function checkWaitlistStatus(email: string): Promise<WaitlistResponse> {
  try {
    console.log('🔍 Checking waitlist status for:', email);
    
    const response = await apiRequest<WaitlistResponse>({
      url: `/waitlist/check/${encodeURIComponent(email)}`,
      method: 'GET',
    });
    
    console.log('✅ Waitlist status retrieved:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to check waitlist status:', error);
    throw error;
  }
}