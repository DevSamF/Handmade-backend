import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header
import os

cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def verify_token(id_token: str = Header(...)):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token["uid"]  # Este é o localId do Firebase
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")
