
import { apiClient } from "./client";

export async function signup({ name, email, password }) {
	const res = await apiClient.post("/auth/signup", { name, email, password });
	return res.data;
}

export async function login({ email, password }) {
	const res = await apiClient.post("/auth/login", { email, password });
	return res.data;
}

export async function me() {
	const res = await apiClient.get("/auth/me");
	return res.data;
}

export async function refreshAccessToken(refreshToken) {
	const res = await apiClient.post(
		"/auth/refresh",
		{},
		{
			headers: {
				Authorization: `Bearer ${refreshToken}`,
			},
		}
	);
	return res.data;
}

