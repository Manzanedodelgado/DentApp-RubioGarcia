import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Raw appointment data from Google Sheets
appointments_data = [
    {"Registro": "36078", "Apellidos": "Posado Jañez", "Nombre": "Benita", "TelMovil": "656862011", "Fecha": "2025-02-06", "Hora": "11:00", "EstadoCita": "Desconocido", "Tratamiento": "Revision", "Odontologo": "Dra. Miriam Carrasco", "Notas": "REV ANUAL", "Duracion": "60"},
    {"Registro": "36694", "Apellidos": "Gonzalez Diez", "Nombre": "Natalia", "TelMovil": "685860258", "Fecha": "2025-04-10", "Hora": "11:30", "EstadoCita": "Planificada", "Tratamiento": "Revision", "Odontologo": "Dra. Miriam Carrasco", "Notas": "RECALL REV Y LIMPIEZA", "Duracion": "60"},
    {"Registro": "36707", "Apellidos": "Salvador Fernandez", "Nombre": "Angeles", "TelMovil": "696535026", "Fecha": "2025-04-08", "Hora": "17:15", "EstadoCita": "Finalizada", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "recall lp", "Duracion": "15"},
    {"Registro": "36712", "Apellidos": "Nisar", "Nombre": "Rehan", "TelMovil": "645326820", "Fecha": "2025-04-08", "Hora": "16:00", "EstadoCita": "Desconocido", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "RECALL.", "Duracion": "15"},
    {"Registro": "36777", "Apellidos": "Prieto Serrano", "Nombre": "Samuel", "TelMovil": "695054057", "Fecha": "2025-04-08", "Hora": "16:15", "EstadoCita": "Finalizada", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "RECALL", "Duracion": "15"},
    {"Registro": "36791", "Apellidos": "Perez Gonzalez", "Nombre": "Eloy", "TelMovil": "699872533", "Fecha": "2025-04-09", "Hora": "10:15", "EstadoCita": "Cancelada", "Tratamiento": "Revision", "Odontologo": "Dr. Mario Rubio", "Notas": "RECALL", "Duracion": "15"},
    {"Registro": "37124", "Apellidos": "Sanchez Pascual", "Nombre": "Lidia", "TelMovil": "914860011", "Fecha": "2025-05-13", "Hora": "16:00", "EstadoCita": "Planificada", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "RECAALL", "Duracion": "15"},
    {"Registro": "37517", "Apellidos": "Posado Jañez", "Nombre": "Benita", "TelMovil": "656862011", "Fecha": "2025-01-09", "Hora": "11:00", "EstadoCita": "Desconocido", "Tratamiento": "Otros", "Odontologo": "Dr. Juan Antonio Manzanedo", "Notas": "", "Duracion": "60"},
    {"Registro": "38062", "Apellidos": "Geronimo Gonzalez", "Nombre": "Nashla Teresa", "TelMovil": "610885204", "Fecha": "2025-05-05", "Hora": "16:00", "EstadoCita": "Finalizada", "Tratamiento": "Revision", "Odontologo": "Dra. Virginia Tresgallo", "Notas": "VALORAR", "Duracion": "15"},
    {"Registro": "38079", "Apellidos": "Perez Murillo", "Nombre": "Juana", "TelMovil": "666666666", "Fecha": "2025-06-03", "Hora": "17:00", "EstadoCita": "Cancelada", "Tratamiento": "Higiene dental", "Odontologo": "Dra. Irene Garcia", "Notas": "", "Duracion": "30"},
    {"Registro": "38228", "Apellidos": "Benavente", "Nombre": "Gloria", "TelMovil": "667218746", "Fecha": "2025-03-12", "Hora": "11:00", "EstadoCita": "Finalizada", "Tratamiento": "Revision", "Odontologo": "Dr. Mario Rubio", "Notas": "REV 6 MESES. VER ENCIAS", "Duracion": "15"},
    {"Registro": "38629", "Apellidos": "Calero Alia", "Nombre": "Eva", "TelMovil": "620291468", "Fecha": "2025-04-22", "Hora": "16:30", "EstadoCita": "Finalizada", "Tratamiento": "Higiene dental", "Odontologo": "Dra. Irene Garcia", "Notas": "POSIBLE CURETAJE", "Duracion": "15"},
    {"Registro": "38644", "Apellidos": "Osoro Esteban", "Nombre": "Iñigo", "TelMovil": "649386575", "Fecha": "2025-01-21", "Hora": "11:00", "EstadoCita": "Finalizada", "Tratamiento": "Higiene dental", "Odontologo": "Dra. Irene Garcia", "Notas": "REV PERIO. ES POSIBLE QUE SEA NECESARIO RASPADOS.", "Duracion": "15"},
    {"Registro": "39225", "Apellidos": "Calzada Cabrero", "Nombre": "Mar", "TelMovil": "606278763", "Fecha": "2025-01-15", "Hora": "10:30", "EstadoCita": "Finalizada", "Tratamiento": "Cirugia Implantes", "Odontologo": "Dr. Mario Rubio", "Notas": "ARCADA COMPLETA Y CARGA INMEDIATA", "Duracion": "180"},
    {"Registro": "39191", "Apellidos": "Garcia Lopez", "Nombre": "Belen", "TelMovil": "686098066", "Fecha": "2025-01-09", "Hora": "18:00", "EstadoCita": "Finalizada", "Tratamiento": "Otros", "Odontologo": "Dr. Juan Antonio Manzanedo", "Notas": "BLANQUEAMIENTO", "Duracion": "60"}
]

def normalize_status(status):
    """Normalize appointment status"""
    status_map = {
        "Planificada": "scheduled",
        "Confirmada": "confirmed", 
        "Finalizada": "completed",
        "Cancelada": "cancelled",
        "Anulada": "cancelled",
        "Desconocido": "scheduled"
    }
    return status_map.get(status, "scheduled")

def parse_date_time(date_str, time_str):
    """Parse date and time into datetime object"""
    try:
        date_parts = date_str.split('-')
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        
        time_parts = time_str.split(':')
        hour, minute = int(time_parts[0]), int(time_parts[1])
        
        return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    except:
        return datetime.now(timezone.utc)

async def import_appointments():
    """Import appointments from Google Sheets data"""
    
    print("🚀 Starting data import for RUBIO GARCÍA DENTAL...")
    
    # Clear existing data
    await db.contacts.delete_many({})
    await db.appointments.delete_many({})
    print("✅ Cleared existing data")
    
    contacts_dict = {}
    imported_contacts = 0
    imported_appointments = 0
    
    for apt_data in appointments_data:
        try:
            # Create or get contact
            full_name = f"{apt_data['Nombre']} {apt_data['Apellidos']}"
            phone = apt_data.get('TelMovil', '')
            
            if full_name not in contacts_dict:
                contact_id = str(uuid.uuid4())
                contact = {
                    "id": contact_id,
                    "name": full_name,
                    "phone": phone,
                    "whatsapp": phone,
                    "email": None,
                    "tags": ["paciente", "importado"],
                    "status": "active",
                    "notes": f"Paciente importado de agenda existente",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                await db.contacts.insert_one(contact)
                contacts_dict[full_name] = contact_id
                imported_contacts += 1
                print(f"📝 Created contact: {full_name}")
            
            # Create appointment
            contact_id = contacts_dict[full_name]
            appointment_date = parse_date_time(apt_data['Fecha'], apt_data['Hora'])
            
            appointment = {
                "id": str(uuid.uuid4()),
                "contact_id": contact_id,
                "contact_name": full_name,
                "title": f"{apt_data['Tratamiento']} - {apt_data['Odontologo']}",
                "description": apt_data.get('Notas', ''),
                "date": appointment_date.isoformat(),
                "duration_minutes": int(apt_data.get('Duracion', '30')),
                "status": normalize_status(apt_data['EstadoCita']),
                "reminder_sent": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.appointments.insert_one(appointment)
            imported_appointments += 1
            
        except Exception as e:
            print(f"❌ Error importing appointment {apt_data.get('Registro', 'Unknown')}: {str(e)}")
    
    print(f"\n🎉 Import completed successfully!")
    print(f"✅ Imported {imported_contacts} unique patients")
    print(f"✅ Imported {imported_appointments} appointments")
    print(f"📊 Data is now available in the platform")

async def main():
    await import_appointments()
    client.close()

if __name__ == "__main__":
    asyncio.run(main())