import axios from 'axios';

type UserRole = 'admin' | 'member' | 'viewer';

interface UserProfile {
  name: string;
  email: string;
  role: UserRole;
  phoneNumber?: string;
}

export async function getUserProfile(id: string): Promise<UserProfile> {
  const response = await axios.get<UserProfile>(`/api/users/${id}`);
  return response.data;
}
