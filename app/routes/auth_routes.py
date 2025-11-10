from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from ..db.query import QuerySendEmail
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timezone

router = APIRouter()
load_dotenv()

CLIENT_SECRET_JSON = json.loads(os.getenv("CLIENT_SECRET_JSON"))
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]
REDIRECT_URI = "https://send-mail-0ruj.onrender.com/auth/callback"

# Inicializa el flujo OAuth2
def build_flow():
    return Flow.from_client_config(
        CLIENT_SECRET_JSON,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

@router.get("/google")
async def auth_google():
    """
    Genera la URL de autenticación de Google y redirige al usuario
    directamente a ella.
    """
    flow = build_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def auth_callback(request: Request):
    """Recibe el código de Google, intercambia por tokens y guarda en Supabase."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Falta el parámetro 'code' en la URL")

    flow = build_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials

    # Extrae información relevante decodificando y verificando el id_token
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        id_info = id_token.verify_oauth2_token(
            credentials.id_token, google_requests.Request(), credentials.client_id
        )
        user_email = id_info.get("email")

    except ValueError as e:
        # Esto puede ocurrir si el token es inválido
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

    if not user_email:
        raise HTTPException(status_code=400, detail="No se pudo obtener el correo del usuario del token.")

    token_data = {
        "usuario_id": user_email,
        "provider": "google",
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": datetime.fromtimestamp(credentials.expiry.timestamp(), tz=timezone.utc).isoformat(),
    }

    # Guarda en Supabase
    db = QuerySendEmail()
    db.supabase.table("tokens_email").upsert(token_data).execute()

    return {"message": f"Usuario {user_email} registrado correctamente."}


