import { StyleSheet, ScrollView, Image } from "react-native"
import { Text, View } from "@/components/Themed"
import Colors from "@/constants/Colors"
import { useColorScheme } from "react-native"

export default function PortfolioScreen() {
  const colorScheme = useColorScheme() ?? "light"

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
    flexDirection: "row",
    flexWrap: "wrap",
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
})
