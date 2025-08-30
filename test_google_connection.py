#!/usr/bin/env python3
"""
Script de prueba para verificar conexión con Google Sheets
Ejecutar ANTES de usar sync_modified.py
"""

import gspread
from google.oauth2.service_account import Credentials
import datetime
import sys

# Configuración (cambiar según tus datos)
GOOGLE_SHEET_ID = '1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ'
SERVICE_ACCOUNT_FILE = 'service-account-key.json'

def test_google_sheets_connection():
    """Prueba la conexión y escritura a Google Sheets"""
    
    print("🧪 PRUEBA DE CONEXIÓN GOOGLE SHEETS")
    print("=" * 50)
    
    try:
        # Paso 1: Verificar archivo de credenciales
        print("1️⃣ Verificando archivo de credenciales...")
        try:
            with open(SERVICE_ACCOUNT_FILE, 'r') as f:
                import json
                creds_data = json.load(f)
                service_email = creds_data.get('client_email', 'No encontrado')
                print(f"   ✅ Archivo encontrado: {SERVICE_ACCOUNT_FILE}")
                print(f"   📧 Service Account Email: {service_email}")
        except FileNotFoundError:
            print(f"   ❌ ERROR: No se encontró el archivo {SERVICE_ACCOUNT_FILE}")
            print("   💡 Asegúrate de descargar el archivo JSON y renombrarlo correctamente")
            return False
        except Exception as e:
            print(f"   ❌ ERROR leyendo credenciales: {e}")
            return False
        
        # Paso 2: Configurar credenciales y scopes
        print("\n2️⃣ Configurando credenciales y permisos...")
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=scopes
        )
        print("   ✅ Credenciales configuradas correctamente")
        
        # Paso 3: Conectar a Google Sheets
        print("\n3️⃣ Conectando a Google Sheets...")
        gc = gspread.authorize(credentials)
        print("   ✅ Autorización exitosa")
        
        # Paso 4: Abrir el Google Sheet específico
        print(f"\n4️⃣ Abriendo Google Sheet ID: {GOOGLE_SHEET_ID}...")
        try:
            spreadsheet = gc.open_by_key(GOOGLE_SHEET_ID)
            
            # Intentar usar la hoja TestSync
            try:
                sheet = spreadsheet.worksheet("TestSync")
                print(f"   ✅ Sheet abierto: '{spreadsheet.title}'")
                print(f"   📄 Hoja activa: 'TestSync' (sin protecciones)")
            except gspread.exceptions.WorksheetNotFound:
                sheet = spreadsheet.sheet1  # Fallback a primera hoja
                print(f"   ⚠️ Hoja TestSync no encontrada, usando: '{sheet.title}'")
        except gspread.SpreadsheetNotFound:
            print(f"   ❌ ERROR: Google Sheet no encontrado o sin acceso")
            print(f"   💡 Verifica que compartiste el sheet con: {service_email}")
            print(f"   💡 URL del sheet: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
            return False
        except Exception as e:
            print(f"   ❌ ERROR abriendo sheet: {e}")
            return False
        
        # Paso 5: Leer datos existentes (opcional)
        print("\n5️⃣ Leyendo datos existentes...")
        try:
            existing_data = sheet.get_all_records()
            print(f"   📊 Filas con datos encontradas: {len(existing_data)}")
            if len(existing_data) > 0:
                print(f"   📋 Columnas: {list(existing_data[0].keys())}")
        except Exception as e:
            print(f"   ⚠️ No se pudieron leer datos existentes: {e}")
        
        # Paso 6: Escribir fila de prueba
        print("\n6️⃣ Escribiendo fila de prueba...")
        test_row = [
            "TEST-001",  # Registro
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # CitMod
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # FechaAlta
            "12345",     # NumPac
            "García",    # Apellidos
            "Test",      # Nombre
            "600123456", # TelMovil
            datetime.datetime.now().strftime('%Y-%m-%d'),  # Fecha
            "10:00",     # Hora
            "Confirmada", # EstadoCita
            "Revision",  # Tratamiento
            "Dr. Test",  # Odontologo
            "Prueba de conexión desde script Python", # Notas
            "30",        # Duracion
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp inserción
        ]
        
        try:
            sheet.append_row(test_row)
            print(f"   ✅ Fila de prueba insertada correctamente")
            print(f"   🔗 Verifica en: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
        except gspread.exceptions.APIError as e:
            print(f"   ❌ ERROR de permisos API: {e}")
            print(f"   💡 Verifica que el service account tiene permisos de EDITOR en el sheet")
            return False
        except Exception as e:
            print(f"   ❌ ERROR escribiendo: {e}")
            return False
        
        # Paso 7: Verificar escritura
        print("\n7️⃣ Verificando escritura...")
        try:
            updated_data = sheet.get_all_records()
            if len(updated_data) > len(existing_data if 'existing_data' in locals() else []):
                print("   ✅ Fila agregada y verificada correctamente")
            else:
                print("   ⚠️ La fila se agregó pero no se pudo verificar")
        except Exception as e:
            print(f"   ⚠️ No se pudo verificar la escritura: {e}")
        
        print(f"\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        print("   ✅ Google Sheets está configurado correctamente")
        print("   ✅ Puedes usar sync_modified.py sin problemas")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        print("\n🔍 PASOS PARA SOLUCIONAR:")
        print("1. Verifica que descargaste el archivo service-account-key.json")
        print("2. Verifica que está en la misma carpeta que este script")
        print("3. Verifica que compartiste el Google Sheet con el service account")
        print("4. Verifica que habilitaste Google Sheets API en Google Cloud Console")
        return False

if __name__ == "__main__":
    success = test_google_sheets_connection()
    
    if success:
        print(f"\n✅ LISTO PARA USAR sync_modified.py")
        sys.exit(0)
    else:
        print(f"\n❌ CONFIGURACIÓN INCOMPLETA")
        print("   Revisa los errores anteriores y sigue las instrucciones")
        sys.exit(1)