from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from cloudinary_utils import upload_image
from database import SessionLocal, Base, engine
from models import Post, Comment
import shutil
import os
import json
import firebase_admin
from firebase_admin import credentials

# Inicialização do Firebase Admin com variável de ambiente segura
if not firebase_admin._apps:
    cred_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not cred_json:
        raise ValueError("Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS_JSON não encontrada.")
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Configuração da API
Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/post/")
def create_post(user_id: str = Form(...), caption: str = Form(...), image: UploadFile = File(...)):
    db = SessionLocal()

    temp_path = f"temp_{image.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_url = upload_image(temp_path)
    os.remove(temp_path)

    post = Post(user_id=user_id, caption=caption, image_url=image_url)
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"message": "Post criado!", "post_id": post.id, "image_url": image_url}

@app.post("/comment/")
def add_comment(post_id: int = Form(...), user_id: str = Form(...), text: str = Form(...)):
    db = SessionLocal()
    comment = Comment(post_id=post_id, user_id=user_id, text=text)
    db.add(comment)
    db.commit()
    return {"message": "Comentário adicionado"}

@app.get("/posts/")
def list_posts():
    db = SessionLocal()
    posts = db.query(Post).all()
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "caption": p.caption,
            "image_url": p.image_url,
            "comments": [{"user_id": c.user_id, "text": c.text} for c in p.comments]
        }
        for p in posts
    ]
