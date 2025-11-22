import boto3
import shutil
import time
from pathlib import Path
from botocore.exceptions import ClientError, EndpointConnectionError
from tqdm import tqdm
from dotenv import load_dotenv
import os

# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=env_path)

# Get AWS configuration from environment variables
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "bucket01-labex")

# Validate that required AWS credentials are set
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("⚠️  WARNING: AWS credentials not found in environment variables.")
    print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file or environment.")
    print("   S3 uploads will fail without proper credentials.")

# Create boto3 session and client
session = boto3.Session(
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3_client = session.client("s3")

def object_exists(bucket, key):
    """
    Verifica si un objeto ya existe en S3
    """
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise

def upload_file_to_s3(local_path, s3_key, max_retries=3, bucket_name=None):
    """
    Sube un archivo local a un bucket S3 (si no existe ya) con reintento
    
    Args:
        local_path: Ruta local del archivo (str o Path)
        s3_key: Clave S3 destino
        max_retries: Número máximo de reintentos
        bucket_name: Nombre del bucket (usa BUCKET_NAME por defecto)
    """
    bucket = bucket_name or BUCKET_NAME
    
    # Convert to string if Path object
    local_path = str(local_path) if isinstance(local_path, Path) else local_path
    
    if not os.path.exists(local_path):
        print(f"⚠️ No existe local: {local_path}")
        return False

    if object_exists(bucket, s3_key):
        print(f"⏭️ Ya existe en S3 (omitido): s3://{bucket}/{s3_key}")
        return True

    filesize = os.path.getsize(local_path)
    
    for attempt in range(1, max_retries + 1):
        try:
            with tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Subiendo {s3_key}") as pbar:
                def upload_progress(chunk):
                    pbar.update(chunk)

                s3_client.upload_file(
                    local_path,
                    bucket,
                    s3_key,
                    Callback=upload_progress
                )

            print(f"✅ Subido a s3://{bucket}/{s3_key}")
            return True  # Éxito

        except (ClientError, EndpointConnectionError) as e:
            print(f"⚡ [{attempt}/{max_retries}] Error subiendo {local_path}: {e}")

            if attempt < max_retries:
                print("⏳ Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                print("❌ Fallo definitivo después de varios intentos.")
                return False

def upload_folder_to_s3(local_folder, s3_prefix, cleanup=True, bucket_name=None):
    """
    Sube recursivamente todos los archivos de una carpeta a S3.
    Solo limpia local si todo se subió correctamente.
    
    Args:
        local_folder: Ruta local de la carpeta (str o Path)
        s3_prefix: Prefijo S3 destino
        cleanup: Si True, elimina la carpeta local después de subir
        bucket_name: Nombre del bucket (usa BUCKET_NAME por defecto)
    """
    bucket = bucket_name or BUCKET_NAME
    
    # Convert to string if Path object
    local_folder = str(local_folder) if isinstance(local_folder, Path) else local_folder
    
    total_files = sum(len(files) for _, _, files in os.walk(local_folder))
    success_files = 0

    print(f"📦 Subiendo {total_files} archivos desde {local_folder} a s3://{bucket}/{s3_prefix}")

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_folder)
            s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")

            if upload_file_to_s3(local_file_path, s3_key, bucket_name=bucket):
                success_files += 1

    if success_files == total_files and cleanup:
        print(f"✅ Todos los archivos ({total_files}) fueron subidos exitosamente. Procediendo a limpieza...")
        cleanup_local_folder(local_folder)
    else:
        print(f"⚠️ Solo {success_files}/{total_files} archivos subidos. NO se limpiará la carpeta local para no perder datos.")

def cleanup_local_folder(local_folder):
    """
    Borra la carpeta local especificada y su contenido
    
    Args:
        local_folder: Ruta local de la carpeta (str o Path)
    """
    # Convert to string if Path object
    local_folder = str(local_folder) if isinstance(local_folder, Path) else local_folder
    
    if os.path.exists(local_folder):
        shutil.rmtree(local_folder)
        print(f"🗑️ Carpeta local eliminada: {local_folder}")
    else:
        print(f"⚠️ Carpeta no encontrada para eliminar: {local_folder}")
