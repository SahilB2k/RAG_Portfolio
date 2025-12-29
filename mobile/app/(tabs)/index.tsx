"use client"

import { useState, useRef, useEffect } from "react"
import {
  StyleSheet,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Image,
  useColorScheme,
  Animated,
} from "react-native"

import { Text, View } from "@/components/Themed"
import { askStreamingQuestion } from "@/services/api"
import { Ionicons } from "@expo/vector-icons"
import Colors from "@/constants/Colors"

interface Message {
  id: string
  text: string
  sender: "user" | "ai"
  metadata?: {
    confidence: number
    [key: string]: any
  }
}

export default function ChatScreen() {
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Hey there! I'm Sahil's digital twin. 🚀 Ask me anything about my projects, skills, or even my favorite stack!",
      sender: "ai",
    },
  ])
  const [loading, setLoading] = useState(false)
  const flatListRef = useRef<FlatList>(null)
  const colorScheme = useColorScheme() ?? "light"

  // Animation for the "typing" indicator
  const fadeAnim = useRef(new Animated.Value(0)).current

  useEffect(() => {
    if (loading) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
          Animated.timing(fadeAnim, { toValue: 0, duration: 500, useNativeDriver: true }),
        ]),
      ).start()
    } else {
      fadeAnim.setValue(0)
    }
  }, [loading])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMsg: Message = { id: Date.now().toString(), text: input, sender: "user" }
    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setLoading(true)

    const aiMsgId = (Date.now() + 1).toString()
    const aiMsg: Message = { id: aiMsgId, text: "", sender: "ai" }
    setMessages((prev) => [...prev, aiMsg])

    try {
      await askStreamingQuestion(
        input,
        (chunk) => {
          setMessages((prev) => prev.map((msg) => (msg.id === aiMsgId ? { ...msg, text: msg.text + chunk } : msg)))
        },
        (metadata) => {
          setMessages((prev) => prev.map((msg) => (msg.id === aiMsgId ? { ...msg, metadata } : msg)))
        },
      )
    } catch (error) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMsgId
            ? { ...msg, text: "Ouch! My digital brain is a bit fuzzy right now. Check if Sahil's server is awake! 😴" }
            : msg,
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  const renderMessage = ({ item }: { item: Message }) => {
    const isUser = item.sender === "user"
    return (
      <View style={[styles.messageWrapper, isUser ? styles.userWrapper : styles.aiWrapper]}>
        {!isUser && (
          <View style={styles.avatarContainer}>
            <Image source={{ uri: "https://avatar.iran.liara.run/public/boy?username=Sahil" }} style={styles.avatar} />
          </View>
        )}
        <View
          style={[
            styles.messageBubble,
            isUser ? styles.userBubble : styles.aiBubble,
            { backgroundColor: isUser ? Colors[colorScheme].bubbleUser : Colors[colorScheme].bubbleAI },
            { borderColor: Colors[colorScheme].border },
          ]}
        >
          <Text style={[styles.messageText, { color: isUser ? "#fff" : Colors[colorScheme].text }]}>{item.text}</Text>
          {item.metadata?.confidence && (
            <Text style={[styles.metadataText, { color: isUser ? "rgba(255,255,255,0.7)" : Colors[colorScheme].text }]}>
              Confidence: {Math.round(item.metadata.confidence * 100)}%
            </Text>
          )}
        </View>
      </View>
    )
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}
      keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={renderMessage}
        contentContainerStyle={styles.chatList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
        onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {loading && (
        <Animated.View style={[styles.typingContainer, { opacity: fadeAnim }]}>
          <Text style={styles.typingText}>Sahil is typing...</Text>
        </Animated.View>
      )}

      <View style={styles.disclaimerContainer}>
        <Text style={styles.disclaimerText}>
          My brain is slow since I was born just now... Please be patient! 👶
        </Text>
      </View>

      <View
        style={[
          styles.inputArea,
          { borderTopColor: Colors[colorScheme].border, backgroundColor: Colors[colorScheme].background },
        ]}
      >
        <TextInput
          style={[
            styles.input,
            {
              backgroundColor: colorScheme === "dark" ? "#1e293b" : "#f1f5f9",
              color: Colors[colorScheme].text,
            },
          ]}
          placeholder="Message Sahil..."
          placeholderTextColor={colorScheme === "dark" ? "#94a3b8" : "#64748b"}
          value={input}
          onChangeText={setInput}
          multiline
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            { backgroundColor: Colors[colorScheme].tint },
            (!input.trim() || loading) && styles.sendButtonDisabled,
          ]}
          onPress={handleSend}
          disabled={!input.trim() || loading}
        >
          <Ionicons name="arrow-up" size={24} color="#fff" />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  chatList: {
    padding: 16,
    paddingBottom: 24,
  },
  messageWrapper: {
    marginBottom: 16,
    flexDirection: "row",
    alignItems: "flex-end",
    maxWidth: "85%",
  },
  userWrapper: {
    alignSelf: "flex-end",
    justifyContent: "flex-end",
  },
  aiWrapper: {
    alignSelf: "flex-start",
  },
  avatarContainer: {
    marginRight: 8,
    marginBottom: 2,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "#e2e8f0",
  },
  messageBubble: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 22,
    borderWidth: 1,
  },
  userBubble: {
    backgroundColor: "#6366f1",
    borderBottomRightRadius: 4,
    borderColor: "#6366f1",
  },
  aiBubble: {
    backgroundColor: "transparent",
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  metadataText: {
    fontSize: 10,
    marginTop: 4,
    opacity: 0.5,
    fontStyle: "italic",
    textAlign: "right",
  },
  typingContainer: {
    paddingHorizontal: 20,
    paddingVertical: 8,
  },
  typingText: {
    fontSize: 12,
    color: "#94a3b8",
    fontStyle: "italic",
  },
  inputArea: {
    flexDirection: "row",
    alignItems: "flex-end",
    padding: 12,
    paddingBottom: Platform.OS === "ios" ? 30 : 12,
    borderTopWidth: 1,
  },
  input: {
    flex: 1,
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 16,
    marginRight: 10,
    maxHeight: 120,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  disclaimerContainer: {
    alignItems: "center",
    paddingVertical: 5,
    backgroundColor: "transparent",
  },
  disclaimerText: {
    fontSize: 10,
    color: "#94a3b8",
    fontStyle: "italic",
    textAlign: "center",
  },
})
