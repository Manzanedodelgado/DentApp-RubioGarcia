import pyodbc
import requests
import sys
import datetime
import json
import gspread
from google.oauth2.service_account import Credentials

# --- Configuración ---
DB_SERVER = 'GABINETE2\\INFOMED'
DB_DATABASE = 'GELITE'

# Google Sheets configuración
GOOGLE_SHEET_ID = '1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ'  # Tu Google Sheet existente
SERVICE_ACCOUNT_FILE = 'service-account-key.json'  # Archivo JSON de Service Account
GOOGLE_API_KEY = 'AIzaSyA0c7nuWYhCyuiT8F2dBI_v-oqyjoutQ4A'  # Tu API key actual

# App SaaS configuración - CONFIGURAR CON TU URL REAL
SAAS_APP_URL = 'http://localhost:8001/api/gesden/appointments/receive'  # Para testing local
SAAS_API_KEY = None  # No necesitamos autenticación por ahora

# --- Logger ---
def log_message(message):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# --- Función para enviar a Google Sheets ---
def send_to_google_sheets(data):
    """
    Envía datos directamente a Google Sheets usando la API
    Reemplaza la funcionalidad de Make.com
    MÉTODO ALTERNATIVO: Usando API REST directamente
    """
    try:
        # MÉTODO 1: Intentar con Service Account
        try:
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
            sheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1
            
            log_message("    📝 Usando Service Account para escribir...")
            
        except Exception as e:
            log_message(f"    ⚠️  Service Account falló: {e}")
            log_message("    🔄 Intentando método alternativo con API REST...")
            
            # MÉTODO 2: Usar API REST directamente
            return send_to_google_sheets_api_rest(data)
        
        # Preparar fila de datos (en el mismo orden que tu Google Sheet actual)
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
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp de inserción
        ]
        
        # Agregar fila al final de la hoja
        sheet.append_row(row_data)
        log_message(f"✅ Google Sheets: Registro {data['Registro']} enviado correctamente")
        return True
        
    except Exception as e:
        log_message(f"❌ ERROR Google Sheets: {e}")
        return False

def send_to_google_sheets_api_rest(data):
    """
    Método alternativo: enviar a Google Sheets usando API REST
    """
    try:
        # Preparar datos para la API REST
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
        
        # URL de la API para append
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/A:O:append"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            "range": "A:O",
            "majorDimension": "ROWS",
            "values": [row_data]
        }
        
        params = {
            'key': GOOGLE_API_KEY,
            'valueInputOption': 'RAW',
            'insertDataOption': 'INSERT_ROWS'
        }
        
        response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
        
        if response.status_code == 200:
            log_message(f"✅ Google Sheets REST API: Registro {data['Registro']} enviado correctamente")
            return True
        else:
            log_message(f"❌ ERROR API REST: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        log_message(f"❌ ERROR Google Sheets API REST: {e}")
        return False

# --- Función para enviar a App SaaS ---
def send_to_saas_app(data):
    """
    Envía datos directamente a la aplicación SaaS
    Nueva funcionalidad para consentimientos automáticos
    """
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
            "IdUsu": get_doctor_id(data.get('Odontologo', '')),  # Convertir nombre a ID
            "IdIcono": get_treatment_id(data.get('Tratamiento', '')),  # Convertir nombre a ID
            "IdSitC": get_status_id(data.get('EstadoCita', '')),  # Convertir nombre a ID
            "Notas": data.get('Notas', ''),
            "Duracion": data.get('Duracion', 30)
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Agregar autenticación si es necesario
        if SAAS_API_KEY:
            headers["Authorization"] = f"Bearer {SAAS_API_KEY}"
        
        # Enviar a la aplicación SaaS
        response = requests.post(SAAS_APP_URL, json=saas_data, headers=headers, timeout=30)
        response.raise_for_status()
        
        log_message(f"✅ SaaS App: Registro {data['Registro']} enviado correctamente. HTTP {response.status_code}")
        
        # Log de respuesta para depuración
        if response.text:
            response_data = response.json()
            if response_data.get('appointment_id'):
                log_message(f"    Cita creada con ID: {response_data['appointment_id']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        log_message(f"❌ ERROR SaaS App: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log_message(f"    Respuesta: {e.response.text}")
        return False
    except Exception as e:
        log_message(f"❌ ERROR SaaS App inesperado: {e}")
        return False

# --- Funciones auxiliares para mapeo de IDs ---
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
        'Higiene dental': 14
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

# --- Conexión SQL Server ---
conn = None
cursor = None

try:
    log_message(f"🚀 INICIO - Sincronización Gesden sin Make.com")
    log_message(f"Conectando a SQL Server: {DB_SERVER}/{DB_DATABASE}")
    
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={DB_SERVER};'
        f'DATABASE={DB_DATABASE};'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    log_message("✅ Conexión SQL Server establecida correctamente.")

    # --- Misma consulta SQL que tu script original ---
    query = """ SELECT TOP 10 -- Obtiene las 10 filas con la HorSitCita más reciente
    IdCita AS Registro,
    HorSitCita AS CitMod, -- Esta es la columna por la que ordenamos
    FecAlta AS FechaAlta,
    NUMPAC AS NumPac,
    CASE
        WHEN CHARINDEX(',', Texto) > 0 THEN LTRIM(RTRIM(LEFT(Texto, CHARINDEX(',', Texto) - 1)))
        ELSE NULL
    END AS Apellidos,
    CASE
        WHEN CHARINDEX(',', Texto) > 0 THEN LTRIM(RTRIM(SUBSTRING(Texto, CHARINDEX(',', Texto) + 1, LEN(Texto))))
        ELSE Texto
    END AS Nombre,
    Movil AS TelMovil,
    CONVERT(VARCHAR(10), DATEADD(DAY, Fecha - 2, '1900-01-01'), 23) AS Fecha,
    CONVERT(VARCHAR(5), DATEADD(SECOND, Hora, 0), 108) AS Hora,
    CASE
        WHEN IdSitC = 0 THEN 'Planificada'
        WHEN IdSitC = 1 THEN 'Anulada'
        WHEN IdSitC = 5 THEN 'Finalizada'
        WHEN IdSitC = 7 THEN 'Confirmada'
        WHEN IdSitC = 8 THEN 'Cancelada'
        ELSE 'Desconocido'
    END AS EstadoCita,
    CASE
        WHEN IdIcono = 1 THEN 'Revision'
        WHEN IdIcono = 2 THEN 'Urgencia'
        WHEN IdIcono = 9 THEN 'Periodoncia'
        WHEN IdIcono = 10 THEN 'Cirugia Implantes'
        WHEN IdIcono = 11 THEN 'Ortodoncia'
        WHEN IdIcono = 13 THEN 'Primera'
        WHEN IdIcono = 14 THEN 'Higiene dental'
        ELSE 'Otros'
    END AS Tratamiento,
    CASE
        WHEN IdUsu = 3 THEN 'Dr. Mario Rubio'
        WHEN IdUsu = 4 THEN 'Dra. Irene Garcia'
        WHEN IdUsu = 8 THEN 'Dra. Virginia Tresgallo'
        WHEN IdUsu = 10 THEN 'Dra. Miriam Carrasco'
        WHEN IdUsu = 12 THEN 'Dr. Juan Antonio Manzanedo'
        ELSE 'Odontologo'
    END AS Odontologo,
    CONVERT(NVARCHAR(MAX), NOTAS) AS Notas, -- Aseguramos la compatibilidad del tipo de dato
    CAST(CAST(Duracion AS DECIMAL(10, 2)) / 60 AS INT) AS Duracion
FROM dbo.DCitas
ORDER BY HorSitCita DESC; -- Ordena por la fecha/hora de modificación en descendente para obtener las últimas
    """

    log_message("Ejecutando consulta SQL...")
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    log_message(f"✅ Consulta ejecutada. Se encontraron {len(rows)} registros.")

    if not rows:
        log_message("ℹ️  No hay registros nuevos para sincronizar.")
    else:
        success_google = 0
        success_saas = 0
        
        for i, row in enumerate(rows):
            data = dict(zip(columns, row))

            # Convertir datos a texto seguro para envío (mismo que tu script original)
            for key, value in data.items():
                if isinstance(value, (bytes, bytearray)):
                    data[key] = value.decode('utf-8', errors='ignore')
                elif isinstance(value, datetime.datetime):
                    data[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif value is None:
                    data[key] = ""
                else:
                    data[key] = str(value)

            # --- LOG COMPLETO DEL REGISTRO ---
            log_message(f"\n➡️  [{i+1}/{len(rows)}] Procesando Registro: {data['Registro']}")
            log_message(f"    Paciente: {data['Nombre']} {data['Apellidos']}")
            log_message(f"    Fecha: {data['Fecha']} {data['Hora']}")
            log_message(f"    Tratamiento: {data['Tratamiento']} | Doctor: {data['Odontologo']}")
            log_message(f"    Estado: {data['EstadoCita']}")

            # --- ENVÍO DUAL: Google Sheets + SaaS App ---
            
            # 1. Envío a Google Sheets (reemplaza Make.com)
            if send_to_google_sheets(data):
                success_google += 1
            
            # 2. Envío a SaaS App (nueva funcionalidad)
            if send_to_saas_app(data):
                success_saas += 1
        
        # --- RESUMEN FINAL ---
        log_message(f"\n📊 RESUMEN DE SINCRONIZACIÓN:")
        log_message(f"    Total registros procesados: {len(rows)}")
        log_message(f"    ✅ Google Sheets exitosos: {success_google}/{len(rows)}")
        log_message(f"    ✅ SaaS App exitosos: {success_saas}/{len(rows)}")
        
        if success_google == len(rows) and success_saas == len(rows):
            log_message(f"🎉 SINCRONIZACIÓN COMPLETAMENTE EXITOSA!")
        else:
            log_message(f"⚠️  Algunos envíos fallaron. Revisar logs anteriores.")

except pyodbc.Error as ex:
    log_message(f"❌ ERROR BD: {ex}")
    sys.exit(1)
except Exception as e:
    log_message(f"❌ ERROR CRÍTICO: {e}")
    sys.exit(1)
finally:
    if cursor:
        cursor.close()
        log_message("🔒 Cursor cerrado.")
    if conn:
        conn.close()
        log_message("🔒 Conexión cerrada.")

log_message("✅ Sincronización finalizada.")
sys.exit(0)