import axios from "axios";

type UserRole = "admin" | "member" | "viewer";

interface User {
  name: string;
  email: string;
  role: UserRole;
  phoneNumber?: string;
}

const apiClient = axios.create({
  baseURL: "/api",
});

export async function getUserById(id: string): Promise<User> {
  const response = await apiClient.get<User>(`/users/${id}`);
  return response.data;
}
