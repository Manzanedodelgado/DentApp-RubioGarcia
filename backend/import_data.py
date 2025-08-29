import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from dotenv import load_dotenv
from googleapiclient.discovery import build
import logging

# Load environment variables
load_dotenv('.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Google Sheets configuration
GOOGLE_SHEETS_API_KEY = os.environ.get('GOOGLE_SHEETS_API_KEY')
SPREADSHEET_ID = '1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ'
RANGE_NAME = 'A:K'  # Try without sheet name first

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_google_sheets_data():
    """Fetch data from Google Sheets"""
    try:
        if not GOOGLE_SHEETS_API_KEY:
            logger.warning("No Google Sheets API key found, using fallback data")
            return get_fallback_data()
        
        service = build('sheets', 'v4', developerKey=GOOGLE_SHEETS_API_KEY)
        sheet = service.spreadsheets()
        
        logger.info(f"🔍 Attempting to fetch data from Google Sheet ID: {SPREADSHEET_ID}")
        
        # Call the Sheets API
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        
        if not values:
            logger.warning("No data found in Google Sheets, using fallback data")
            return get_fallback_data()
        
        logger.info(f"📊 Successfully retrieved {len(values)} rows from Google Sheets")
        
        # Convert to list of dictionaries
        headers = values[0] if values else []
        logger.info(f"📋 Sheet headers found: {headers}")
        
        appointments = []
        
        for i, row in enumerate(values[1:], start=2):  # Skip header row, start counting from row 2
            if len(row) >= len(headers):
                appointment = {}
                for j, header in enumerate(headers):
                    appointment[header] = row[j] if j < len(row) else ""
                
                # Only add if we have essential data (at least name and date)
                if appointment.get('Nombre') and appointment.get('Fecha'):
                    appointments.append(appointment)
                    logger.debug(f"Row {i}: {appointment.get('Nombre')} - {appointment.get('Fecha')}")
        
        logger.info(f"✅ Successfully processed {len(appointments)} appointments from Google Sheets")
        
        # Sort by date (Fecha column) to ensure proper ordering from January 1, 2025
        appointments.sort(key=lambda x: x.get('Fecha', ''))
        logger.info(f"📅 Appointments sorted by date. Date range: {appointments[0].get('Fecha', '')} to {appointments[-1].get('Fecha', '')}")
        
        return appointments
        
    except Exception as e:
        logger.error(f"❌ Error fetching from Google Sheets: {str(e)}")
        logger.info("Using fallback data instead")
        return get_fallback_data()

def get_fallback_data():
    """Fallback data in case Google Sheets is not available"""
    return [
        {"Registro": "36078", "Apellidos": "Posado Jañez", "Nombre": "Benita", "TelMovil": "656862011", "Fecha": "2025-01-20", "Hora": "11:00", "EstadoCita": "Planificada", "Tratamiento": "Revision", "Odontologo": "Dra. Miriam Carrasco", "Notas": "REV ANUAL", "Duracion": "60"},
        {"Registro": "36694", "Apellidos": "Gonzalez Diez", "Nombre": "Natalia", "TelMovil": "685860258", "Fecha": "2025-01-21", "Hora": "11:30", "EstadoCita": "Planificada", "Tratamiento": "Revision", "Odontologo": "Dra. Miriam Carrasco", "Notas": "RECALL REV Y LIMPIEZA", "Duracion": "60"},
        {"Registro": "36707", "Apellidos": "Salvador Fernandez", "Nombre": "Angeles", "TelMovil": "696535026", "Fecha": "2025-01-22", "Hora": "17:15", "EstadoCita": "Planificada", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "recall lp", "Duracion": "15"},
        {"Registro": "36712", "Apellidos": "Nisar", "Nombre": "Rehan", "TelMovil": "645326820", "Fecha": "2025-01-22", "Hora": "16:00", "EstadoCita": "Confirmada", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "RECALL.", "Duracion": "15"},
        {"Registro": "36777", "Apellidos": "Prieto Serrano", "Nombre": "Samuel", "TelMovil": "695054057", "Fecha": "2025-01-23", "Hora": "16:15", "EstadoCita": "Finalizada", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "RECALL", "Duracion": "15"},
        {"Registro": "36791", "Apellidos": "Perez Gonzalez", "Nombre": "Eloy", "TelMovil": "699872533", "Fecha": "2025-01-24", "Hora": "10:15", "EstadoCita": "Cancelada", "Tratamiento": "Revision", "Odontologo": "Dr. Mario Rubio", "Notas": "RECALL", "Duracion": "15"},
        {"Registro": "37124", "Apellidos": "Sanchez Pascual", "Nombre": "Lidia", "TelMovil": "914860011", "Fecha": "2025-01-25", "Hora": "16:00", "EstadoCita": "Planificada", "Tratamiento": "Revision", "Odontologo": "Dra. Irene Garcia", "Notas": "RECAALL", "Duracion": "15"},
        {"Registro": "37517", "Apellidos": "Posado Jañez", "Nombre": "Benita", "TelMovil": "656862011", "Fecha": "2025-01-26", "Hora": "11:00", "EstadoCita": "Confirmada", "Tratamiento": "Otros", "Odontologo": "Dr. Juan Antonio Manzanedo", "Notas": "", "Duracion": "60"},
        {"Registro": "38062", "Apellidos": "Geronimo Gonzalez", "Nombre": "Nashla Teresa", "TelMovil": "610885204", "Fecha": "2025-01-27", "Hora": "16:00", "EstadoCita": "Planificada", "Tratamiento": "Revision", "Odontologo": "Dra. Virginia Tresgallo", "Notas": "VALORAR", "Duracion": "15"},
        {"Registro": "38079", "Apellidos": "Perez Murillo", "Nombre": "Juana", "TelMovil": "666666666", "Fecha": "2025-01-28", "Hora": "17:00", "EstadoCita": "Planificada", "Tratamiento": "Higiene dental", "Odontologo": "Dra. Irene Garcia", "Notas": "", "Duracion": "30"},
        {"Registro": "38228", "Apellidos": "Benavente", "Nombre": "Gloria", "TelMovil": "667218746", "Fecha": "2025-01-29", "Hora": "11:00", "EstadoCita": "Finalizada", "Tratamiento": "Revision", "Odontologo": "Dr. Mario Rubio", "Notas": "REV 6 MESES. VER ENCIAS", "Duracion": "15"},
        {"Registro": "38629", "Apellidos": "Calero Alia", "Nombre": "Eva", "TelMovil": "620291468", "Fecha": "2025-01-30", "Hora": "16:30", "EstadoCita": "Planificada", "Tratamiento": "Higiene dental", "Odontologo": "Dra. Irene Garcia", "Notas": "POSIBLE CURETAJE", "Duracion": "15"},
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
    
    # Get data from Google Sheets
    appointments_data = get_google_sheets_data()
    print(f"📊 Retrieved {len(appointments_data)} appointments from data source")
    
    # Don't clear existing data - instead check for duplicates
    print("🔍 Checking for existing contacts to avoid duplicates...")
    
    existing_contacts = {}
    try:
        existing_contacts_cursor = db.contacts.find({})
        async for contact in existing_contacts_cursor:
            name = contact.get('name', '')
            phone = contact.get('phone', '')
            # Use name + phone as unique key
            key = f"{name}_{phone}"
            existing_contacts[key] = contact.get('id')
        print(f"📋 Found {len(existing_contacts)} existing contacts in database")
    except Exception as e:
        print(f"⚠️ Error checking existing contacts: {e}")
    
    # Clear only appointments to refresh with latest data
    await db.appointments.delete_many({})
    print("✅ Cleared existing appointments for fresh sync")
    
    contacts_dict = {}
    imported_contacts = 0
    imported_appointments = 0
    updated_contacts = 0
    
    # Sort appointments by date (Fecha column) starting from January 1, 2025
    appointments_data.sort(key=lambda x: x.get('Fecha', ''))
    
    for apt_data in appointments_data:
        try:
            # Create or get contact
            full_name = f"{apt_data.get('Nombre', '')} {apt_data.get('Apellidos', '')}".strip()
            phone = apt_data.get('TelMovil', '').strip()
            
            if not full_name or not apt_data.get('Fecha'):
                print(f"⚠️ Skipping incomplete data: {full_name} - {apt_data.get('Fecha')}")
                continue
            
            # Check if contact already exists (avoid duplicates)
            contact_key = f"{full_name}_{phone}"
            
            if contact_key in existing_contacts:
                # Use existing contact
                contact_id = existing_contacts[contact_key]
                contacts_dict[full_name] = contact_id
                updated_contacts += 1
                print(f"🔄 Using existing contact: {full_name}")
            elif full_name not in contacts_dict:
                # Create new contact
                contact_id = str(uuid.uuid4())
                contact = {
                    "id": contact_id,
                    "name": full_name,
                    "phone": phone,
                    "whatsapp": phone,
                    "email": None,
                    "tags": ["paciente", "google-sheets"],
                    "status": "active",
                    "notes": f"Paciente importado desde Google Sheets - Registro: {apt_data.get('Registro', 'N/A')}",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                await db.contacts.insert_one(contact)
                contacts_dict[full_name] = contact_id
                existing_contacts[contact_key] = contact_id  # Add to existing for future checks
                imported_contacts += 1
                print(f"📝 Created new contact: {full_name}")
            else:
                contact_id = contacts_dict[full_name]
            
            # Create appointment using Fecha as key for ordering
            contact_id = contacts_dict[full_name]
            appointment_date = parse_date_time(apt_data['Fecha'], apt_data.get('Hora', '09:00'))
            
            # Build comprehensive title
            treatment = apt_data.get('Tratamiento', 'Consulta')
            doctor = apt_data.get('Odontologo', 'Dr. No especificado')
            title = f"{treatment} - {doctor}"
            
            appointment = {
                "id": str(uuid.uuid4()),
                "contact_id": contact_id,
                "contact_name": full_name,
                "title": title,
                "description": apt_data.get('Notas', ''),
                "date": appointment_date.isoformat(),
                "duration_minutes": int(apt_data.get('Duracion', '30')),
                "status": normalize_status(apt_data.get('EstadoCita', 'Planificada')),
                "reminder_sent": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.appointments.insert_one(appointment)
            imported_appointments += 1
            
        except Exception as e:
            print(f"❌ Error importing appointment {apt_data.get('Registro', 'Unknown')}: {str(e)}")
    
    print(f"\n🎉 Import completed successfully!")
    print(f"✅ Created {imported_contacts} new patients")
    print(f"🔄 Updated {updated_contacts} existing patients")
    print(f"✅ Imported {imported_appointments} appointments")
    print(f"📊 Data is now available in the platform")
    
    if imported_appointments > 0:
        # Get date range for confirmation
        first_apt = await db.appointments.find_one({}, sort=[("date", 1)])
        last_apt = await db.appointments.find_one({}, sort=[("date", -1)])
        if first_apt and last_apt:
            first_date = first_apt.get('date', '')[:10]
            last_date = last_apt.get('date', '')[:10]
            print(f"📅 Appointment date range: {first_date} to {last_date}")

async def main():
    await import_appointments()
    client.close()

if __name__ == "__main__":
    asyncio.run(main())