
import React, { useEffect, useState } from "react";
import { Alert, SafeAreaView, Text, TouchableOpacity, View } from "react-native";

import Loader from "../components/Loader";
import { me } from "../api/auth.api";
import { clearSession } from "../storage/tokenStorage";

export default function SettingsScreen({ navigation }) {
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const [user, setUser] = useState(null);

	useEffect(() => {
		let mounted = true;
		(async () => {
			setLoading(true);
			setError(null);
			try {
				const data = await me();
				if (mounted) setUser(data?.user ?? null);
			} catch (e) {
				const msg = e?.response?.data?.error ?? e?.message ?? "Failed to load profile";
				if (mounted) setError(msg);
			} finally {
				if (mounted) setLoading(false);
			}
		})();
		return () => {
			mounted = false;
		};
	}, []);

	const handleLogout = () => {
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
	};

	if (loading) return <Loader />;

	return (
		<SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
			<View style={{ padding: 16, flex: 1, gap: 12 }}>
				<Text style={{ fontSize: 22, fontWeight: "800" }}>Settings</Text>

				{error ? <Text style={{ color: "#b00020" }}>{error}</Text> : null}

				<View
					style={{
						padding: 16,
						borderRadius: 12,
						backgroundColor: "#f3f4f6",
						gap: 8,
					}}
				>
					<Text style={{ fontWeight: "800", fontSize: 16 }}>Profile</Text>
					<Text style={{ color: "#111827" }}>
						Name: <Text style={{ fontWeight: "700" }}>{user?.name || "-"}</Text>
					</Text>
					<Text style={{ color: "#111827" }}>
						Email: <Text style={{ fontWeight: "700" }}>{user?.email || "-"}</Text>
					</Text>
				</View>

				<TouchableOpacity
					onPress={handleLogout}
					style={{
						marginTop: 8,
						paddingVertical: 12,
						borderRadius: 10,
						backgroundColor: "#b00020",
					}}
				>
					<Text style={{ color: "#fff", textAlign: "center", fontWeight: "800" }}>
						Logout
					</Text>
				</TouchableOpacity>
			</View>
		</SafeAreaView>
	);
}

