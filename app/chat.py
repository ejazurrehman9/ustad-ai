import os
import asyncio
import itertools
from fastapi import APIRouter, Header, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq
import groq as groq_module
import google.generativeai as genai

from app.persona import EDUCATOR_PERSONA
from app.rag import add_document, search, list_documents, delete_document
from app.session import get_history, save_exchange, clear_session, session_count

router = APIRouter()

# ─────────────────────────────────────────────
# Model Definitions (Updated for Stability)
# ─────────────────────────────────────────────
GEMINI_MODEL = "gemini-1.5-flash"
GROQ_MODELS = ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768"]

# ─────────────────────────────────────────────
# AI Client Setup — Gemini Primary, Groq Fallback
# ─────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_KEYS = [k.strip() for k in os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", "")).split(",") if k.strip()]
_groq_key_cycle = itertools.cycle(GROQ_KEYS) if GROQ_KEYS else iter([])

def _get_groq_client():
    if not GROQ_KEYS:
        raise ValueError("No Groq API keys configured")
    return Groq(api_key=next(_groq_key_cycle))

def _call_gemini(messages: list, max_tokens: int = 1500) -> str:
    """Call Gemini API using updated model."""
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=next((m["content"] for m in messages if m["role"] == "system"), None)
    )
    history = []
    for m in messages:
        if m["role"] == "system":
            continue
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})

    if not history:
        return ""
    last = history.pop()
    chat = model.start_chat(history=history)
    resp = chat.send_message(last["parts"][0], generation_config={"max_output_tokens": max_tokens})
    return resp.text

def _call_ai(messages: list, max_tokens: int = 1500) -> str:
    """Try Gemini first, fallback to Groq on error."""
    if GEMINI_KEY:
        try:
            return _call_gemini(messages, max_tokens)
        except Exception as e:
            print(f"[Gemini error, falling back to Groq]: {e}")
            
    # Groq fallback
    if GROQ_KEYS:
        for model in GROQ_MODELS:
            try:
                client = _get_groq_client()
                resp = client.chat.completions.create(
                    model=model, max_tokens=max_tokens, messages=messages
                )
                return resp.choices[0].message.content
            except Exception as e:
                print(f"[Groq model {model} error]: {e}")
                continue
    return "⚠️ Abhi server busy hai. Thodi der mein dobara try karein."

def _stream_ai(messages: list, max_tokens: int = 1500):
    """Generator: Try Gemini streaming first, fallback to Groq."""
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=next((m["content"] for m in messages if m["role"] == "system"), None)
            )
            history = []
            for m in messages:
                if m["role"] == "system":
                    continue
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})
            if history:
                last = history.pop()
                chat = model.start_chat(history=history)
                for chunk in chat.send_message(last["parts"][0], stream=True,
                                               generation_config={"max_output_tokens": max_tokens}):
                    if chunk.text:
                        yield chunk.text
                return
        except Exception as e:
            print(f"[Gemini stream error, falling back to Groq]: {e}")

    # Groq fallback with safe loop error catching
    if GROQ_KEYS:
        for model in GROQ_MODELS:
            try:
                client = _get_groq_client()
                s = client.chat.completions.create(
                    model=model, max_tokens=max_tokens, messages=messages, stream=True
                )
                for chunk in s:
                    text = chunk.choices[0].delta.content or ""
                    if text:
                        yield text
                return
            except Exception as e:
                print(f"[Groq stream model {model} error]: {e}")
                continue
                
    yield "⚠️ Abhi server busy hai. Thodi der mein dobara try karein."

# ─────────────────────────────────────────────
# Subject Registry
# ─────────────────────────────────────────────
SUBJECTS: dict = {
    "it-101":   {"subject_name": "Information Technology", "teacher_name": "IT Teacher",       "persona_name": "TechMentor"},
    "cs-201":   {"subject_name": "Computer Science",       "teacher_name": "CS Teacher",       "persona_name": "CodeMentor"},
    "math-101": {"subject_name": "Mathematics",            "teacher_name": "Math Teacher",     "persona_name": "MathMentor"},
    "bio-101":  {"subject_name": "Biology",                "teacher_name": "Biology Teacher",  "persona_name": "BioGuide"},
    "eng-101":  {"subject_name": "English",                "teacher_name": "English Teacher",  "persona_name": "LinguaGuide"},
    "phy-101":  {"subject_name": "Physics",                "teacher_name": "Physics Teacher",  "persona_name": "PhysicsMentor"},
}

PRACTICAL_KEYWORDS = {
    "practical", "task", "assignment", "file", "report", "likh", "bana",
    "karo", "karna", "complete", "submit", "meri", "mera", "do my", "write my",
    "make my", "create my", "finish my",
}

VIVA_KEYWORDS = {
    "viva", "quiz", "short answer", "short question", "one line", "1 line",
    "brief", "briefly", "define", "definition", "what is", "kya hai",
    "kitney", "kitni", "konsi", "konsa", "shortcut", "formula", "types",
    "name the", "list the", "how many", "kitne",
}

# ─────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SubjectRequest(BaseModel):
    slug: str
    subject_name: str
    teacher_name: str
    persona_name: Optional[str] = "EduMentor"

class CurriculumTextRequest(BaseModel):
    title: str
    content: str
    doc_type: Optional[str] = "lecture"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _subject_cfg(slug: str) -> dict:
    return SUBJECTS.get(slug, {
        "subject_name": slug.replace("-", " ").title(),
        "teacher_name": "Your Teacher",
        "persona_name": "EduMentor",
    })

def _is_practical_request(msg: str) -> bool:
    msg_lower = msg.lower()
    return any(kw in msg_lower for kw in PRACTICAL_KEYWORDS)

def _is_viva_question(msg: str) -> bool:
    msg_lower = msg.lower()
    return any(kw in msg_lower for kw in VIVA_KEYWORDS)

def _verify_teacher_key(key: Optional[str]) -> None:
    expected = os.getenv("TEACHER_KEY", "teacher2026")
    if key != expected:
        raise HTTPException(status_code=401, detail="Invalid teacher key. Check x-teacher-key header.")

async def _build_system(slug: str, user_msg: str, quiz_mode: bool = False) -> str:
    cfg = _subject_cfg(slug)
    context = search(slug, user_msg, top_k=5)

    curriculum_block = ""
    if context:
        curriculum_block = f"""

════════════════════════════════════════
TEACHER'S CURRICULUM (use this FIRST):
════════════════════════════════════════
{context}
════════════════════════════════════════
Reference specific chapter or practical numbers when answering.
"""

    practical_block = ""
    if _is_practical_request(user_msg):
        practical_block = """

⚠️ PRACTICAL TASK DETECTED — EXTRA RULES:
The student is asking about a practical task or assignment.
- NEVER write the complete task for them.
- Guide them step-by-step.
- Ask what part they are stuck on.
- Reference the relevant practical number from the curriculum.
"""

    viva_block = ""
    if _is_viva_question(user_msg) and not quiz_mode:
        viva_block = """

⚡ VIVA / QUIZ MODE — STRICT RULES:
The student is asking a viva or short-answer question.
- Answer in MAXIMUM 1-2 lines only. No paragraphs.
- No explanations, no analogies, no extra detail.
- Format: [Answer only] — direct and to the point.
- Examples:
    Q: Page orientation kitney types ki hoti hai?
    A: 2 types: Portrait aur Landscape.

    Q: SUM formula kya hai Excel mein?
    A: =SUM(range) — e.g. =SUM(A1:A10)

    Q: Bold ka shortcut kya hai Word mein?
    A: Ctrl + B

- Do NOT add Knowledge Check at the end in viva mode.
- Do NOT add any extra lines or context.
"""

    quiz_block = ""
    if quiz_mode:
        quiz_block = """

🎯 VIVA QUIZ MODE — YOU ARE THE PRACTICAL EXAMINER:
You are conducting a practical viva exam. Follow these rules STRICTLY:

1. Ask ONE practical question at a time — nothing else.
2. Questions must be PRACTICAL only: shortcuts, menu paths, steps, formula syntax, which tab/button to use.
3. NO theory questions like "define", "what is", "explain".
4. When student answers:
   - ✅ Correct! OR ❌ Wrong! — correct answer in 1 line.
   - Then immediately ask the NEXT question.
5. Keep running score: "Score: X/Y" after each answer.
6. After 10 questions show: "Final Score: X/10" with a short remark.

Good question examples:
  - MS Word mein table insert karne ka shortcut?
  - Excel mein average formula kaise likhain?
  - Print preview kahan se khulta hai?
  - Paragraph indent kaise karein Word mein?
  - Cell merge kaise karein Excel mein?

FORMAT for each turn:
[RESULT + correct answer if wrong]
Score: X/Y

[NEXT PRACTICAL QUESTION]

START: Ask Q1 immediately. No greeting, no explanation.
"""

    return EDUCATOR_PERSONA.format(**cfg) + curriculum_block + practical_block + viva_block + quiz_block

# ─────────────────────────────────────────────
# Student: Chat
# ─────────────────────────────────────────────
@router.get("/viva/questions")
async def viva_questions(x_subject_id: str = Header(default="it-101")):
    """Generate practical viva Q&A list from the uploaded curriculum."""
    cfg = _subject_cfg(x_subject_id)
    context = search(x_subject_id, "practical task steps shortcut formula menu path how to create insert format", top_k=10)

    curriculum_note = f"\nPractical curriculum material:\n{context}" if context else \
        "\nNo curriculum uploaded — use general practical knowledge for this subject."

    prompt = f"""Prepare 15 practical viva voice questions with short answers for {cfg['subject_name']}.
{curriculum_note}

STRICT RULES:
- Questions must be PRACTICAL EXAM style only — NOT theory definitions.
- Ask about: shortcuts, menu paths, steps to do something, formula syntax, which tool/button to use.
- Each answer must be 1 line maximum.
- NO "what is", NO "define", NO "explain" type questions.

Good examples:
  Q: MS Word mein bold karne ka shortcut kya hai?
  A: Ctrl + B

  Q: Excel mein SUM formula kaise likhain?
  A: =SUM(A1:A10)

  Q: Page orientation kahan se change karein?
  A: Layout tab → Orientation → Portrait/Landscape

  Q: MS Word mein header insert kaise karein?
  A: Insert tab → Header → style select karein

Format EXACTLY like this (no extra text, no numbering mistakes):

Q1: [practical question]
A: [1-line answer]

Q2: [practical question]
A: [1-line answer]

...up to Q15."""

    result = _call_ai([{"role": "user", "content": prompt}], max_tokens=1500)
    return {"subject": x_subject_id, "questions": result}

@router.post("/chat")
async def chat_stream(
    req: ChatRequest,
    x_subject_id: str = Header(default="it-101"),
    x_quiz_mode: str = Header(default="false"),
):
    """Streaming chat — student asks, AI answers from teacher's curriculum."""
    session_id = req.session_id or "anon"
    history = get_history(session_id)
    quiz_mode = x_quiz_mode.lower() == "true"
    system = await _build_system(x_subject_id, req.message, quiz_mode)

    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": req.message}]
    full_reply_parts: List[str] = []

    def stream():
        for text in _stream_ai(messages, max_tokens=1500):
            full_reply_parts.append(text)
            yield text

    async def save_after():
        await asyncio.sleep(0.1)
        save_exchange(session_id, req.message, "".join(full_reply_parts))

    response = StreamingResponse(stream(), media_type="text/plain")
    asyncio.create_task(save_after())
    return response

@router.post("/chat/ask")
async def chat_simple(req: ChatRequest, x_subject_id: str = Header(default="it-101")):
    """Non-streaming chat — for WhatsApp or simple integrations."""
    session_id = req.session_id or "anon"
    history = get_history(session_id)
    system = await _build_system(x_subject_id, req.message)
    messages = history + [{"role": "user", "content": req.message}]

    messages = [{"role": "system", "content": system}] + messages
    reply = _call_ai(messages, max_tokens=1500)
    save_exchange(session_id, req.message, reply)
    return {
        "reply": reply,
        "subject": x_subject_id,
        "session_id": session_id,
    }

@router.delete("/chat/session/{session_id}")
async def clear_student_session(session_id: str):
    """Clear a student's conversation history."""
    clear_session(session_id)
    return {"cleared": True, "session_id": session_id}

# ─────────────────────────────────────────────
# Teacher: Curriculum Management (protected)
# ─────────────────────────────────────────────
@router.post("/curriculum/upload")
async def upload_text(
    req: CurriculumTextRequest,
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    """Teacher uploads curriculum text."""
    _verify_teacher_key(x_teacher_key)
    doc = add_document(x_subject_id, req.title, req.content, req.doc_type)
    return {
        "status": "uploaded",
        "subject": x_subject_id,
        "doc_id": doc["id"],
        "title": doc["title"],
        "chunks": doc["chunk_count"],
        "message": f"'{req.title}' added. Students can now ask about it.",
    }

@router.post("/curriculum/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str = Form(default="lecture"),
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    """Teacher uploads a .txt file as curriculum."""
    _verify_teacher_key(x_teacher_key)
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported.")
    raw = await file.read()
    content = raw.decode("utf-8", errors="ignore")
    if len(content.strip()) < 10:
        raise HTTPException(status_code=400, detail="File appears empty.")
    doc = add_document(x_subject_id, title, content, doc_type)
    return {
        "status": "uploaded",
        "filename": file.filename,
        "subject": x_subject_id,
        "doc_id": doc["id"],
        "chunks": doc["chunk_count"],
    }

@router.get("/curriculum")
async def list_docs(
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    """Teacher: list uploaded documents."""
    _verify_teacher_key(x_teacher_key)
    docs = list_documents(x_subject_id)
    return {"subject": x_subject_id, "total": len(docs), "documents": docs}

@router.delete("/curriculum/{doc_id}")
async def delete_doc(
    doc_id: str,
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    """Teacher: delete a document."""
    _verify_teacher_key(x_teacher_key)
    ok = delete_document(x_subject_id, doc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"deleted": True, "doc_id": doc_id}

# ─────────────────────────────────────────────
# Subject Registry
# ─────────────────────────────────────────────
@router.post("/subjects")
async def create_subject(
    req: SubjectRequest,
    x_teacher_key: Optional[str] = Header(default=None),
):
    """Register a new subject."""
    _verify_teacher_key(x_teacher_key)
    SUBJECTS[req.slug] = {
        "subject_name": req.subject_name,
        "teacher_name": req.teacher_name,
        "persona_name": req.persona_name or "EduMentor",
    }
    return {"status": "created", "slug": req.slug}

@router.get("/subjects")
async def get_subjects():
    """List all registered subjects (public)."""
    return {
        "subjects": [
            {"slug": k, "subject_name": v["subject_name"], "teacher_name": v["teacher_name"]}
            for k, v in SUBJECTS.items()
        ]
    }

# ─────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────
@router.get("/stats")
async def stats(x_teacher_key: Optional[str] = Header(default=None)):
    """Basic usage stats for teacher dashboard."""
    _verify_teacher_key(x_teacher_key)
    all_docs = {}
    for slug in SUBJECTS:
        all_docs[slug] = len(list_documents(slug))
    return {
        "active_sessions": session_count(),
        "subjects": len(SUBJECTS),
        "docs_per_subject": all_docs,
    }
