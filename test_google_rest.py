#!/usr/bin/env python3
"""
Prueba del método REST API para escribir a Google Sheets
"""

import requests
import datetime
import json

# Configuración
GOOGLE_SHEET_ID = '1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ'
GOOGLE_API_KEY = 'AIzaSyA0c7nuWYhCyuiT8F2dBI_v-oqyjoutQ4A'

def test_google_sheets_rest_api():
    """Prueba escribir a Google Sheets usando REST API"""
    
    print("🧪 PRUEBA GOOGLE SHEETS REST API")
    print("=" * 50)
    
    try:
        # Datos de prueba
        test_row = [
            "TEST-REST-001",  # Registro
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # CitMod
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # FechaAlta
            "99999",          # NumPac
            "API",            # Apellidos
            "Test REST",      # Nombre
            "600999999",      # TelMovil
            datetime.datetime.now().strftime('%Y-%m-%d'),  # Fecha
            "15:30",          # Hora
            "Programada",     # EstadoCita
            "Prueba API",     # Tratamiento
            "Dr. Test REST",  # Odontologo
            "Prueba de escritura REST API",  # Notas
            "45",             # Duracion
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp
        ]
        
        print("1️⃣ Preparando datos de prueba...")
        print(f"   📊 Datos: {test_row[:3]}... (y {len(test_row)-3} campos más)")
        
        print("\n2️⃣ Enviando a Google Sheets REST API...")
        
        # URL de la API
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/A:O:append"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            "range": "A:O",
            "majorDimension": "ROWS",
            "values": [test_row]
        }
        
        params = {
            'key': GOOGLE_API_KEY,
            'valueInputOption': 'RAW',
            'insertDataOption': 'INSERT_ROWS'
        }
        
        print(f"   🌐 URL: {url}")
        print(f"   🔑 API Key: {GOOGLE_API_KEY[:20]}...")
        
        response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
        
        print(f"\n3️⃣ Respuesta del servidor:")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"   ✅ Éxito! Datos escritos correctamente")
            print(f"   📍 Rango actualizado: {response_data.get('updates', {}).get('updatedRange', 'N/A')}")
            print(f"   📝 Filas agregadas: {response_data.get('updates', {}).get('updatedRows', 0)}")
            print(f"\n🎉 PRUEBA EXITOSA - Google Sheets REST API funciona!")
            print(f"🔗 Verifica en: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            
            # Diagnóstico de errores comunes
            if response.status_code == 403:
                print(f"\n🔍 DIAGNÓSTICO:")
                print(f"   • Error 403: Permisos insuficientes")
                print(f"   • Solución: El API key necesita permisos de escritura")
                print(f"   • O el Google Sheet no permite escritura pública")
            elif response.status_code == 400:
                print(f"\n🔍 DIAGNÓSTICO:")
                print(f"   • Error 400: Formato de datos incorrecto")
                print(f"   • Revisar estructura de datos enviados")
            
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        return False

if __name__ == "__main__":
    success = test_google_sheets_rest_api()
    
    if success:
        print(f"\n✅ MÉTODO REST FUNCIONA")
        print("   Puedes usar sync_modified.py con el método alternativo")
    else:
        print(f"\n❌ MÉTODO REST FALLÓ")
        print("   Necesitamos configurar OAuth o usar otro método")