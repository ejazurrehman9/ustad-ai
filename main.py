from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from app.chat import router
from app.seed import seed_it_curriculum


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_it_curriculum()
    print("✅ Ustad AI ready.")
    yield
    print("Ustad AI shutting down.")


app = FastAPI(
    title="Ustad AI API",
    description="Ustad AI — powered by teacher's own curriculum",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def student_ui():
    return FileResponse("static/index.html")


@app.get("/teacher")
async def teacher_ui():
    return FileResponse("static/teacher.html")


@app.get("/health")
async def health():
    return {"status": "ok", "message": "Ustad AI chal raha hai!"}
