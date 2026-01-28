export function getApiErrorMessage(error, fallback = "Request failed") {
	const apiError =
		error?.response?.data?.error ??
		error?.response?.data?.message ??
		error?.response?.data?.detail;
	if (typeof apiError === "string" && apiError.trim()) {
		return apiError;
	}

	const hasResponse = Boolean(error?.response);
	const status = error?.response?.status;

	if (!hasResponse) {
		// Most common cause in Expo/React Native: wrong base URL (127.0.0.1 from device) or backend not running.
		return `${fallback}: can’t reach the server. Check API base URL and that backend is running.`;
	}

	if (status) {
		return `${fallback} (HTTP ${status})`;
	}

	return fallback;
}
