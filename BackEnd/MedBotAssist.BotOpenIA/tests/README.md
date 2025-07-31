# Tests

Esta carpeta contiene todos los archivos de prueba para el proyecto MedBot Assistant.

## Estructura de Tests

### 📋 Tests Principales
- **`test_blob_service.py`** - Pruebas para integración con Azure Blob Storage
- **`test_vectorization.py`** - Pruebas para funcionalidad de vectorización de documentos

### 🔧 Tests de Herramientas
- **`test_diagnosis_search_tools.py`** - Pruebas para herramientas de búsqueda de diagnósticos
- **`test_medical_history_tools.py`** - Pruebas para herramientas de historial médico
- **`test_use_agent_permission.py`** - Pruebas para sistema de permisos del agente

### 🏗️ Tests de Arquitectura
- **`test_complete_update.py`** - Pruebas de actualización completa del sistema
- **`test_import_structure.py`** - Validación de estructura de importaciones
- **`test_modular_structure.py`** - Pruebas de arquitectura modular
- **`test_normalization.py`** - Pruebas de normalización de datos

## Cómo Ejecutar las Pruebas

### Ejecutar una prueba individual
```bash
# Desde la raíz del proyecto
python -m tests.test_blob_service
python -m tests.test_vectorization
```

### Ejecutar todas las pruebas con pytest
```bash
# Instalar pytest si no lo tienes
pip install pytest

# Ejecutar todas las pruebas
pytest tests/

# Ejecutar con output detallado
pytest tests/ -v

# Ejecutar una prueba específica
pytest tests/test_vectorization.py -v
```

### Ejecutar pruebas desde VS Code
1. Abrir la Command Palette (`Ctrl+Shift+P`)
2. Seleccionar "Python: Configure Tests"
3. Elegir "pytest"
4. Seleccionar la carpeta `tests`

## Requisitos para las Pruebas

Algunas pruebas requieren configuración adicional:

### test_blob_service.py
- Token SAS válido para el contenedor de Azure Blob Storage
- Acceso a la cuenta de almacenamiento `strmedbotassist`

### test_vectorization.py
- API key de OpenAI configurada
- ChromaDB instalado
- Dependencias de procesamiento de documentos (PyPDF2, python-docx, etc.)

## Configuración de Variables de Entorno

Asegúrate de que tu archivo `.env` contenga:
```env
OPENAI_API_KEY=tu_api_key_aqui
BLOB_STORAGE_BASE_URL=https://strmedbotassist.blob.core.windows.net
BLOB_CONTAINER_NAME=instructions-files
```

## Notas

- Los archivos están organizados por funcionalidad
- Todos los tests incluyen logging detallado para facilitar el debugging
- Los tests pueden ejecutarse independientemente o como suite completa
- Se recomienda ejecutar los tests antes de hacer deploy a producción
