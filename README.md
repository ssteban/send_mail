# Servicio de Envío de Correos Multi-Cuenta

Este proyecto es un microservicio construido con FastAPI que proporciona una API para enviar correos electrónicos a través de la API de Gmail. Soporta múltiples cuentas de remitentes gracias a un sistema de autenticación dinámico con OAuth2 y almacenamiento de tokens en Supabase.

## Características

- **API para Envío de Correos**: Endpoint simple para enviar correos electrónicos.
- **Soporte Multi-Cuenta**: Envía correos desde cualquier cuenta de Gmail registrada en el sistema.
- **Autenticación con OAuth2**: Flujo completo para que los usuarios autoricen a la aplicación de forma segura.
- **Gestión Dinámica de Tokens**:
  - Almacena las credenciales de cada usuario en una base de datos Supabase.
  - Refresca automáticamente los `access_token` expirados usando los `refresh_token`.
  - Persiste los tokens actualizados en la base de datos para optimizar peticiones futuras.
- **Seguro**: Carga de configuraciones y credenciales a través de variables de entorno.

---

## Configuración del Entorno

### 1. Prerrequisitos

- Python 3.9+
- Una cuenta de Google y un proyecto en [Google Cloud Console](https://console.cloud.google.com/) con la API de Gmail habilitada.
- Una cuenta y un proyecto en [Supabase](https://supabase.com/).

### 2. Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # En Windows: .venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Variables de Entorno

Crea un archivo llamado `.env` en la raíz del proyecto y añade las siguientes variables:

```ini
# Credenciales de tu proyecto de Supabase
SUPER_URL="https://tu-id-de-proyecto.supabase.co"
SUPER_KEY="tu-llave-anon-o-service-role"

# Contenido completo del archivo client_secret.json de Google Cloud
# Asegúrate de que esté en una sola línea o formatea el JSON correctamente si tu sistema lo permite.
CLIENT_SECRET_JSON='{"web":{"client_id":"TU_CLIENT_ID.apps.googleusercontent.com","project_id":"tu-project-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"TU_CLIENT_SECRET","redirect_uris":["http://localhost:8000/auth/callback"]}}'

# URL de redirección (debe coincidir con una de las configuradas en Google Cloud)
REDIRECT_URI="http://localhost:8000/auth/callback"
```

### 4. Base de Datos

En tu instancia de Supabase, ejecuta la siguiente consulta SQL para crear la tabla necesaria:

```sql
CREATE TABLE tokens_email (
  id SERIAL PRIMARY KEY,
  usuario_id VARCHAR(255) NOT NULL UNIQUE, -- correo o identificador del usuario
  provider VARCHAR(50) NOT NULL,         -- 'google', 'outlook', etc.
  access_token TEXT NOT NULL,
  refresh_token TEXT NOT NULL,
  token_uri TEXT NOT NULL,
  client_id TEXT NOT NULL,
  client_secret TEXT NOT NULL,
  scopes TEXT[],
  expiry TIMESTAMP,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---


## Uso de la API

### 1. Iniciar el Servidor

```bash
uvicorn app.main:app --reload
```
El servicio estará disponible en `http://localhost:8000`.

### 2. Registrar una Nueva Cuenta de Correo

1.  Abre tu navegador y ve a:
    `http://localhost:8000/auth/google`

2.  Serás redirigido a la página de consentimiento de Google. Inicia sesión y autoriza los permisos.

3.  Tras la autorización, serás redirigido de vuelta a la aplicación, y tus credenciales quedarán guardadas en la base de datos.

### 3. Enviar un Correo

Realiza una petición `POST` al endpoint `/service/send-email`.

**Ejemplo con `curl`:**

```bash
curl -X 'POST' \
  'http://localhost:8000/service/send-email' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d 
'{
  "remitente": "tu-email-registrado@gmail.com",
  "destinatario": "email-destino@example.com",
  "asunto": "Prueba desde la API",
  "mensaje": "Este es un correo de prueba.",
  "es_html": false
}'
```

---


## Endpoints de la API

- `GET /`: Mensaje de bienvenida.
- `GET /auth/google`: Inicia el flujo de autenticación de Google.
- `GET /auth/callback`: Endpoint de redirección para que Google complete la autenticación.
- `GET /service/status`: Verifica que el servicio de envío esté activo.
- `POST /service/send-email`: Envía un correo.
  - **Body**:
    - `remitente` (str, email): La cuenta de Gmail registrada que enviará el correo.
    - `destinatario` (str, email): El destinatario del correo.
    - `asunto` (str): El asunto del correo.
    - `mensaje` (str): El cuerpo del correo.
    - `es_html` (bool, opcional): `true` si el cuerpo es HTML. Por defecto es `false`.

