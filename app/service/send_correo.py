from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from ..db.query import QuerySendEmail
from dotenv import load_dotenv
from datetime import datetime
import base64


load_dotenv()

def create_message(sender, to, subject, message_text, html=False):
    """Crea un mensaje de correo en el formato requerido por la API de Gmail."""
    if html:
        message = MIMEText(message_text, "html", "utf-8")
    else:
        message = MIMEText(message_text, "plain", "utf-8")
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


def send_email(remitente, destinatario, asunto, mensaje, es_html=False):
    """
    Envía un correo electrónico utilizando las credenciales del remitente almacenadas en la BD.
    Refresca y actualiza el token si es necesario.
    """
    db_query = QuerySendEmail()

    # 1. Obtener el token de la base de datos
    token_data = db_query.get_email_access_token(remitente)
    if not token_data:
        raise Exception(f"No se encontraron credenciales para el remitente: {remitente}")

    # La fecha de expiración de la BD puede ser un string, la convertimos a datetime
    expiry_dt = None
    if token_data.get("expiry"):
        try:
            # Intenta primero formato ISO estándar
            expiry_dt = datetime.fromisoformat(token_data["expiry"])
        except Exception:
            try:
                # Si no es ISO, intenta formato SQL (YYYY-MM-DD HH:MM:SS)
                expiry_dt = datetime.strptime(token_data["expiry"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise Exception("Formato de fecha de expiración inválido en la base de datos.")

    # 2. Crear credenciales a partir de las columnas de la BD
    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"],
        expiry=expiry_dt,
    )

    # 3. Refrescar el token si ha expirado
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # 4. Guardar el nuevo token y la expiración en la base de datos
        update_data = {
            "access_token": creds.token,
            "expiry": creds.expiry.isoformat(),
        }
        db_query.update_email_access_token(remitente, update_data)

    # 5. Construir el servicio de Gmail y enviar el correo
    service = build('gmail', 'v1', credentials=creds)
    
    msg = create_message(remitente, destinatario, asunto, mensaje, html=es_html)
    service.users().messages().send(userId="me", body=msg).execute()
    
    return {"status": "ok", "destinatario": destinatario}

