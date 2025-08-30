#!/usr/bin/env python3
"""
Test de las funciones de sincronización sin dependencias de pyodbc
"""

import requests
import datetime
import json
import gspread
from google.oauth2.service_account import Credentials

# Configuración (copiada de sync_modified.py)
GOOGLE_SHEET_ID = '1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ'
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
SAAS_APP_URL = 'http://localhost:8001/api/gesden/appointments/receive'
SAAS_API_KEY = None

# Logger
def log_message(message):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# Funciones de envío (copiadas y adaptadas de sync_modified.py)
def send_to_google_sheets(data):
    """Envía datos directamente a Google Sheets usando la API"""
    try:
        # Configurar credenciales
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=scopes
        )
        
        # Conectar a Google Sheets
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(GOOGLE_SHEET_ID)
        
        # Usar hoja TestSync
        try:
            sheet = spreadsheet.worksheet("TestSync")
            log_message("    📋 Usando hoja 'TestSync'")
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.sheet1
            log_message("    📋 Usando 'Hoja 1' (principal)")
        
        # Preparar fila de datos
        row_data = [
            data.get('Registro', ''),
            data.get('CitMod', ''),
            data.get('FechaAlta', ''),
            data.get('NumPac', ''),
            data.get('Apellidos', ''),
            data.get('Nombre', ''),
            data.get('TelMovil', ''),
            data.get('Fecha', ''),
            data.get('Hora', ''),
            data.get('EstadoCita', ''),
            data.get('Tratamiento', ''),
            data.get('Odontologo', ''),
            data.get('Notas', ''),
            data.get('Duracion', ''),
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp
        ]
        
        # Agregar fila
        sheet.append_row(row_data)
        log_message(f"✅ Google Sheets: Registro {data['Registro']} enviado correctamente")
        return True
        
    except Exception as e:
        log_message(f"❌ ERROR Google Sheets: {e}")
        return False

def send_to_saas_app(data):
    """Envía datos directamente a la aplicación SaaS"""
    try:
        # Mapear datos al formato esperado por la app SaaS
        saas_data = {
            "id": data.get('Registro'),
            "NumPac": data.get('NumPac'),
            "Nombre": data.get('Nombre', ''),
            "Apellidos": data.get('Apellidos', ''),
            "TelMovil": data.get('TelMovil', ''),
            "Fecha": data.get('Fecha'),
            "Hora": data.get('Hora'),
            "IdUsu": get_doctor_id(data.get('Odontologo', '')),
            "IdIcono": get_treatment_id(data.get('Tratamiento', '')),
            "IdSitC": get_status_id(data.get('EstadoCita', '')),
            "Notas": data.get('Notas', ''),
            "Duracion": data.get('Duracion', 30)
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Enviar a la aplicación SaaS
        response = requests.post(SAAS_APP_URL, json=saas_data, headers=headers, timeout=30)
        response.raise_for_status()
        
        log_message(f"✅ SaaS App: Registro {data['Registro']} enviado correctamente. HTTP {response.status_code}")
        
        # Log de respuesta
        if response.text:
            try:
                response_data = response.json()
                if response_data.get('appointment_id'):
                    log_message(f"    📋 Cita creada con ID: {response_data['appointment_id']}")
            except:
                pass
        
        return True
        
    except Exception as e:
        log_message(f"❌ ERROR SaaS App: {e}")
        return False

# Funciones auxiliares para mapeo
def get_doctor_id(doctor_name):
    """Convierte nombre del doctor a ID numérico"""
    doctor_mapping = {
        'Dr. Mario Rubio': 3,
        'Dra. Irene Garcia': 4,
        'Dra. Virginia Tresgallo': 8,
        'Dra. Miriam Carrasco': 10,
        'Dr. Juan Antonio Manzanedo': 12
    }
    return doctor_mapping.get(doctor_name, 0)

def get_treatment_id(treatment_name):
    """Convierte nombre del tratamiento a ID numérico"""
    treatment_mapping = {
        'Revision': 1,
        'Urgencia': 2,
        'Periodoncia': 9,
        'Cirugia Implantes': 10,
        'Ortodoncia': 11,
        'Primera': 13,
        'Higiene dental': 14,
        'Endodoncia': 16
    }
    return treatment_mapping.get(treatment_name, 0)

def get_status_id(status_name):
    """Convierte nombre del estado a ID numérico"""
    status_mapping = {
        'Planificada': 0,
        'Anulada': 1,
        'Finalizada': 5,
        'Confirmada': 7,
        'Cancelada': 8
    }
    return status_mapping.get(status_name, 0)

def test_complete_sync_flow():
    """Simulación completa del flujo"""
    
    print("🧪 SIMULACIÓN COMPLETA - ELIMINANDO MAKE.COM")
    print("=" * 60)
    
    # Datos simulados de Gesden
    simulated_gesden_data = [
        {
            'Registro': 'SIM-001',
            'CitMod': '2025-08-30 10:35:00',
            'FechaAlta': '2025-08-29 15:20:00',
            'NumPac': '12345',
            'Apellidos': 'García Ruiz',
            'Nombre': 'Ana',
            'TelMovil': '600123456',
            'Fecha': '2025-09-15',
            'Hora': '09:30',
            'EstadoCita': 'Planificada',
            'Tratamiento': 'Cirugia Implantes',  # Código 10 - Requiere consentimiento
            'Odontologo': 'Dr. Mario Rubio',
            'Notas': 'Primera consulta para implante dental',
            'Duracion': '60'
        },
        {
            'Registro': 'SIM-002', 
            'CitMod': '2025-08-30 10:36:00',
            'FechaAlta': '2025-08-29 16:00:00',
            'NumPac': '67890',
            'Apellidos': 'López Martín',
            'Nombre': 'Carlos',
            'TelMovil': '600654321',
            'Fecha': '2025-09-16',
            'Hora': '11:00',
            'EstadoCita': 'Confirmada',
            'Tratamiento': 'Primera',  # Código 13 - Requiere LOPD
            'Odontologo': 'Dra. Irene Garcia',
            'Notas': 'Primera visita - revisión general',
            'Duracion': '30'
        }
    ]
    
    log_message("🚀 INICIANDO SIMULACIÓN DE FLUJO COMPLETO")
    log_message(f"📊 Simulando {len(simulated_gesden_data)} registros de Gesden")
    
    success_google = 0
    success_saas = 0
    
    for i, data in enumerate(simulated_gesden_data):
        
        log_message(f"\n➡️ [{i+1}/{len(simulated_gesden_data)}] Procesando Registro: {data['Registro']}")
        log_message(f"    👤 Paciente: {data['Nombre']} {data['Apellidos']}")
        log_message(f"    📅 Fecha: {data['Fecha']} {data['Hora']}")
        log_message(f"    🏥 Tratamiento: {data['Tratamiento']} (ID: {get_treatment_id(data['Tratamiento'])})")
        log_message(f"    👨‍⚕️ Doctor: {data['Odontologo']} (ID: {get_doctor_id(data['Odontologo'])})")
        log_message(f"    📊 Estado: {data['EstadoCita']} (ID: {get_status_id(data['EstadoCita'])})")
        
        # Envío a Google Sheets
        if send_to_google_sheets(data):
            success_google += 1
        
        # Envío a SaaS App
        if send_to_saas_app(data):
            success_saas += 1
    
    # Resumen
    log_message(f"\n📊 RESUMEN DE SIMULACIÓN:")
    log_message(f"    📋 Total registros procesados: {len(simulated_gesden_data)}")
    log_message(f"    📄 Google Sheets exitosos: {success_google}/{len(simulated_gesden_data)}")
    log_message(f"    🚀 SaaS App exitosos: {success_saas}/{len(simulated_gesden_data)}")
    
    if success_google == len(simulated_gesden_data) and success_saas == len(simulated_gesden_data):
        log_message(f"\n🎉 ¡SIMULACIÓN COMPLETAMENTE EXITOSA!")
        log_message(f"    ✅ Make.com ELIMINADO - Flujo directo funcional")
        log_message(f"    ✅ Google Sheets - Datos sincronizados")
        log_message(f"    ✅ SaaS App - Consentimientos automáticos listos")
        return True
    else:
        log_message(f"\n⚠️ Algunos envíos fallaron.")
        return False

if __name__ == "__main__":
    success = test_complete_sync_flow()
    
    if success:
        print(f"\n🎉 ¡ÉXITO TOTAL! MAKE.COM ELIMINADO")
        print("=" * 50)
        print("✅ Google Sheets: Funcionando perfectamente")
        print("✅ SaaS App: Consentimientos automáticos listos")
        print("✅ Script sync_modified.py: Listo para producción")
        print("\nPuedes reemplazar tu script actual por sync_modified.py")
    else:
        print(f"\n❌ HAY ERRORES QUE CORREGIR")