import { useState } from "react"
import { StyleSheet, ScrollView, Image, TouchableOpacity, Alert, Modal, TextInput } from "react-native"
import { Text, View } from "@/components/Themed"
import Colors from "@/constants/Colors"
import { useColorScheme } from "react-native"
import { requestResume } from "@/services/api"
import { Ionicons } from "@expo/vector-icons"

export default function PortfolioScreen() {
  const colorScheme = useColorScheme() ?? "light"
  const [email, setEmail] = useState("")
  const [modalVisible, setModalVisible] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleRequestResume = async () => {
    if (!email || !email.includes("@")) {
      Alert.alert("Invalid Email", "Please enter a valid email address to receive the link.")
      return
    }

    setLoading(true)
    try {
      await requestResume(email)
      setSuccess(true)
      setModalVisible(false)
    } catch (error) {
      Alert.alert("Error", "Failed to send request. Is the server running?")
    } finally {
      setLoading(false)
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
        <Text style={styles.sectionTitle}>Resume Download</Text>
        {!success ? (
          <TouchableOpacity
            style={[styles.downloadButton, { backgroundColor: Colors[colorScheme].tint }]}
            onPress={() => setModalVisible(true)}
          >
            <Ionicons name="document-text-outline" size={20} color="#fff" />
            <Text style={styles.buttonText}>Request Resume Link</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.statusBox}>
            <Ionicons name="mail-unread-outline" size={24} color="#22c55e" />
            <Text style={[styles.statusText, { color: "#22c55e" }]}>Email Sent!</Text>
            <Text style={styles.subStatusText}>Please check your inbox (and spam) for the secure download link.</Text>
            <TouchableOpacity onPress={() => setSuccess(false)} style={{ marginTop: 10 }}>
              <Text style={{ color: Colors[colorScheme].tint, fontSize: 12 }}>Send to another email?</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colorScheme === 'dark' ? '#1e293b' : '#fff' }]}>
            <Text style={styles.modalTitle}>Where should I send the link?</Text>
            <Text style={styles.modalSub}>Enter your professional email to receive a secure, one-time download link.</Text>

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
                <Text style={styles.confirmText}>{loading ? "Sending..." : "Send Link"}</Text>
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
