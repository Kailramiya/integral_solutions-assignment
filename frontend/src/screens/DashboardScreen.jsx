
import React, { useCallback, useEffect, useLayoutEffect, useState } from "react";
import { Alert, FlatList, RefreshControl, SafeAreaView, Text, TouchableOpacity, View } from "react-native";

import { fetchDashboardVideos } from "../api/video.api";
import Loader from "../components/Loader";
import VideoTile from "../components/VideoTile";
import { clearSession } from "../storage/tokenStorage";

export default function DashboardScreen({ navigation }) {
	const [items, setItems] = useState([]);
	const [loading, setLoading] = useState(true);
	const [refreshing, setRefreshing] = useState(false);
	const [error, setError] = useState(null);

	useLayoutEffect(() => {
		navigation.setOptions({
			headerRight: () => (
				<View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
					<TouchableOpacity
						onPress={() => navigation.navigate("Settings")}
						style={{ paddingHorizontal: 12, paddingVertical: 6 }}
					>
						<Text style={{ color: "#111827", fontWeight: "700" }}>Settings</Text>
					</TouchableOpacity>

					<TouchableOpacity
						onPress={() => {
							Alert.alert("Logout", "Do you want to logout?", [
								{ text: "Cancel", style: "cancel" },
								{
									text: "Logout",
									style: "destructive",
									onPress: async () => {
										await clearSession();
										navigation.reset({ index: 0, routes: [{ name: "Login" }] });
									},
								},
							]);
						}}
						style={{ paddingHorizontal: 12, paddingVertical: 6 }}
					>
						<Text style={{ color: "#b00020", fontWeight: "700" }}>Logout</Text>
					</TouchableOpacity>
				</View>
			),
		});
	}, [navigation]);

	const load = useCallback(async () => {
		setError(null);
		const data = await fetchDashboardVideos();
		setItems(data.items ?? []);
	}, []);

	useEffect(() => {
		(async () => {
			try {
				await load();
			} catch (e) {
				setError(e?.response?.data?.error ?? "Failed to load dashboard");
			} finally {
				setLoading(false);
			}
		})();
	}, [load]);

	const onRefresh = useCallback(async () => {
		setRefreshing(true);
		try {
			await load();
		} catch (e) {
			setError(e?.response?.data?.error ?? "Failed to refresh");
		} finally {
			setRefreshing(false);
		}
	}, [load]);

	const onPressItem = (item) => {
		navigation.navigate("VideoPlayer", { video: item });
	};

	if (loading) return <Loader />;

	return (
		<SafeAreaView style={{ flex: 1 }}>
			<View style={{ padding: 16, flex: 1 }}>
				{error ? (
					<Text style={{ color: "#b00020", marginBottom: 12 }}>{error}</Text>
				) : null}

				<FlatList
					data={items}
					keyExtractor={(item) => item.id}
					renderItem={({ item }) => <VideoTile item={item} onPress={onPressItem} />}
					refreshControl={
						<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
					}
					ListEmptyComponent={
						<Text style={{ color: "#666" }}>No videos available.</Text>
					}
				/>
			</View>
		</SafeAreaView>
	);
}

