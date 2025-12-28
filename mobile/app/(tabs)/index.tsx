import React, { useState, useRef } from 'react';
import {
  StyleSheet,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Animated
} from 'react-native';

import { Text, View } from '@/components/Themed';
import { askQuestion, askStreamingQuestion } from '@/services/api';
import { Ionicons } from '@expo/vector-icons';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  metadata?: any;
}

export default function ChatScreen() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: "Hello! I'm Sahil's Digital Twin. Ask me anything about his projects, skills, or experience.", sender: 'ai' }
  ]);
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { id: Date.now().toString(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const aiMsgId = (Date.now() + 1).toString();
    const aiMsg: Message = { id: aiMsgId, text: '', sender: 'ai' };
    setMessages(prev => [...prev, aiMsg]);

    try {
      await askStreamingQuestion(
        input,
        (chunk) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMsgId ? { ...msg, text: msg.text + chunk } : msg
            )
          );
        },
        (metadata) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMsgId ? { ...msg, metadata } : msg
            )
          );
        }
      );
    } catch (error) {
      setMessages(prev =>
        prev.map(msg =>
          msg.id === aiMsgId
            ? { ...msg, text: "Sorry, I'm having trouble connecting to the brain right now. Please check if the backend is running." }
            : msg
        )
      );
    } finally {
      setLoading(false);
      setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View style={[
      styles.messageWrapper,
      item.sender === 'user' ? styles.userWrapper : styles.aiWrapper
    ]}>
      <View style={[
        styles.messageBubble,
        item.sender === 'user' ? styles.userBubble : styles.aiBubble
      ]}>
        <Text style={styles.messageText}>{item.text}</Text>
      </View>
      {item.metadata && (
        <View style={styles.metadataRow}>
          <Text style={styles.confidenceText}>Confidence: {item.metadata.confidence}</Text>
        </View>
      )}
    </View>
  );

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
      keyboardVerticalOffset={100}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Sahil's RAG Bot</Text>
        <View style={styles.onlineBadge}>
          <View style={styles.onlineDot} />
          <Text style={styles.onlineText}>Online</Text>
        </View>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={item => item.id}
        renderItem={renderMessage}
        contentContainerStyle={styles.chatList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      <View style={styles.inputArea}>
        <TextInput
          style={styles.input}
          placeholder="Ask about Sahil's resume..."
          placeholderTextColor="#666"
          value={input}
          onChangeText={setInput}
          multiline
        />
        <TouchableOpacity
          style={[styles.sendButton, (!input.trim() || loading) && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={!input.trim() || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Ionicons name="send" size={20} color="#fff" />
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    backgroundColor: '#1e293b',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#f8fafc',
  },
  onlineBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#22c55e',
    marginRight: 6,
  },
  onlineText: {
    fontSize: 12,
    color: '#22c55e',
    fontWeight: '600',
  },
  chatList: {
    padding: 20,
    paddingBottom: 40,
  },
  messageWrapper: {
    marginBottom: 20,
    maxWidth: '85%',
  },
  userWrapper: {
    alignSelf: 'flex-end',
  },
  aiWrapper: {
    alignSelf: 'flex-start',
  },
  messageBubble: {
    padding: 14,
    borderRadius: 20,
  },
  userBubble: {
    backgroundColor: '#3b82f6',
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    backgroundColor: '#1e293b',
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: '#334155',
  },
  messageText: {
    color: '#f8fafc',
    fontSize: 15,
    lineHeight: 22,
  },
  inputArea: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    paddingBottom: Platform.OS === 'ios' ? 40 : 16,
    backgroundColor: '#1e293b',
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  input: {
    flex: 1,
    backgroundColor: '#0f172a',
    borderRadius: 24,
    paddingHorizontal: 20,
    paddingVertical: 10,
    color: '#f8fafc',
    fontSize: 15,
    marginRight: 10,
    maxHeight: 100,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#3b82f6',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
  },
  sendButtonDisabled: {
    backgroundColor: '#64748b',
    opacity: 0.5,
  },
  metadataRow: {
    marginTop: 6,
    paddingHorizontal: 10,
  },
  confidenceText: {
    fontSize: 11,
    color: '#94a3b8',
    fontStyle: 'italic',
  }
});
