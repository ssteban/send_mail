from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    remitente: EmailStr
    destinatario: EmailStr
    asunto: str
    mensaje: str
    es_html: bool = False  # si viene True, el cuerpo se interpretará como HTML
