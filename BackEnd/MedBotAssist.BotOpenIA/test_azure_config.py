"""
Script de prueba para verificar la configuración de Azure Storage
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar configuración
azure_conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
auto_vectorize = os.getenv("AUTO_VECTORIZE_ON_STARTUP")
blob_base_url = os.getenv("BLOB_STORAGE_BASE_URL")
container_name = os.getenv("BLOB_CONTAINER_NAME")

print("=== VERIFICACIÓN DE CONFIGURACIÓN AZURE ===")
print(f"AZURE_STORAGE_CONNECTION_STRING: {'✅ Configurado' if azure_conn_str else '❌ No configurado'}")
print(f"AUTO_VECTORIZE_ON_STARTUP: {auto_vectorize}")
print(f"BLOB_STORAGE_BASE_URL: {blob_base_url}")
print(f"BLOB_CONTAINER_NAME: {container_name}")

# Probar la importación de Azure SDK
try:
    from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
    print("✅ Azure Storage SDK disponible")
    
    if azure_conn_str:
        try:
            # Probar crear cliente
            blob_service_client = BlobServiceClient.from_connection_string(azure_conn_str)
            print("✅ BlobServiceClient creado exitosamente")
            print(f"Account name: {blob_service_client.account_name}")
            
        except Exception as e:
            print(f"❌ Error creando BlobServiceClient: {e}")
    else:
        print("❌ No se puede probar la conexión sin connection string")
        
except ImportError as e:
    print(f"❌ Azure Storage SDK no disponible: {e}")

print("=== FIN DE VERIFICACIÓN ===")
