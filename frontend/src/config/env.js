
import { Platform } from "react-native";

// You can override this at runtime via an Expo public env var:
// - PowerShell: $env:EXPO_PUBLIC_API_BASE_URL="http://<your-lan-ip>:5000"; npx expo start
//
// Defaults:
// - Android emulator -> http://10.0.2.2:5000
// - iOS simulator -> http://localhost:5000
// - Physical device -> http://<your-lan-ip>:5000  (set EXPO_PUBLIC_API_BASE_URL)

const envBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL;

export const API_BASE_URL = "http://192.168.10.16:5000";

