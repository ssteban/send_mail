from .connection import ConnectionSendEmail
from typing import Dict, Any
from datetime import datetime, timezone

class QuerySendEmail:
    def __init__(self) -> None:
        """Inicializa la clase de consultas con la conexión a Supabase."""
        self.connection = ConnectionSendEmail()
        self.supabase = self.connection.get_supabase()

    def get_email_access_token(self, email: str) -> dict:
        """Obtiene todas las partes del token de acceso para un correo específico.

        Args:
            email (str): El correo electrónico del usuario (usuario_id en la tabla).

        Returns:
            dict: Un diccionario con toda la información del token.
        """
        response = (
            self.supabase.table("tokens_email")
            .select(
                "access_token, refresh_token, token_uri, client_id, client_secret, scopes, expiry"
            )
            .eq("usuario_id", email)
            .single()
            .execute()
        )
        return response.data

    def update_email_access_token(
        self, email: str, update_data: Dict[str, Any]
    ) -> None:
        """Actualiza campos específicos del token para un correo.

        Args:
            email (str): El correo electrónico del usuario a actualizar.
            update_data (Dict[str, Any]): Un diccionario con los campos a actualizar.
        """
        # Añade el campo updated_at automáticamente
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        (
            self.supabase.table("tokens_email")
            .update(update_data)
            .eq("usuario_id", email)
            .execute()
        )