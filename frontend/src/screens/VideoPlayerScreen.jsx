
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Linking, SafeAreaView, Text, TouchableOpacity, View } from "react-native";
import { ResizeMode, Video } from "expo-av";
import { WebView } from "react-native-webview";

import Loader from "../components/Loader";
import { fetchPlaybackToken, fetchStreamUrl } from "../api/video.api";

export default function VideoPlayerScreen({ route }) {
	const videoParam = route?.params?.video;
	const videoId = videoParam?.id;

	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const [url, setUrl] = useState(null);
	const [watchUrl, setWatchUrl] = useState(null);
	const [streamType, setStreamType] = useState(null);
	const [webViewFailed, setWebViewFailed] = useState(false);
	const videoRef = useRef(null);

	const webUrl = useMemo(() => {
		if (!url) return null;
		const join = url.includes("?") ? "&" : "?";
		// Improve YouTube embed behavior.
		return `${url}${join}autoplay=1&controls=1&playsinline=1&modestbranding=1&rel=0`;
	}, [url]);

	useEffect(() => {
		let mounted = true;

		(async () => {
			setError(null);
			setLoading(true);
			try {
				if (!videoId) throw new Error("Missing video id");
				setWebViewFailed(false);
				const tokenRes = await fetchPlaybackToken(videoId);
				const streamRes = await fetchStreamUrl(videoId, tokenRes.token);
				if (mounted) {
					setUrl(streamRes.url);
					setWatchUrl(streamRes.watch_url ?? null);
					const inferredType =
						streamRes.stream_type ??
						(streamRes.url?.includes("youtube.com/embed") ? "embed" : null) ??
						(streamRes.url?.toLowerCase()?.endsWith(".mp4") ? "mp4" : null);
					setStreamType(inferredType);
				}
			} catch (e) {
				const msg = e?.response?.data?.error ?? e?.message ?? "Failed to load stream";
				if (mounted) setError(msg);
			} finally {
				if (mounted) setLoading(false);
			}
		})();

		return () => {
			mounted = false;
		};
	}, [videoId]);

	if (loading) return <Loader />;

	return (
		<SafeAreaView style={{ flex: 1 }}>
			<View style={{ padding: 16, flex: 1 }}>
				<Text style={{ fontSize: 18, fontWeight: "700" }}>{videoParam?.title}</Text>
				<Text style={{ marginTop: 8, color: "#555" }}>{videoParam?.description}</Text>

				{error ? (
					<Text style={{ marginTop: 12, color: "#b00020" }}>{error}</Text>
				) : null}

				{url ? (
					<View style={{ marginTop: 16 }}>
						<View
							style={{
								width: "100%",
								aspectRatio: 16 / 9,
								borderRadius: 12,
								overflow: "hidden",
								backgroundColor: "#000",
							}}
						>
							{streamType === "mp4" ? (
								<Video
									ref={videoRef}
									source={{ uri: url }}
									style={{ width: "100%", height: "100%" }}
									useNativeControls
									resizeMode={ResizeMode.CONTAIN}
									onError={() => {
										setError("Failed to play this video.");
									}}
								/>
							) : webUrl ? (
								<WebView
									source={{ uri: webUrl }}
									originWhitelist={["*"]}
									javaScriptEnabled
									domStorageEnabled
									mediaPlaybackRequiresUserAction={false}
									allowsFullscreenVideo
									thirdPartyCookiesEnabled
									sharedCookiesEnabled
									startInLoadingState
									renderLoading={() => <Loader />}
									onError={() => {
										setWebViewFailed(true);
										setError(
											"Video player configuration error (often means YouTube embedding is disabled, e.g. error 153)."
										);
									}}
									onHttpError={() => {
										setWebViewFailed(true);
										setError(
											"Video player configuration error (often means YouTube embedding is disabled, e.g. error 153)."
										);
									}}
								/>
							) : null}
						</View>

						{watchUrl ? (
							<TouchableOpacity
								onPress={() => Linking.openURL(watchUrl)}
								style={{
									marginTop: 12,
									padding: 12,
									borderRadius: 10,
									backgroundColor: webViewFailed || error ? "#111827" : "#374151",
								}}
							>
								<Text style={{ color: "#fff", textAlign: "center", fontWeight: "700" }}>
									Open in YouTube
								</Text>
							</TouchableOpacity>
						) : null}
					</View>
				) : null}
			</View>
		</SafeAreaView>
	);
}


