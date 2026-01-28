
import axios from "axios";

import { API_BASE_URL } from "../config/env";
import {
	clearSession,
	getAccessToken,
	getRefreshToken,
	setAccessToken,
} from "../storage/tokenStorage";
import { refreshAccessToken } from "./auth.api";

export const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
	timeout: 15000,
});

apiClient.interceptors.request.use(async (config) => {
	const token = await getAccessToken();
	if (token) {
		config.headers = config.headers ?? {};
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

let refreshPromise = null;

apiClient.interceptors.response.use(
	(response) => response,
	async (error) => {
		const originalRequest = error?.config;
		const status = error?.response?.status;

		if (!originalRequest || status !== 401) {
			return Promise.reject(error);
		}

		// Avoid infinite loops
		if (originalRequest._retry) {
			return Promise.reject(error);
		}
		originalRequest._retry = true;

		const refreshToken = await getRefreshToken();
		if (!refreshToken) {
			await clearSession();
			return Promise.reject(error);
		}

		try {
			if (!refreshPromise) {
				refreshPromise = (async () => {
					const data = await refreshAccessToken(refreshToken);
					await setAccessToken(data.access_token);
					return data.access_token;
				})().finally(() => {
					refreshPromise = null;
				});
			}

			const newAccessToken = await refreshPromise;
			originalRequest.headers = originalRequest.headers ?? {};
			originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
			return apiClient(originalRequest);
		} catch (refreshErr) {
			await clearSession();
			return Promise.reject(refreshErr);
		}
	}
);

