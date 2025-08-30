#!/usr/bin/env python3
"""
Simulación completa del flujo sync_modified.py
Simula datos de Gesden y prueba el envío a Google Sheets + SaaS App
"""

import sys
import os
import datetime

# Agregar el directorio actual al path para importar sync_modified
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar funciones del sync_modified
from sync_modified import send_to_google_sheets, send_to_saas_app, log_message

def test_complete_sync_flow():
    """
    Simular el flujo completo de sincronización
    """
    
    print("🧪 SIMULACIÓN COMPLETA - ELIMINANDO MAKE.COM")
    print("=" * 60)
    
    # Datos simulados de Gesden (como si vinieran de tu query SQL)
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
        },
        {
            'Registro': 'SIM-003',
            'CitMod': '2025-08-30 10:37:00', 
            'FechaAlta': '2025-08-29 17:30:00',
            'NumPac': '11111',
            'Apellidos': 'Fernández',
            'Nombre': 'María',
            'TelMovil': '600999888',
            'Fecha': '2025-09-17',
            'Hora': '14:30',
            'EstadoCita': 'Planificada',
            'Tratamiento': 'Revision',  # Código 1 - No requiere consentimiento
            'Odontologo': 'Dra. Miriam Carrasco',
            'Notas': 'Revisión de control semestral',
            'Duracion': '20'
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
        log_message(f"    🏥 Tratamiento: {data['Tratamiento']} | 👨‍⚕️ Doctor: {data['Odontologo']}")
        log_message(f"    📊 Estado: {data['EstadoCita']}")
        
        # --- ENVÍO DUAL: Google Sheets + SaaS App ---
        
        # 1. Envío a Google Sheets (reemplaza Make.com)
        log_message(f"    📝 Enviando a Google Sheets...")
        if send_to_google_sheets(data):
            success_google += 1
            log_message(f"    ✅ Google Sheets: OK")
        else:
            log_message(f"    ❌ Google Sheets: ERROR")
        
        # 2. Envío a SaaS App (nueva funcionalidad)
        log_message(f"    🚀 Enviando a SaaS App...")
        if send_to_saas_app(data):
            success_saas += 1
            log_message(f"    ✅ SaaS App: OK")
        else:
            log_message(f"    ❌ SaaS App: ERROR")
    
    # --- RESUMEN FINAL ---
    log_message(f"\n📊 RESUMEN DE SIMULACIÓN:")
    log_message(f"    📋 Total registros procesados: {len(simulated_gesden_data)}")
    log_message(f"    📄 Google Sheets exitosos: {success_google}/{len(simulated_gesden_data)}")
    log_message(f"    🚀 SaaS App exitosos: {success_saas}/{len(simulated_gesden_data)}")
    
    # Analizar tipos de tratamiento
    treatments = {}
    for data in simulated_gesden_data:
        treatment = data['Tratamiento']
        treatments[treatment] = treatments.get(treatment, 0) + 1
    
    log_message(f"\n🏥 ANÁLISIS DE TRATAMIENTOS:")
    for treatment, count in treatments.items():
        log_message(f"    • {treatment}: {count} cita(s)")
        
        # Determinar si requiere consentimiento
        if treatment in ['Cirugia Implantes', 'Periodoncia', 'Ortodoncia', 'Endodoncia']:
            log_message(f"      → 📋 Requiere consentimiento informado")
        elif treatment == 'Primera':
            log_message(f"      → 📋 Requiere LOPD")
        else:
            log_message(f"      → ✅ No requiere consentimiento")
    
    if success_google == len(simulated_gesden_data) and success_saas == len(simulated_gesden_data):
        log_message(f"\n🎉 ¡SIMULACIÓN COMPLETAMENTE EXITOSA!")
        log_message(f"    ✅ Make.com ELIMINADO - Flujo directo funcional")
        log_message(f"    ✅ Google Sheets - Datos sincronizados")
        log_message(f"    ✅ SaaS App - Consentimientos automáticos listos")
        return True
    else:
        log_message(f"\n⚠️ Algunos envíos fallaron. Revisar logs anteriores.")
        return False

if __name__ == "__main__":
    success = test_complete_sync_flow()
    
    if success:
        print(f"\n✅ LISTO PARA REEMPLAZAR MAKE.COM")
        print("   Tu script sync_modified.py está funcionando perfectamente")
        print("   Puedes reemplazar sync.py por sync_modified.py")
    else:
        print(f"\n❌ HAY ERRORES QUE CORREGIR")
        print("   Revisa los logs para identificar problemas")