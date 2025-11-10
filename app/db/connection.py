import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPER_URL")
key = os.getenv("SUPER_KEY")


class ConnectionSendEmail:
    def __init__(self) -> None:
        """Inicializa la conexión con Supabase usando las variables de entorno."""
        if not url or not key:
            raise ValueError("⚠️ No se encontraron las variables SUPER_URL o SUPER_KEY en el entorno.")
        self.supabase: Client = create_client(url, key)

    def get_supabase(self) -> Client:
        """Devuelve el cliente de Supabase activo."""
        return self.supabase

    def test_connection(self) -> bool:
        """Verifica si la conexión con Supabase funciona correctamente."""
        try:
            data = self.supabase.table("tokens_email").select("id").limit(1).execute()
            print(f"✅ Conexión exitosa con Supabase {data}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar con Supabase: {e}")
            return False
