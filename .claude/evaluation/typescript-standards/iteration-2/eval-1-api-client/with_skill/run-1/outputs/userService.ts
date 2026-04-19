import axios from 'axios';
import { z } from 'zod';

const UserRole = ['admin', 'member', 'viewer'] as const;
type UserRole = (typeof UserRole)[number];

const UserProfileSchema = z.object({
  name: z.string(),
  email: z.string().email(),
  role: z.enum(UserRole),
  phoneNumber: z.string().optional(),
});

export type UserProfile = z.infer<typeof UserProfileSchema>;

export async function fetchUserProfile(userId: string): Promise<UserProfile> {
  const response = await axios.get<unknown>(`/api/users/${userId}`);
  return UserProfileSchema.parse(response.data);
}
