import axios from 'axios';
import { z } from 'zod';

const userRoles = ['admin', 'member', 'viewer'] as const;
type UserRole = (typeof userRoles)[number];

const UserProfileSchema = z.object({
  name: z.string(),
  email: z.string(),
  role: z.enum(userRoles),
  phoneNumber: z.string().optional(),
});

export type UserProfile = z.infer<typeof UserProfileSchema>;

export async function fetchUserProfile(userId: string): Promise<UserProfile> {
  const response = await axios.get(`/api/users/${userId}`);
  return UserProfileSchema.parse(response.data);
}
