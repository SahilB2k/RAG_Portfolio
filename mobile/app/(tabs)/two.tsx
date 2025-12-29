import { useState, useEffect, useRef } from "react"
import { StyleSheet, ScrollView, Image, TouchableOpacity, Alert, Modal, TextInput, ActivityIndicator, Linking } from "react-native"
import { Text, View } from "@/components/Themed"
import Colors from "@/constants/Colors"
import { useColorScheme } from "react-native"
import { requestResume, checkAccessStatus, getDownloadUrl } from "@/services/api"
import { Ionicons } from "@expo/vector-icons"

export default function PortfolioScreen() {
  const colorScheme = useColorScheme() ?? "light"
  const [email, setEmail] = useState("")
  const [modalVisible, setModalVisible] = useState(false)
  const [loading, setLoading] = useState(false)
  const [accessPending, setAccessPending] = useState(false)
  const [accessApproved, setAccessApproved] = useState(false)
  const [accessToken, setAccessToken] = useState<string | null>(null)

  const pollInterval = useRef<any>(null)

  // System Internal: resume_access_control polling
  useEffect(() => {
    if (accessPending && accessToken && !accessApproved) {
      pollInterval.current = setInterval(async () => {
        const status = await checkAccessStatus(accessToken)
        if (status === 'approved') {
          setAccessApproved(true)
          setAccessPending(false)
          if (pollInterval.current) clearInterval(pollInterval.current)
        }
      }, 5000) // Poll every 5s
    }

    return () => {
      if (pollInterval.current) clearInterval(pollInterval.current)
    }
  }, [accessPending, accessToken, accessApproved])

  const handleRequestResume = async () => {
    if (!email || !email.includes("@")) {
      Alert.alert("Invalid Email", "Please enter a valid professional email address.")
      return
    }

    setLoading(true)
    try {
      const response = await requestResume(email)
      if (response.token) {
        setAccessToken(response.token)
        setAccessPending(true)
        setModalVisible(false)
      }
    } catch (error: any) {
      const msg = error.response?.data?.message || "Internal system error. Please try again later."
      Alert.alert("Notice", msg)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (accessToken) {
      const url = getDownloadUrl(accessToken)
      const supported = await Linking.canOpenURL(url)
      if (supported) {
        await Linking.openURL(url)
        // Reset state after attempted download as it's single-use
        setAccessApproved(false)
        setAccessPending(false)
        setAccessToken(null)
      } else {
        Alert.alert("Error", "Can't open download link.")
      }
    }
  }

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
        <Text style={styles.sectionTitle}>Resume Access</Text>

        {!accessPending && !accessApproved && (
          <TouchableOpacity
            style={[styles.downloadButton, { backgroundColor: Colors[colorScheme].tint }]}
            onPress={() => setModalVisible(true)}
          >
            <Ionicons name="shield-checkmark-outline" size={20} color="#fff" />
            <Text style={styles.buttonText}>Request Access</Text>
          </TouchableOpacity>
        )}

        {accessPending && (
          <View style={[styles.statusBox, { borderColor: Colors[colorScheme].tint }]}>
            <ActivityIndicator size="small" color={Colors[colorScheme].tint} />
            <Text style={[styles.statusText, { color: Colors[colorScheme].tint }]}>Request is being processed</Text>
            <Text style={styles.subStatusText}>Resume access will be enabled shortly.</Text>
            <Text style={styles.momentText}>This may take a moment...</Text>
            <Text style={[styles.disclaimerText, { marginTop: 8 }]}>This helps ensure availability and prevent misuse.</Text>
          </View>
        )}

        {accessApproved && (
          <View style={styles.statusBox}>
            <Ionicons name="lock-open-outline" size={24} color="#22c55e" />
            <Text style={[styles.statusText, { color: "#22c55e" }]}>Access Enabled</Text>
            <TouchableOpacity
              style={[styles.downloadButton, { backgroundColor: "#22c55e", width: '100%' }]}
              onPress={handleDownload}
            >
              <Ionicons name="cloud-download-outline" size={20} color="#fff" />
              <Text style={styles.buttonText}>Download Resume Now</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      <Modal
        animationType="fade"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colorScheme === 'dark' ? '#1e293b' : '#fff' }]}>
            <Text style={styles.modalTitle}>Resume Access Control</Text>
            <Text style={styles.modalSub}>Please enter your professional email to initiate the access verification workflow.</Text>

            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colorScheme === 'dark' ? '#0f172a' : '#f8fafc',
                  color: colorScheme === 'dark' ? '#fff' : '#000',
                  borderColor: Colors[colorScheme].border
                }
              ]}
              placeholder="recruiter@company.com"
              placeholderTextColor="#94a3b8"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoFocus={true}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton, { backgroundColor: Colors[colorScheme].tint }]}
                onPress={handleRequestResume}
                disabled={loading}
              >
                <Text style={styles.confirmText}>{loading ? "Processing..." : "Initiate Request"}</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

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
    borderColor: "#22c55e",
    marginTop: 10,
    backgroundColor: "rgba(34, 197, 94, 0.05)",
  },
  statusText: {
    fontSize: 16,
    fontWeight: "700",
    marginTop: 8,
  },
  subStatusText: {
    fontSize: 12,
    opacity: 0.6,
    marginTop: 4,
    textAlign: "center",
  },
  momentText: {
    fontSize: 12,
    opacity: 0.5,
    fontStyle: "italic",
    marginTop: 4,
  },
  disclaimerText: {
    fontSize: 10,
    color: "#94a3b8",
    fontStyle: "italic",
    textAlign: "center",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    padding: 20,
  },
  modalContent: {
    borderRadius: 20,
    padding: 25,
    elevation: 5,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '800',
    marginBottom: 8,
  },
  modalSub: {
    fontSize: 14,
    opacity: 0.6,
    marginBottom: 20,
    lineHeight: 20,
  },
  input: {
    height: 50,
    borderRadius: 12,
    paddingHorizontal: 15,
    fontSize: 16,
    borderWidth: 1,
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  modalButton: {
    flex: 1,
    height: 50,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButton: {
    backgroundColor: 'transparent',
  },
  confirmButton: {
    shadowColor: "#6366f1",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 8,
  },
  cancelText: {
    fontWeight: '600',
    color: '#94a3b8',
  },
  confirmText: {
    fontWeight: '700',
    color: '#fff',
  },
})
