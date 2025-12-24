import subprocess
import os
from app.query_resume import hybrid_search


def clean_text(text: str) -> str:
    return text.encode("utf-8", errors="ignore").decode("utf-8")


def generate_answer(question: str) -> str:
    # 1. Get more chunks (top_k=7) to ensure nothing is missed
    retrieved_chunks = hybrid_search(question, top_k=10)

    # 2. Lower threshold significantly (0.20) for the Librarian
    relevant_text = "\n---\n".join([c[0] for c in retrieved_chunks if c[1] > 0.20])

    if not relevant_text:
        return "I couldn't find a direct match. Could you try rephrasing?"

    prompt = f"""
<|system|>
You are "Sahil's AI Proxy"—a professional, highly intelligent representative of Sahil Jadhav.
Your goal is to answer ANY question an interviewer might ask based on the provided Resume Context.

DATA SCOPE:
- Education (10th, 12th, CGPA, College)
- Technical Skills (Languages, Frameworks, Tools)
- Projects (Detailed descriptions, technologies used, outcomes)
- Certifications & Achievements (NPTEL, Leadership, Hackathons)

INSTRUCTIONS:
1. Scan the entire Context for the answer.
2. If asked about multiple things (e.g., projects AND grades), address BOTH.
3. Use a professional, confident tone as if you are recommending Sahil for a job.
4. If a specific detail (like a exact percentage) is missing, say: "That specific detail isn't in the resume, but Sahil is a [Year] student at [College] with a focus on AI."

FORMATTING RULES:
1. Use a **bulleted list** for projects.
2. For each project, provide a **1-sentence summary** followed by a list of **technologies used**.
3. Be concise. Avoid long paragraphs.
4. If asked about "all projects," ensure every project from the context is included.

Resume Context:
{relevant_text}
<|user|>
Question: {question}
<|assistant|>
"""

    context = "\n---\n".join(chunk for chunk, score , _ in retrieved_chunks)

    if not context:
        return "I'm sorry, I couldn't find that in the resume."


    result = subprocess.run(
        ["ollama", "run", "llama3.2"],
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True,
        env={
            **os.environ,
            "OLLAMA_NUM_CTX": "2048",      # CPU optimized
            "OLLAMA_NUM_THREADS": "6"     # Best for i5-1235U
        }
    )

    return result.stdout.strip()

def generate_answer_with_sources(question: str):
    """
    Streamlit-facing wrapper:
    Returns answer + sources + confidence + total_chunks
    """

    result = generate_answer(question)

    # Defensive defaults to avoid crashes
    answer = result.get("answer", "")
    sources = result.get("sources", [])
    confidence = result.get("confidence", "medium")

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "total_chunks": len(sources)
    }



if __name__ == "__main__":
    question = input("Enter your question about the resume: ")
    print("\n🤖 Answer:\n")
    print(generate_answer(question))
