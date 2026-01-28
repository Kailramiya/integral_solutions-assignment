
import React, { useState } from "react";
import {
	SafeAreaView,
	Text,
	TextInput,
	TouchableOpacity,
	View,
} from "react-native";

import { login } from "../api/auth.api";
import { setAccessToken, setRefreshToken } from "../storage/tokenStorage";
import { getApiErrorMessage } from "../utils/apiError";

export default function LoginScreen({ navigation }) {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [showPassword, setShowPassword] = useState(false);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	const onSubmit = async () => {
		setError(null);
		setLoading(true);
		try {
			const data = await login({ email, password });
			await setAccessToken(data.access_token);
			await setRefreshToken(data.refresh_token);
			navigation.reset({ index: 0, routes: [{ name: "Dashboard" }] });
		} catch (e) {
			setError(getApiErrorMessage(e, "Login failed"));
		} finally {
			setLoading(false);
		}
	};

	return (
		<SafeAreaView style={{ flex: 1 }}>
			<View style={{ padding: 16, flex: 1, justifyContent: "center" }}>
				<Text style={{ fontSize: 24, fontWeight: "700", marginBottom: 16 }}>
					Login
				</Text>
				{error ? <Text style={{ color: "#b00020" }}>{error}</Text> : null}

				<TextInput
					value={email}
					onChangeText={setEmail}
					placeholder="Email"
					autoCapitalize="none"
					keyboardType="email-address"
					style={{
						borderWidth: 1,
						borderColor: "#ddd",
						borderRadius: 10,
						padding: 12,
						marginTop: 12,
					}}
				/>
				<View style={{ marginTop: 12 }}>
					<TextInput
						value={password}
						onChangeText={setPassword}
						placeholder="Password"
						autoCapitalize="none"
						secureTextEntry={!showPassword}
						style={{
							borderWidth: 1,
							borderColor: "#ddd",
							borderRadius: 10,
							padding: 12,
							paddingRight: 72,
						}}
					/>
					<TouchableOpacity
						onPress={() => setShowPassword((v) => !v)}
						style={{
							position: "absolute",
							right: 12,
							top: 0,
							bottom: 0,
							justifyContent: "center",
						}}
					>
						<Text style={{ color: "#2563eb", fontWeight: "600" }}>
							{showPassword ? "Hide" : "Show"}
						</Text>
					</TouchableOpacity>
				</View>

				<TouchableOpacity
					onPress={onSubmit}
					disabled={loading}
					style={{
						backgroundColor: "#111827",
						padding: 14,
						borderRadius: 10,
						marginTop: 16,
						opacity: loading ? 0.7 : 1,
					}}
				>
					<Text style={{ color: "#fff", textAlign: "center", fontWeight: "600" }}>
						{loading ? "Signing in..." : "Login"}
					</Text>
				</TouchableOpacity>

				<TouchableOpacity
					onPress={() => navigation.navigate("Signup")}
					style={{ padding: 12, marginTop: 12 }}
				>
					<Text style={{ textAlign: "center", color: "#2563eb" }}>
						Create an account
					</Text>
				</TouchableOpacity>
			</View>
		</SafeAreaView>
	);
}

