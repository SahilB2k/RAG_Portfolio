import { Tabs } from "expo-router"
import { Ionicons } from "@expo/vector-icons"
import { useColorScheme } from "react-native"
import Colors from "@/constants/Colors"

export default function TabLayout() {
  const colorScheme = useColorScheme() ?? "light"

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme].tint,
        tabBarStyle: {
          backgroundColor: Colors[colorScheme].background,
          borderTopColor: Colors[colorScheme].border,
          elevation: 0,
          shadowOpacity: 0,
          height: 60,
          paddingBottom: 10,
        },
        headerStyle: {
          backgroundColor: Colors[colorScheme].background,
          elevation: 0,
          shadowOpacity: 0,
          borderBottomWidth: 1,
          borderBottomColor: Colors[colorScheme].border,
        },
        headerTitleStyle: {
          fontWeight: "800",
          color: Colors[colorScheme].text,
          fontSize: 18,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Chat with Sahil",
          tabBarLabel: "Chat",
          tabBarIcon: ({ color }) => <Ionicons name="chatbubble-ellipses" size={24} color={color} />,
        }}
      />
      <Tabs.Screen
        name="two"
        options={{
          title: "Portfolio",
          tabBarLabel: "Profile",
          tabBarIcon: ({ color }) => <Ionicons name="person" size={24} color={color} />,
        }}
      />
    </Tabs>
  )
}
