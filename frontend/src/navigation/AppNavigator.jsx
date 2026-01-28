
import React, { useEffect, useState } from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import DashboardScreen from "../screens/DashboardScreen";
import LoginScreen from "../screens/LoginScreen";
import SettingsScreen from "../screens/SettingsScreen";
import SignupScreen from "../screens/SignupScreen";
import VideoPlayerScreen from "../screens/VideoPlayerScreen";
import { getAccessToken } from "../storage/tokenStorage";
import Loader from "../components/Loader";

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
	const [isLoading, setIsLoading] = useState(true);
	const [hasToken, setHasToken] = useState(false);

	useEffect(() => {
		let mounted = true;
		(async () => {
			try {
				const token = await getAccessToken();
				if (mounted) setHasToken(Boolean(token));
			} finally {
				if (mounted) setIsLoading(false);
			}
		})();
		return () => {
			mounted = false;
		};
	}, []);

	if (isLoading) return <Loader />;

	return (
		<Stack.Navigator
			key={hasToken ? "auth" : "guest"}
			initialRouteName={hasToken ? "Dashboard" : "Login"}
		>
			<Stack.Screen name="Login" component={LoginScreen} />
			<Stack.Screen name="Signup" component={SignupScreen} />
			<Stack.Screen
				name="Dashboard"
				component={DashboardScreen}
				options={{ headerBackVisible: false }}
			/>
			<Stack.Screen
				name="VideoPlayer"
				component={VideoPlayerScreen}
				options={{ title: "Video" }}
			/>
			<Stack.Screen name="Settings" component={SettingsScreen} />
		</Stack.Navigator>
	);
}

