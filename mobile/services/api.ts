import axios from 'axios';

// IMPORTANT: Replace this with your computer's local IP address (e.g., 192.168.1.X)
// so that a physical mobile device can connect to the local backend.
// if you are using an Android emulator, 10.0.2.2 usually works.
const BASE_URL = 'https://rag-portfolio-mvjo.onrender.com';

export function askStreamingQuestion(
  question: string,
  onChunk: (chunk: string) => void,
  onMetadata?: (metadata: any) => void,
) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${BASE_URL}/ask`);
    xhr.setRequestHeader('Content-Type', 'application/json');

    let lastIndex = 0;

    xhr.onreadystatechange = () => {
      if (xhr.readyState === 3 || xhr.readyState === 4) {
        const currentResponse = xhr.responseText;
        const newChunks = currentResponse.substring(lastIndex);
        lastIndex = currentResponse.length;

        const lines = newChunks.split('\n');
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            if (data.answer_chunk) {
              onChunk(data.answer_chunk);
            }
            if (data.metadata && onMetadata) {
              onMetadata(data.metadata);
            }
          } catch (e) {
            // Partial JSON - common during streaming
          }
        }

        if (xhr.readyState === 4) {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(true);
          } else {
            reject(new Error(`API Error: ${xhr.status}`));
          }
        }
      }
    };

    xhr.onerror = () => reject(new Error('Network error'));
    xhr.send(JSON.stringify({ question }));
  });
}

export async function askQuestion(question: string) {
  try {
    const response = await axios.post(`${BASE_URL}/ask_sync`, {
      question: question,
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
