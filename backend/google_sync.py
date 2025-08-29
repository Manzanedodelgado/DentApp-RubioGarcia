import asyncio
import json
import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv('.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Google Sheets configuration
SPREADSHEET_ID = '1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ'
RANGE_NAME = 'A:O'
SERVICE_ACCOUNT_ID = '105327385088371729569'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Column mapping for Google Sheets (1-based index)
COLUMN_MAPPING = {
    'A': 'Registro',      # Patient ID/Registry number
    'B': 'Campo2',        # Unknown field 2
    'C': 'Campo3',        # Unknown field 3  
    'D': 'NumPac',        # Patient Number
    'E': 'Nombre',        # First Name
    'F': 'Apellidos',     # Last Name
    'G': 'TelMovil',      # Mobile Phone
    'H': 'Fecha',         # Date
    'I': 'Hora',          # Time
    'J': 'EstadoCita',    # Appointment Status
    'K': 'Tratamiento',   # Treatment
    'L': 'Doctor',        # Doctor/Odontologo
    'M': 'Notas',         # Notes
    'N': 'Duracion',      # Duration
    'O': 'Campo15'        # Additional field
}

class GoogleSheetsSync:
    def __init__(self):
        self.service = None
        self.credentials_path = '/app/backend/service-account-key.json'
        
    def authenticate(self):
        """Authenticate with Google Sheets API using Service Account"""
        try:
            if not os.path.exists(self.credentials_path):
                logger.warning(f"Service account file not found at {self.credentials_path}")
                return False
                
            # Define the scope
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ]
            
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Successfully authenticated with Google Sheets API")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            return False
    
    def read_sheet_data(self) -> List[List[str]]:
        """Read all data from Google Sheet"""
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"📊 Read {len(values)} rows from Google Sheet")
            return values
            
        except HttpError as e:
            logger.error(f"❌ HTTP error reading sheet: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"❌ Error reading sheet: {str(e)}")
            return []
    
    def write_sheet_data(self, data: List[List[str]], range_name: str = None) -> bool:
        """Write data to Google Sheet"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            if range_name is None:
                range_name = RANGE_NAME
            
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            logger.info(f"✅ Updated {updated_cells} cells in Google Sheet")
            return True
            
        except HttpError as e:
            logger.error(f"❌ HTTP error writing sheet: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Error writing sheet: {str(e)}")
            return False
    
    def update_single_row(self, row_number: int, row_data: List[str]) -> bool:
        """Update a single row in Google Sheet"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            range_name = f"A{row_number}:O{row_number}"
            
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"✅ Updated row {row_number} in Google Sheet")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating row {row_number}: {str(e)}")
            return False
    
    def find_appointment_row(self, patient_number: str, fecha: str, hora: str) -> int:
        """Find the row number of an appointment based on unique identifiers"""
        try:
            sheet_data = self.read_sheet_data()
            if not sheet_data:
                return -1
            
            # Skip header row, start from row 2
            for i, row in enumerate(sheet_data[1:], start=2):
                if len(row) >= 9:  # Ensure row has enough columns
                    row_numpac = row[3] if len(row) > 3 else ''  # Column D
                    row_fecha = row[7] if len(row) > 7 else ''   # Column H
                    row_hora = row[8] if len(row) > 8 else ''    # Column I
                    
                    if (row_numpac == patient_number and 
                        row_fecha == fecha and 
                        row_hora == hora):
                        logger.info(f"Found appointment at row {i}")
                        return i
            
            logger.warning(f"Appointment not found: NumPac={patient_number}, Fecha={fecha}, Hora={hora}")
            return -1
            
        except Exception as e:
            logger.error(f"❌ Error finding appointment row: {str(e)}")
            return -1

# Global sync instance
google_sync = GoogleSheetsSync()

def appointment_to_sheet_row(appointment: Dict[str, Any], existing_row: List[str] = None) -> List[str]:
    """Convert appointment from MongoDB to Google Sheets row format"""
    try:
        # Start with existing row or create new one
        if existing_row and len(existing_row) >= 15:
            row = existing_row.copy()
        else:
            row = [''] * 15  # 15 columns (A to O)
        
        # Map appointment data to appropriate columns
        # Keep existing data that we don't manage
        row[3] = appointment.get('patient_number', '')     # Column D - NumPac
        row[4] = appointment.get('contact_name', '').split()[0] if appointment.get('contact_name') else ''  # Column E - Nombre
        row[5] = ' '.join(appointment.get('contact_name', '').split()[1:]) if appointment.get('contact_name') else ''  # Column F - Apellidos
        row[6] = appointment.get('phone', '')              # Column G - TelMovil
        
        # Parse date from ISO format to YYYY-MM-DD
        if appointment.get('date'):
            try:
                date_obj = datetime.fromisoformat(appointment['date'].replace('Z', '+00:00'))
                row[7] = date_obj.strftime('%Y-%m-%d')     # Column H - Fecha
            except:
                row[7] = appointment.get('date', '')[:10]
        
        row[8] = appointment.get('time', '')               # Column I - Hora
        
        # Map status from our format to Google Sheets format
        status_mapping = {
            'scheduled': 'Planificada',
            'confirmed': 'Confirmada',
            'completed': 'Finalizada',
            'cancelled': 'Cancelada'
        }
        row[9] = status_mapping.get(appointment.get('status'), 'Planificada')  # Column J - EstadoCita
        
        row[10] = appointment.get('treatment', '')         # Column K - Tratamiento  
        row[11] = appointment.get('doctor', '')            # Column L - Doctor
        
        # Notes can include description or other info
        notes = appointment.get('description', '')
        if appointment.get('notes'):
            notes += f" | {appointment['notes']}"
        row[12] = notes                                    # Column M - Notas
        
        row[13] = str(appointment.get('duration_minutes', 30))  # Column N - Duracion
        
        return row
        
    except Exception as e:
        logger.error(f"❌ Error converting appointment to sheet row: {str(e)}")
        return [''] * 15

async def sync_appointment_to_sheets(appointment: Dict[str, Any]) -> bool:
    """Sync a single appointment change back to Google Sheets"""
    try:
        logger.info(f"🔄 Syncing appointment to Google Sheets: {appointment.get('contact_name')} - {appointment.get('date')}")
        
        # Find the appointment row in Google Sheets
        patient_number = appointment.get('patient_number', '')
        date_str = appointment.get('date', '')[:10] if appointment.get('date') else ''
        time_str = appointment.get('time', '')
        
        row_number = google_sync.find_appointment_row(patient_number, date_str, time_str)
        
        if row_number > 0:
            # Get existing row data
            sheet_data = google_sync.read_sheet_data()
            existing_row = sheet_data[row_number - 1] if len(sheet_data) >= row_number else None
            
            # Convert appointment to sheet row format
            updated_row = appointment_to_sheet_row(appointment, existing_row)
            
            # Update the specific row
            success = google_sync.update_single_row(row_number, updated_row)
            
            if success:
                logger.info(f"✅ Successfully synced appointment to Google Sheets row {row_number}")
                
                # Mark appointment as synced in database
                await db.appointments.update_one(
                    {"id": appointment["id"]},
                    {"$set": {
                        "synced_to_sheets": True,
                        "last_synced_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                return True
            else:
                logger.error(f"❌ Failed to sync appointment to Google Sheets")
                return False
        else:
            logger.warning(f"⚠️ Appointment not found in Google Sheets, skipping sync")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error syncing appointment to sheets: {str(e)}")
        return False

async def sync_pending_changes_to_sheets():
    """Sync all pending appointment changes to Google Sheets"""
    try:
        logger.info("🔄 Starting sync of pending changes to Google Sheets...")
        
        # Find appointments that have been modified but not synced
        pending_appointments = await db.appointments.find({
            "$or": [
                {"synced_to_sheets": {"$ne": True}},
                {"updated_at": {"$gt": {"$date": "2024-01-01T00:00:00Z"}}}  # Modified recently
            ]
        }).limit(50).to_list(50)
        
        if not pending_appointments:
            logger.info("✅ No pending changes to sync")
            return True
        
        logger.info(f"📊 Found {len(pending_appointments)} appointments to sync")
        
        sync_count = 0
        error_count = 0
        
        for appointment in pending_appointments:
            success = await sync_appointment_to_sheets(appointment)
            if success:
                sync_count += 1
            else:
                error_count += 1
            
            # Small delay to avoid API rate limits
            await asyncio.sleep(0.1)
        
        logger.info(f"✅ Sync completed: {sync_count} successful, {error_count} errors")
        return error_count == 0
        
    except Exception as e:
        logger.error(f"❌ Error in sync process: {str(e)}")
        return False

# Test function
async def test_google_sheets_sync():
    """Test the Google Sheets synchronization"""
    try:
        logger.info("🧪 Testing Google Sheets synchronization...")
        
        # Test authentication
        if google_sync.authenticate():
            logger.info("✅ Authentication successful")
        else:
            logger.error("❌ Authentication failed")
            return False
        
        # Test reading
        data = google_sync.read_sheet_data()
        if data:
            logger.info(f"✅ Successfully read {len(data)} rows")
        else:
            logger.error("❌ Failed to read sheet data")
            return False
        
        logger.info("✅ All tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Run test
    asyncio.run(test_google_sheets_sync())