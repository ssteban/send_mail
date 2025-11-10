from fastapi import APIRouter, HTTPException
from ..models.models import EmailRequest
from ..service.send_correo import send_email

router = APIRouter()

@router.get("/status")
async def read_status():
    return {"status": "ok"}

@router.post("/send-email")
async def send_email_endpoint(email_request: EmailRequest):
    try:
        response = send_email(
            remitente=email_request.remitente,
            destinatario=email_request.destinatario,
            asunto=email_request.asunto,
            mensaje=email_request.mensaje,
            es_html=email_request.es_html
        )
        return {"message": "Correo enviado exitosamente", "details": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error envindo correo: {str(e)}")


