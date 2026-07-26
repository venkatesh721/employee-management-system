import re
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.policy import PolicyDocument, PolicyDocumentChunk
from app.models.user import User

router = APIRouter(prefix="/api/policies", tags=["Policy assistant"])
MAX_SIZE = 2 * 1024 * 1024
ALLOWED = {".txt", ".md"}


class PolicyQuestion(BaseModel):
    question: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_policy(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    suffix = (
        "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    )
    if suffix not in ALLOWED:
        raise HTTPException(422, "Only .txt and .md policy documents are allowed")
    raw = await file.read(MAX_SIZE + 1)
    if len(raw) > MAX_SIZE:
        raise HTTPException(413, "Policy document exceeds the 2 MB limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(422, "Policy document must be UTF-8 text")
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u0080-\uFFFF]", "", text).strip()
    if not text:
        raise HTTPException(422, "Policy document is empty")
    doc = PolicyDocument(name=file.filename, uploaded_by=user.id)
    db.add(doc)
    db.flush()
    chunks = [text[i : i + 1200] for i in range(0, len(text), 1000)]
    for i, content in enumerate(chunks):
        heading = next(
            (
                line.lstrip("# ").strip()
                for line in content.splitlines()
                if line.startswith("#")
            ),
            f"Section {i + 1}",
        )
        db.add(
            PolicyDocumentChunk(
                document_id=doc.id, chunk_index=i, section=heading, content=content
            )
        )
    db.commit()
    return {"id": str(doc.id), "name": doc.name, "chunks": len(chunks)}


@router.post("/ask")
def ask_policy(
    payload: PolicyQuestion,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    terms = {
        w
        for w in re.findall(r"[a-z]{3,}", payload.question.lower())
        if w not in {"what", "when", "where", "which", "does", "this", "that", "policy"}
    }
    scored = []
    for chunk in db.query(PolicyDocumentChunk).all():
        score = sum(term in chunk.content.lower() for term in terms)
        if score:
            scored.append((score, chunk))
    if not scored:
        return {
            "answer": "The requested information is unavailable in the uploaded policies.",
            "sources": [],
            "model_version": "keyword-rag-v1",
        }
    scored.sort(key=lambda item: item[0], reverse=True)
    best = scored[:3]
    answer = " ".join(c.content[:500].strip() for _, c in best)
    docs = {d.id: d.name for d in db.query(PolicyDocument).all()}
    return {
        "answer": answer,
        "sources": [
            {"document": docs.get(c.document_id, "Policy"), "section": c.section}
            for _, c in best
        ],
        "model_version": "keyword-rag-v1",
    }
