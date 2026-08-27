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
# Model Definitions (Updated & Crash-Proof)
# ─────────────────────────────────────────────
GEMINI_MODEL = "gemini-1.5-flash"
GROQ_MODELS = ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama3-8b-8192"]

# ─────────────────────────────────────────────
# AI Client Setup
# ─────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_KEYS = [k.strip() for k in os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", "")).split(",") if k.strip()]
_groq_key_cycle = itertools.cycle(GROQ_KEYS) if GROQ_KEYS else iter([])

def _get_groq_client():
    if not GROQ_KEYS:
        raise ValueError("No Groq API keys configured")
    return Groq(api_key=next(_groq_key_cycle))

def _call_gemini(messages: list, max_tokens: int = 1500) -> str:
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
    if GEMINI_KEY:
        try:
            return _call_gemini(messages, max_tokens)
        except Exception as e:
            print(f"[Gemini error, falling back to Groq]: {e}")

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
    return "⚠️ Server busy hai. Please thodi der baad dobara try karein."

def _stream_ai(messages: list, max_tokens: int = 1500):
    """Generator: Safely streams from Gemini, falls back to Groq models, prevents ASGI crashes."""
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
                print(f"[Groq stream model '{model}' error]: {e}")
                continue

    yield "⚠️ Server busy hai. Please thodi der baad dobara try karein."

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
# Pydantic Schemas
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
# Helper Functions
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
        raise HTTPException(status_code=401, detail="Invalid teacher key.")

async def _build_system(slug: str, user_msg: str, quiz_mode: bool = False) -> str:
    cfg = _subject_cfg(slug)
    context = search(slug, user_msg, top_k=5)

    curriculum_block = ""
    if context:
        curriculum_block = f"\n\nTEACHER'S CURRICULUM:\n{context}\n"

    practical_block = ""
    if _is_practical_request(user_msg):
        practical_block = "\n⚠️ PRACTICAL TASK DETECTED: Guide step-by-step. Do not do complete task for them.\n"

    viva_block = ""
    if _is_viva_question(user_msg) and not quiz_mode:
        viva_block = "\n⚡ VIVA MODE: Direct 1-2 line response only.\n"

    quiz_block = ""
    if quiz_mode:
        quiz_block = "\n🎯 VIVA QUIZ MODE: Ask practical questions 1 by 1 and evaluate.\n"

    return EDUCATOR_PERSONA.format(**cfg) + curriculum_block + practical_block + viva_block + quiz_block

# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@router.get("/viva/questions")
async def viva_questions(x_subject_id: str = Header(default="it-101")):
    cfg = _subject_cfg(x_subject_id)
    context = search(x_subject_id, "practical task steps shortcut formula menu path", top_k=10)
    curriculum_note = f"\nCurriculum:\n{context}" if context else ""
    
    prompt = f"Prepare 15 practical viva questions with 1-line answers for {cfg['subject_name']}.{curriculum_note}"
    result = _call_ai([{"role": "user", "content": prompt}], max_tokens=1500)
    return {"subject": x_subject_id, "questions": result}

@router.post("/chat")
async def chat_stream(
    req: ChatRequest,
    x_subject_id: str = Header(default="it-101"),
    x_quiz_mode: str = Header(default="false"),
):
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
    session_id = req.session_id or "anon"
    history = get_history(session_id)
    system = await _build_system(x_subject_id, req.message)
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": req.message}]
    reply = _call_ai(messages, max_tokens=1500)
    save_exchange(session_id, req.message, reply)
    return {"reply": reply, "subject": x_subject_id, "session_id": session_id}

@router.delete("/chat/session/{session_id}")
async def clear_student_session(session_id: str):
    clear_session(session_id)
    return {"cleared": True, "session_id": session_id}

@router.post("/curriculum/upload")
async def upload_text(
    req: CurriculumTextRequest,
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    _verify_teacher_key(x_teacher_key)
    doc = add_document(x_subject_id, req.title, req.content, req.doc_type)
    return {"status": "uploaded", "subject": x_subject_id, "doc_id": doc["id"]}

@router.post("/curriculum/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str = Form(default="lecture"),
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    _verify_teacher_key(x_teacher_key)
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files allowed.")
    raw = await file.read()
    content = raw.decode("utf-8", errors="ignore")
    doc = add_document(x_subject_id, title, content, doc_type)
    return {"status": "uploaded", "filename": file.filename, "doc_id": doc["id"]}

@router.get("/curriculum")
async def list_docs(
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    _verify_teacher_key(x_teacher_key)
    return {"subject": x_subject_id, "documents": list_documents(x_subject_id)}

@router.delete("/curriculum/{doc_id}")
async def delete_doc(
    doc_id: str,
    x_subject_id: str = Header(default="it-101"),
    x_teacher_key: Optional[str] = Header(default=None),
):
    _verify_teacher_key(x_teacher_key)
    if not delete_document(x_subject_id, doc_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"deleted": True, "doc_id": doc_id}

@router.post("/subjects")
async def create_subject(
    req: SubjectRequest,
    x_teacher_key: Optional[str] = Header(default=None),
):
    _verify_teacher_key(x_teacher_key)
    SUBJECTS[req.slug] = {
        "subject_name": req.subject_name,
        "teacher_name": req.teacher_name,
        "persona_name": req.persona_name or "EduMentor",
    }
    return {"status": "created", "slug": req.slug}

@router.get("/subjects")
async def get_subjects():
    return {
        "subjects": [
            {"slug": k, "subject_name": v["subject_name"], "teacher_name": v["teacher_name"]}
            for k, v in SUBJECTS.items()
        ]
    }

@router.get("/stats")
async def stats(x_teacher_key: Optional[str] = Header(default=None)):
    _verify_teacher_key(x_teacher_key)
    return {"active_sessions": session_count(), "subjects": len(SUBJECTS)}
