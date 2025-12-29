import { useState, useEffect } from "react"
import { StyleSheet, ScrollView, Image, TouchableOpacity, Linking, Alert } from "react-native"
import { Text, View } from "@/components/Themed"
import Colors from "@/constants/Colors"
import { useColorScheme } from "react-native"
import { requestResume, checkRequestStatus, getDownloadUrl } from "@/services/api"
import { Ionicons } from "@expo/vector-icons"

export default function PortfolioScreen() {
  const colorScheme = useColorScheme() ?? "light"
  const [requestId, setRequestId] = useState<string | null>(null)
  const [status, setStatus] = useState<"none" | "pending" | "approved">("none")
  const [loading, setLoading] = useState(false)

  const handleRequestResume = async () => {
    setLoading(true)
    try {
      const data = await requestResume()
      setRequestId(data.request_id)
      setStatus("pending")
      Alert.alert("Request Sent", "Sahil has been notified. You can download the resume once he approves it.")
    } catch (error) {
      Alert.alert("Error", "Failed to send request. Is the server running?")
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (requestId && status === "approved") {
      Linking.openURL(getDownloadUrl(requestId))
    }
  }

  // Poll for status if pending
  useEffect(() => {
    let interval: any
    if (requestId && status === "pending") {
      interval = setInterval(async () => {
        try {
          const data = await checkRequestStatus(requestId)
          if (data.status === "approved") {
            setStatus("approved")
            clearInterval(interval)
            Alert.alert("Approved!", "Sahil has approved your request. You can now download the resume.")
          }
        } catch (error) {
          console.error("Polling error:", error)
        }
      }, 5000) // Check every 5 seconds
    }
    return () => interval && clearInterval(interval)
  }, [requestId, status])

  return (
    <ScrollView style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <View style={styles.header}>
        <Image
          source={{ uri: "https://avatar.iran.liara.run/public/boy?username=Sahil" }}
          style={styles.profileImage}
        />
        <Text style={styles.name}>Sahil Jadhav</Text>
        <Text style={styles.title}>AI/ML Engineer & Full Stack Developer</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Resume Download</Text>
        {status === "none" ? (
          <TouchableOpacity
            style={[styles.downloadButton, { backgroundColor: Colors[colorScheme].tint }]}
            onPress={handleRequestResume}
            disabled={loading}
          >
            <Ionicons name="document-text-outline" size={20} color="#fff" />
            <Text style={styles.buttonText}>{loading ? "Sending Request..." : "Request Resume Download"}</Text>
          </TouchableOpacity>
        ) : status === "pending" ? (
          <View style={styles.statusBox}>
            <Ionicons name="timer-outline" size={24} color="#f59e0b" />
            <Text style={styles.statusText}>Request Pending Approval...</Text>
            <Text style={styles.subStatusText}>Sahil will receive an email to approve this.</Text>
          </View>
        ) : (
          <TouchableOpacity
            style={[styles.downloadButton, { backgroundColor: "#22c55e" }]}
            onPress={handleDownload}
          >
            <Ionicons name="download-outline" size={20} color="#fff" />
            <Text style={styles.buttonText}>Download Resume Now</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About Me</Text>
        <Text style={styles.bio}>
          Passionate about building AI-driven applications and solving complex problems with clean code.
          Expertise in Python, React, and Large Language Models.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Top Skills</Text>
        <View style={styles.skillsContainer}>
          {["Python", "React Native", "RAG", "LLMs", "Docker"].map((skill) => (
            <View key={skill} style={[styles.skillBadge, { backgroundColor: Colors[colorScheme].tint }]}>
              <Text style={styles.skillText}>{skill}</Text>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    alignItems: "center",
    padding: 30,
    backgroundColor: "transparent",
  },
  profileImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 16,
    borderWidth: 3,
    borderColor: "#6366f1",
  },
  name: {
    fontSize: 24,
    fontWeight: "800",
  },
  title: {
    fontSize: 16,
    opacity: 0.6,
    marginTop: 4,
  },
  section: {
    padding: 20,
    backgroundColor: "transparent",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 10,
  },
  bio: {
    fontSize: 15,
    lineHeight: 22,
    opacity: 0.8,
  },
  skillsContainer: {
    flexDirection: "row" as "row",
    flexWrap: "wrap" as "wrap",
    gap: 10,
    backgroundColor: "transparent",
  },
  skillBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  skillText: {
    color: "#fff",
    fontSize: 13,
    fontWeight: "600",
  },
  downloadButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 15,
    borderRadius: 12,
    gap: 10,
    marginTop: 10,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
  },
  statusBox: {
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderStyle: "dashed",
    borderColor: "#f59e0b",
    marginTop: 10,
    backgroundColor: "rgba(245, 158, 11, 0.05)",
  },
  statusText: {
    fontSize: 16,
    fontWeight: "700",
    color: "#f59e0b",
    marginTop: 8,
  },
  subStatusText: {
    fontSize: 12,
    opacity: 0.6,
    marginTop: 4,
    textAlign: "center",
  },
})
