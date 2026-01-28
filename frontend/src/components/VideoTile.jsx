
import React from "react";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";

export default function VideoTile({ item, onPress }) {
	return (
		<Pressable style={styles.card} onPress={() => onPress?.(item)}>
			<Image source={{ uri: item.thumbnail_url }} style={styles.thumb} />
			<View style={styles.meta}>
				<Text style={styles.title} numberOfLines={1}>
					{item.title}
				</Text>
				<Text style={styles.desc} numberOfLines={2}>
					{item.description}
				</Text>
			</View>
		</Pressable>
	);
}

const styles = StyleSheet.create({
	card: {
		flexDirection: "row",
		padding: 12,
		borderRadius: 12,
		backgroundColor: "#fff",
		marginBottom: 12,
		borderWidth: 1,
		borderColor: "#eee",
	},
	thumb: {
		width: 96,
		height: 64,
		borderRadius: 10,
		backgroundColor: "#f2f2f2",
	},
	meta: {
		flex: 1,
		marginLeft: 12,
	},
	title: {
		fontSize: 16,
		fontWeight: "600",
	},
	desc: {
		marginTop: 4,
		fontSize: 13,
		color: "#555",
	},
});

