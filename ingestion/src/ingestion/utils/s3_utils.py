import boto3
import os
import shutil
import time
from botocore.exceptions import ClientError, EndpointConnectionError
from tqdm import tqdm

session = boto3.Session(region_name="us-east-2")
s3_client = boto3.client("s3")
BUCKET_NAME = "bucket01-labex"

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

def upload_file_to_s3(local_path, s3_key, max_retries=3):
    """
    Sube un archivo local a un bucket S3 (si no existe ya) con reintento
    """
    if not os.path.exists(local_path):
        print(f"⚠️ No existe local: {local_path}")
        return False

    if object_exists(BUCKET_NAME, s3_key):
        print(f"⏭️ Ya existe en S3 (omitido): s3://{BUCKET_NAME}/{s3_key}")
        return True

    filesize = os.path.getsize(local_path)
    
    for attempt in range(1, max_retries + 1):
        try:
            with tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Subiendo {s3_key}") as pbar:
                def upload_progress(chunk):
                    pbar.update(chunk)

                s3_client.upload_file(
                    local_path,
                    BUCKET_NAME,
                    s3_key,
                    Callback=upload_progress
                )

            print(f"✅ Subido a s3://{BUCKET_NAME}/{s3_key}")
            return True  # Éxito

        except (ClientError, EndpointConnectionError) as e:
            print(f"⚡ [{attempt}/{max_retries}] Error subiendo {local_path}: {e}")

            if attempt < max_retries:
                print("⏳ Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                print("❌ Fallo definitivo después de varios intentos.")
                return False

def upload_folder_to_s3(local_folder, s3_prefix, cleanup=True):
    """
    Sube recursivamente todos los archivos de una carpeta a S3.
    Solo limpia local si todo se subió correctamente.
    """
    total_files = sum(len(files) for _, _, files in os.walk(local_folder))
    success_files = 0

    print(f"📦 Subiendo {total_files} archivos desde {local_folder} a s3://{BUCKET_NAME}/{s3_prefix}")

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_folder)
            s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")

            if upload_file_to_s3(local_file_path, s3_key):
                success_files += 1

    if success_files == total_files and cleanup:
        print(f"✅ Todos los archivos ({total_files}) fueron subidos exitosamente. Procediendo a limpieza...")
        cleanup_local_folder(local_folder)
    else:
        print(f"⚠️ Solo {success_files}/{total_files} archivos subidos. NO se limpiará la carpeta local para no perder datos.")

def cleanup_local_folder(local_folder):
    """
    Borra la carpeta local especificada y su contenido
    """
    if os.path.exists(local_folder):
        shutil.rmtree(local_folder)
        print(f"🗑️ Carpeta local eliminada: {local_folder}")
    else:
        print(f"⚠️ Carpeta no encontrada para eliminar: {local_folder}")
