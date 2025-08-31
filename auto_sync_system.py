#!/usr/bin/env python3
"""
Sistema de Sincronización Automática para Rubio_sync
Actualiza automáticamente los archivos locales en GABINETE2
"""

import os
import requests
import json
import shutil
import hashlib
from datetime import datetime
import logging

# Configuración
RUBIO_SYNC_PATH = "C:\\Rubio_sync"  # Ruta en GABINETE2
DEVELOPMENT_API_URL = "https://dentiflow.preview.emergentagent.com/api"  # URL del entorno de desarrollo
UPDATE_CHECK_URL = f"{DEVELOPMENT_API_URL}/sync/check-updates"
DOWNLOAD_URL = f"{DEVELOPMENT_API_URL}/sync/download-files"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(RUBIO_SYNC_PATH, 'auto_sync.log')),
        logging.StreamHandler()
    ]
)

def check_for_updates():
    """Verifica si hay actualizaciones disponibles"""
    try:
        # Obtener hash actual de archivos locales
        local_hashes = {}
        files_to_check = [
            'sync_modified.py',
            'requirements_sync.txt',
            'service-account-key.json',
            'SETUP_GOOGLE_SERVICE_ACCOUNT.md'
        ]
        
        for filename in files_to_check:
            filepath = os.path.join(RUBIO_SYNC_PATH, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    content = f.read()
                    local_hashes[filename] = hashlib.md5(content).hexdigest()
            else:
                local_hashes[filename] = None
        
        # Consultar servidor para ver si hay nuevas versiones
        response = requests.post(UPDATE_CHECK_URL, json={
            "local_hashes": local_hashes,
            "client_id": "GABINETE2_RUBIO_GARCIA"
        }, timeout=30)
        
        if response.status_code == 200:
            update_info = response.json()
            return update_info.get("updates_available", False), update_info.get("files_to_update", [])
        else:
            logging.error(f"Error checking for updates: {response.status_code}")
            return False, []
            
    except Exception as e:
        logging.error(f"Error checking for updates: {str(e)}")
        return False, []

def download_and_update_files(files_to_update):
    """Descarga y actualiza los archivos especificados"""
    try:
        # Crear backup de archivos actuales
        backup_dir = os.path.join(RUBIO_SYNC_PATH, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        updated_files = []
        
        for filename in files_to_update:
            logging.info(f"Actualizando archivo: {filename}")
            
            # Hacer backup del archivo actual si existe
            current_file = os.path.join(RUBIO_SYNC_PATH, filename)
            if os.path.exists(current_file):
                shutil.copy2(current_file, os.path.join(backup_dir, filename))
            
            # Descargar nueva versión
            download_response = requests.post(DOWNLOAD_URL, json={
                "filename": filename,
                "client_id": "GABINETE2_RUBIO_GARCIA"
            }, timeout=60)
            
            if download_response.status_code == 200:
                file_data = download_response.json()
                new_content = file_data.get("content", "")
                
                # Escribir nuevo archivo
                if filename.endswith('.json'):
                    # Para archivos JSON, escribir como JSON
                    with open(current_file, 'w', encoding='utf-8') as f:
                        json.dump(json.loads(new_content), f, indent=2)
                else:
                    # Para archivos de texto/código
                    with open(current_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                
                updated_files.append(filename)
                logging.info(f"✅ Archivo actualizado: {filename}")
                
            else:
                logging.error(f"❌ Error descargando {filename}: {download_response.status_code}")
        
        if updated_files:
            logging.info(f"🎉 Sincronización completada. Archivos actualizados: {updated_files}")
            
            # Enviar confirmación al servidor
            requests.post(f"{DEVELOPMENT_API_URL}/sync/confirm-update", json={
                "client_id": "GABINETE2_RUBIO_GARCIA",
                "updated_files": updated_files,
                "timestamp": datetime.now().isoformat()
            }, timeout=30)
            
        return updated_files
        
    except Exception as e:
        logging.error(f"Error updating files: {str(e)}")
        return []

def main():
    """Función principal de sincronización"""
    logging.info("🔄 Iniciando verificación de actualizaciones automáticas...")
    
    # Verificar si hay actualizaciones
    has_updates, files_to_update = check_for_updates()
    
    if has_updates and files_to_update:
        logging.info(f"📥 Actualizaciones disponibles para: {files_to_update}")
        updated_files = download_and_update_files(files_to_update)
        
        if updated_files:
            logging.info("✅ Sincronización automática completada exitosamente")
            return True
        else:
            logging.error("❌ Error en la sincronización automática")
            return False
    else:
        logging.info("✅ No hay actualizaciones disponibles. Archivos actualizados.")
        return True

if __name__ == "__main__":
    main()