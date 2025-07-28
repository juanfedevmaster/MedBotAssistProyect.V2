# MedBot Assistant API

API para asistente médico con agentes IA y consultas SQL directas.

## Estructura del Proyecto

```
MedBotAssist.BotOpenIA/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── medical_query_agent.py    # Agente principal médico
│   │   └── tools.py                  # Herramientas del agente
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── agent.py             # Endpoints del agente
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                # Configuración de la aplicación
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py              # Modelos de base de datos
│   │   └── schemas.py               # Modelos Pydantic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database_service.py      # Servicio de base de datos SQL
│   │   └── vectorization_service.py # Servicio simplificado (solo SQL)
│   └── __init__.py
├── main.py                          # Aplicación FastAPI principal
├── server.py                        # Script para despliegue
├── startup.sh                       # Script de inicio para Azure
├── runtime.txt                      # Versión de Python para Azure
├── requirements.txt                 # Dependencias
├── .env.example                     # Ejemplo de variables de entorno
└── README.md                        # Este archivo
```

## Configuración

1. **Copia el archivo de variables de entorno:**
   ```bash
   copy .env.example .env
   ```

2. **Configura tu API key de OpenAI en el archivo `.env`:**
   ```
   OPENAI_API_KEY=tu_api_key_aqui
   ```

3. **Configura las credenciales de la base de datos SQL Server (opcional):**
   ```
   DB_SERVER=tu_servidor.database.windows.net
   DB_DATABASE=tu_base_de_datos
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   ```

4. **Configura el backend externo para gestión de pacientes:**
   ```
   EXTERNAL_BACKEND_API_URL=http://localhost:5098/api/
   ```

5. **Configura las credenciales JWT:**
   ```
   JWT_SECRET=tu_secreto_jwt
   JWT_ISSUER=MedBotAssist
   JWT_AUDIENCE=MedBotAssistUsers
   JWT_EXPIRATION_MINUTES=60
   ```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

### Opción 1: Usando el script principal
```bash
python main.py
```

### Opción 2: Usando uvicorn directamente
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 3: Para despliegue (Azure)
```bash
python server.py
```

## Endpoints Disponibles

### 📊 Documentación Automática
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 🤖 Endpoints del Agente Médico

#### Chat con el Agente
- **POST** `/api/v1/agent/chat` - Conversar con el agente médico
- **GET** `/api/v1/agent/tools` - Listar herramientas disponibles del agente
- **POST** `/api/v1/agent/health` - Estado del agente médico

#### Gestión de Conversaciones
- **GET** `/api/v1/agent/conversation/{id}` - Obtener historial de conversación
- **DELETE** `/api/v1/agent/conversation/{id}` - Limpiar historial de conversación

## Herramientas del Agente

El agente médico tiene acceso a las siguientes herramientas:

### 🔍 Búsqueda de Pacientes
- **search_patients** - Búsqueda general por consulta natural
- **search_patients_by_name** - Búsqueda por nombre con normalización
- **filter_patients_by_demographics** - Filtros por edad, email, año de nacimiento
- **get_patient_by_id** - Detalles completos solo con IdentificationNumber

### 📊 Estadísticas
- **get_patients_summary** - Resumen estadístico (solo conteos, sin detalles)

### 📞 Búsqueda por Contacto
- **search_patients_by_condition** - Buscar por información de contacto

### ➕ Gestión de Pacientes
- **create_patient** - Crear nuevos pacientes en el sistema externo
  - **Requiere permiso:** ManagePatients
  - **Backend externo:** Consume API en `EXTERNAL_BACKEND_API_URL`
  - **Endpoint:** POST `/api/Patient/create`
  - **Autenticación:** JWT token del usuario actual
- **update_patient** - Actualizar información de pacientes existentes
  - **Requiere permiso:** ManagePatients
  - **Backend externo:** Consume API en `EXTERNAL_BACKEND_API_URL`
  - **Endpoint:** PUT `/api/Patient/update-patient`
  - **Autenticación:** JWT token del usuario actual

## Ejemplo de Uso

### Conversar con el agente:
```json
POST /api/v1/agent/chat
{
  "message": "Busca pacientes con el apellido García",
  "conversation_id": "conv_123"
}
```

### Crear un nuevo paciente:
```json
POST /api/v1/agent/chat
{
  "message": "Crea un nuevo paciente con el nombre 'Juanfe Test', identificación '123456789', fecha de nacimiento '2020-07-27T22:25:33.321Z', edad 25, teléfono '3004441111' y email 'juanfe.test2@gmail.com'",
  "conversation_id": "conv_456"
}
```

### Actualizar un paciente existente:
```json
POST /api/v1/agent/chat
{
  "message": "Actualiza el paciente con identificación '123456789', cambia su email a 'nuevo.email@gmail.com' y su teléfono a '+57-301-555-1234'",
  "conversation_id": "conv_789"
}
```

### Respuesta esperada:
```json
{
  "response": "Encontré 3 pacientes con el apellido García:\n\n1. Paciente María García con identificación ID002, 32 años de edad, nacida el 20 de agosto de 1992, teléfono 555-5678, email maria.garcia@email.com\n\n2. Paciente José García López con identificación ID015, 28 años de edad...",
  "conversation_id": "conv_123",
  "agent_used_tools": true,
  "available_tools": ["search_patients", "search_patients_by_name", "get_patients_summary", "filter_patients_by_demographics", "search_patients_by_condition", "get_patient_by_id", "create_patient", "update_patient"],
  "status": "success"
}
```

### Obtener herramientas disponibles:
```bash
GET /api/v1/agent/tools
```

## Funcionalidades Principales

✅ **Consulta directa a SQL Server** - Sin intermediarios, datos en tiempo real  
✅ **Agente conversacional** - Procesamiento de lenguaje natural con OpenAI  
✅ **Búsqueda normalizada** - Encuentra "García" buscando "garcia"  
✅ **Múltiples herramientas** - Búsqueda, filtrado, estadísticas, creación y actualización  
✅ **Integración con backend externo** - Creación y actualización de pacientes via HTTP API  
✅ **Historial de conversaciones** - Mantiene contexto entre consultas  
✅ **API REST completa** - Endpoints documentados y validados  
✅ **Compatible con Azure** - Configurado para App Service  

## Sistema de Seguridad:

- 🔐 Autenticación JWT obligatoria en /api/v1/agent/chat
- 🛡️ Validación de permisos ViewPatients para herramientas de consulta
- 🛡️ Validación de permisos ManagePatients para creación y actualización de pacientes
- 🚫 Mensajes de error personalizados para acceso denegado
- 🔗 Integración con backend externo para operaciones de escritura

## Características de Búsqueda

### 🔤 Normalización de Texto
El sistema normaliza automáticamente las búsquedas para mayor flexibilidad:

- **"sanchez"** → Encuentra **"Sánchez García"**
- **"jose maria"** → Encuentra **"José María"**
- **"PEREZ"** → Encuentra **"Pérez López"**

### 🎯 Tipos de Búsqueda
- **Por nombre completo o parcial**
- **Por información demográfica** (edad, email)
- **Por información de contacto** (teléfono, email)
- **Búsquedas generales** con lenguaje natural

## Gestión de Pacientes

### ➕ Creación de Pacientes
La herramienta `create_patient` permite crear nuevos pacientes a través del agente conversacional:

**Requisitos:**
- Usuario autenticado con JWT token
- Permiso `ManagePatients` en el token
- Backend externo funcionando en `EXTERNAL_BACKEND_API_URL`

**Formato de solicitud:**
```
"Crea un nuevo paciente con el nombre '[NOMBRE]', identificación '[ID]', fecha de nacimiento '[FECHA]', edad [EDAD], teléfono '[TELEFONO]' y email '[EMAIL]'"
```

**Ejemplo:**
```
"Crea un nuevo paciente con el nombre 'Juan Pérez', identificación '12345678', fecha de nacimiento '1990-05-15T00:00:00.000Z', edad 33, teléfono '+57-300-123-4567' y email 'juan.perez@email.com'"
```

**Proceso interno:**
1. Validación de permisos ManagePatients
2. Extracción del JWT token del contexto
3. Construcción del payload JSON
4. Llamada HTTP POST al backend externo
5. Manejo de respuestas (éxito/error)

**Respuestas esperadas:**
- ✅ **200/201:** Paciente creado exitosamente
- ❌ **400:** Error de validación de datos
- ❌ **401:** Token JWT inválido o expirado
- ❌ **403:** Sin permisos ManagePatients
- ❌ **500:** Error del servidor externo

### 🔄 Actualización de Pacientes
La herramienta `update_patient` permite actualizar información de pacientes existentes a través del agente conversacional:

**Requisitos:**
- Usuario autenticado con JWT token
- Permiso `ManagePatients` en el token
- Backend externo funcionando en `EXTERNAL_BACKEND_API_URL`
- Número de identificación del paciente (obligatorio)

**Formato de solicitud:**
```
"Actualiza el paciente con identificación '[ID]', cambia [CAMPO1] a '[VALOR1]', [CAMPO2] a '[VALOR2]'"
```

**Ejemplos:**
```
"Actualiza el paciente con identificación '12345678', cambia su email a 'nuevo@email.com'"
"Actualiza el paciente con identificación '87654321', cambia su nombre a 'María Elena García' y su teléfono a '+57-301-555-9999'"
"Actualiza el paciente con identificación '11223344', cambia su edad a 35 y su fecha de nacimiento a '1988-12-25T00:00:00.000Z'"
```

**Proceso interno:**
1. Validación de permisos ManagePatients
2. Extracción del JWT token del contexto
3. Búsqueda del paciente actual con `get_patient_by_id`
4. Combinación de datos existentes con nuevos valores
5. Llamada HTTP PUT al backend externo
6. Manejo de respuestas (éxito/error)

**Respuestas esperadas:**
- ✅ **200/204:** Paciente actualizado exitosamente
- ❌ **400:** Error de validación de datos
- ❌ **401:** Token JWT inválido o expirado
- ❌ **403:** Sin permisos ManagePatients
- ❌ **404:** Paciente no encontrado
- ❌ **500:** Error del servidor externo

## Arquitectura

### �️ Datos
- **SQL Server** como única fuente de verdad
- **Consultas directas** sin cache ni sincronización
- **Normalización en tiempo real** para búsquedas

### 🤖 Agente IA
- **LangChain** para gestión del agente
- **OpenAI GPT** para procesamiento de lenguaje
- **Herramientas especializadas** para acceso a datos

### 🔐 Seguridad (Preparado para JWT)
- **JWT configurado** para autenticación futura
- **Variables de entorno** para secretos
- **Configuración lista** para autorización por herramientas

## Tecnologías

- **FastAPI** - Framework web moderno
- **Pydantic** - Validación de datos
- **OpenAI** - GPT para conversación
- **LangChain** - Framework para agentes IA
- **SQLAlchemy** - ORM para SQL Server
- **pyodbc** - Driver de base de datos
- **httpx** - Cliente HTTP para integración con backend externo
- **PyJWT** - Procesamiento de tokens JWT

## Despliegue en Azure

El proyecto está configurado para Azure App Service:

1. **startup.sh** - Script de inicialización
2. **server.py** - Servidor para producción  
3. **runtime.txt** - Especifica Python 3.11.12
4. **requirements.txt** - Todas las dependencias

## Corrección de errores:

En los archivos criticos los app services en el formato Unix debe ser (\n). 
En caso de fallar debes correr estos scripts:

# Convertir startup.sh
(Get-Content startup.sh -Raw) -replace "`r`n", "`n" | Set-Content startup.sh -NoNewline

# Convertir requirements.txt  
(Get-Content requirements.txt -Raw) -replace "`r`n", "`n" | Set-Content requirements.txt -NoNewline

# Convertir server.py
(Get-Content server.py -Raw) -replace "`r`n", "`n" | Set-Content server.py -NoNewline

# Convertir runtime.txt
(Get-Content runtime.txt -Raw) -replace "`r`n", "`n" | Set-Content runtime.txt -NoNewline
