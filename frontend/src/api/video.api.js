
import { apiClient } from "./client";

export async function fetchDashboardVideos() {
	const res = await apiClient.get("/dashboard");
	return res.data;
}

export async function fetchPlaybackToken(videoId) {
	const res = await apiClient.get(`/video/${videoId}/token`);
	return res.data;
}

export async function fetchStreamUrl(videoId, token) {
	const res = await apiClient.get(`/video/${videoId}/stream`, {
		params: { token },
	});
	return res.data;
}

