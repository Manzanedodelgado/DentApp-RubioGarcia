#!/usr/bin/env python3
"""
URGENT GOOGLE SHEETS COLUMN VERIFICATION TEST
============================================

This test specifically addresses the user's urgent request to verify exact column mapping
between expected columns and actual Google Sheets columns.

USER EXPECTATIONS:
- Column D: NumPac  
- Column E: Nombre
- Column F: Apellidos
- Column G: TelMovil
- Column H: Fecha
- Column I: Hora 
- Column J: Estado
- Column K: Tratamiento
- Column L: Doctor

CRITICAL ISSUE: User reports columns "Hora" (Column I) and "Doctor" (Column L) are missing
but testing shows different results. Need exact verification.
"""

import requests
import sys
import json
from datetime import datetime, timezone
import subprocess
import time

class GoogleSheetsColumnTester:
    def __init__(self, base_url="https://dental-sync.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
    def log_message(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def trigger_sync_and_capture_logs(self):
        """Trigger sync and capture backend logs to see exact headers"""
        self.log_message("🚀 TRIGGERING SYNC TO CAPTURE GOOGLE SHEETS HEADERS", "URGENT")
        
        # Step 1: Trigger sync
        try:
            response = requests.post(f"{self.api_url}/appointments/sync", 
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                self.log_message(f"✅ Sync triggered successfully: {response.json()}")
            else:
                self.log_message(f"❌ Sync failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log_message(f"❌ Sync request failed: {str(e)}", "ERROR")
            return False
        
        # Step 2: Wait a moment for sync to complete
        self.log_message("⏳ Waiting for sync to complete...")
        time.sleep(3)
        
        # Step 3: Capture backend logs to find headers
        self.log_message("📋 CAPTURING BACKEND LOGS FOR GOOGLE SHEETS HEADERS")
        try:
            # Get recent backend logs
            result = subprocess.run(['tail', '-n', '100', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logs = result.stdout
                self.log_message("✅ Backend logs captured successfully")
                return self.analyze_logs_for_headers(logs)
            else:
                self.log_message("❌ Failed to capture backend logs", "ERROR")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error capturing logs: {str(e)}", "ERROR")
            return False
    
    def analyze_logs_for_headers(self, logs):
        """Analyze logs to find exact Google Sheets headers"""
        self.log_message("🔍 ANALYZING LOGS FOR GOOGLE SHEETS HEADERS")
        
        # Look for the specific log message that shows headers
        lines = logs.split('\n')
        headers_found = None
        
        for line in lines:
            if "Sheet headers found:" in line:
                self.log_message(f"📋 FOUND HEADERS LOG: {line}")
                # Extract the headers from the log line
                try:
                    # The format should be: "📋 Sheet headers found: ['header1', 'header2', ...]"
                    start_idx = line.find('[')
                    end_idx = line.find(']') + 1
                    if start_idx != -1 and end_idx != -1:
                        headers_str = line[start_idx:end_idx]
                        headers_found = eval(headers_str)  # Convert string representation to list
                        break
                except Exception as e:
                    self.log_message(f"❌ Error parsing headers: {str(e)}", "ERROR")
        
        if headers_found:
            self.log_message("✅ GOOGLE SHEETS HEADERS SUCCESSFULLY EXTRACTED")
            return self.compare_headers_with_expectations(headers_found)
        else:
            self.log_message("❌ NO HEADERS FOUND IN LOGS - May need to check different log source", "ERROR")
            return False
    
    def compare_headers_with_expectations(self, actual_headers):
        """Compare actual headers with user expectations"""
        self.log_message("🎯 COMPARING ACTUAL HEADERS WITH USER EXPECTATIONS")
        
        # User's expected column mapping
        expected_mapping = {
            'D': 'NumPac',
            'E': 'Nombre', 
            'F': 'Apellidos',
            'G': 'TelMovil',
            'H': 'Fecha',
            'I': 'Hora',
            'J': 'Estado',
            'K': 'Tratamiento',
            'L': 'Doctor'
        }
        
        print("\n" + "="*80)
        print("📊 GOOGLE SHEETS COLUMN VERIFICATION RESULTS")
        print("="*80)
        
        print(f"\n📋 ACTUAL HEADERS FOUND IN GOOGLE SHEETS:")
        for i, header in enumerate(actual_headers):
            column_letter = chr(65 + i)  # A=65, B=66, etc.
            print(f"   Column {column_letter}: {header}")
        
        print(f"\n📋 USER EXPECTED HEADERS:")
        for column, expected_header in expected_mapping.items():
            print(f"   Column {column}: {expected_header}")
        
        print(f"\n🔍 COLUMN-BY-COLUMN COMPARISON:")
        
        # Check each expected column
        missing_columns = []
        mismatched_columns = []
        found_columns = []
        
        for expected_column, expected_header in expected_mapping.items():
            column_index = ord(expected_column) - 65  # Convert letter to index (A=0, B=1, etc.)
            
            if column_index < len(actual_headers):
                actual_header = actual_headers[column_index]
                if actual_header == expected_header:
                    print(f"   ✅ Column {expected_column}: '{expected_header}' - MATCH")
                    found_columns.append(expected_column)
                else:
                    print(f"   ❌ Column {expected_column}: Expected '{expected_header}', Found '{actual_header}' - MISMATCH")
                    mismatched_columns.append((expected_column, expected_header, actual_header))
            else:
                print(f"   ❌ Column {expected_column}: Expected '{expected_header}' - MISSING (sheet only has {len(actual_headers)} columns)")
                missing_columns.append((expected_column, expected_header))
        
        # Check for extra columns in the sheet
        extra_columns = []
        if len(actual_headers) > len(expected_mapping):
            for i in range(len(expected_mapping), len(actual_headers)):
                column_letter = chr(65 + i)
                extra_columns.append((column_letter, actual_headers[i]))
        
        # Summary
        print(f"\n📊 VERIFICATION SUMMARY:")
        print(f"   ✅ Matching columns: {len(found_columns)}")
        print(f"   ❌ Mismatched columns: {len(mismatched_columns)}")
        print(f"   ❌ Missing columns: {len(missing_columns)}")
        print(f"   ➕ Extra columns: {len(extra_columns)}")
        
        if mismatched_columns:
            print(f"\n❌ MISMATCHED COLUMNS DETAILS:")
            for column, expected, actual in mismatched_columns:
                print(f"   Column {column}: Expected '{expected}' → Found '{actual}'")
        
        if missing_columns:
            print(f"\n❌ MISSING COLUMNS DETAILS:")
            for column, expected in missing_columns:
                print(f"   Column {column}: Expected '{expected}' → NOT FOUND")
        
        if extra_columns:
            print(f"\n➕ EXTRA COLUMNS FOUND:")
            for column, header in extra_columns:
                print(f"   Column {column}: '{header}'")
        
        # Specific check for user's reported missing columns
        print(f"\n🚨 SPECIFIC CHECK FOR USER'S REPORTED MISSING COLUMNS:")
        
        # Check for "Hora" (Column I)
        hora_found = False
        if 'I' in [col for col, _, _ in mismatched_columns] or 'I' in found_columns:
            hora_found = True
        
        if hora_found or 'Hora' in actual_headers:
            print(f"   ✅ 'Hora' column: FOUND in Google Sheets")
        else:
            print(f"   ❌ 'Hora' column: NOT FOUND in Google Sheets")
        
        # Check for "Doctor" (Column L)  
        doctor_found = False
        if 'L' in [col for col, _, _ in mismatched_columns] or 'L' in found_columns:
            doctor_found = True
        
        if doctor_found or 'Doctor' in actual_headers:
            print(f"   ✅ 'Doctor' column: FOUND in Google Sheets")
        else:
            print(f"   ❌ 'Doctor' column: NOT FOUND in Google Sheets")
        
        return {
            'actual_headers': actual_headers,
            'matching_columns': len(found_columns),
            'mismatched_columns': mismatched_columns,
            'missing_columns': missing_columns,
            'extra_columns': extra_columns,
            'hora_found': hora_found or 'Hora' in actual_headers,
            'doctor_found': doctor_found or 'Doctor' in actual_headers
        }
    
    def get_sample_raw_data(self):
        """Get sample raw data to show what's actually being imported"""
        self.log_message("📊 GETTING SAMPLE RAW DATA FROM APPOINTMENTS")
        
        try:
            # Get first 5 appointments to show raw data
            response = requests.get(f"{self.api_url}/appointments", 
                                  headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                appointments = response.json()
                
                print(f"\n📊 SAMPLE RAW DATA (First 5 appointments):")
                print("="*80)
                
                for i, apt in enumerate(appointments[:5]):
                    print(f"\n📋 Appointment {i+1}:")
                    print(f"   Contact Name: {apt.get('contact_name', 'N/A')}")
                    print(f"   Date: {apt.get('date', 'N/A')}")
                    print(f"   Title: {apt.get('title', 'N/A')}")
                    print(f"   Patient Number: {apt.get('patient_number', 'N/A')}")
                    print(f"   Phone: {apt.get('phone', 'N/A')}")
                    print(f"   Doctor: {apt.get('doctor', 'N/A')}")
                    print(f"   Treatment: {apt.get('treatment', 'N/A')}")
                    print(f"   Time: {apt.get('time', 'N/A')}")
                    print(f"   Status: {apt.get('status', 'N/A')}")
                
                return True
            else:
                self.log_message(f"❌ Failed to get appointments: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error getting sample data: {str(e)}", "ERROR")
            return False
    
    def run_complete_verification(self):
        """Run complete Google Sheets column verification"""
        print("\n" + "="*80)
        print("🚨 URGENT: GOOGLE SHEETS COLUMN VERIFICATION")
        print("="*80)
        print("USER ISSUE: Columns 'Hora' (I) and 'Doctor' (L) reported missing")
        print("TASK: Verify exact column headers in Google Sheets")
        print("="*80)
        
        # Step 1: Trigger sync and capture headers
        success = self.trigger_sync_and_capture_logs()
        
        if not success:
            self.log_message("❌ CRITICAL: Could not capture Google Sheets headers from logs", "ERROR")
            self.log_message("🔄 Attempting alternative method...", "INFO")
            
            # Alternative: Try to get headers from error logs or other sources
            try:
                result = subprocess.run(['grep', '-r', 'headers found', '/var/log/supervisor/'], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout:
                    self.log_message("✅ Found headers in alternative log search")
                    return self.analyze_logs_for_headers(result.stdout)
            except:
                pass
            
            self.log_message("❌ FAILED: Cannot determine exact Google Sheets headers", "CRITICAL")
            return False
        
        # Step 2: Get sample raw data
        self.get_sample_raw_data()
        
        return True

def main():
    """Main function to run the Google Sheets column verification"""
    tester = GoogleSheetsColumnTester()
    
    print("🚨 STARTING URGENT GOOGLE SHEETS COLUMN VERIFICATION")
    print("=" * 80)
    
    success = tester.run_complete_verification()
    
    if success:
        print("\n✅ GOOGLE SHEETS COLUMN VERIFICATION COMPLETED")
    else:
        print("\n❌ GOOGLE SHEETS COLUMN VERIFICATION FAILED")
        print("🚨 CRITICAL: Cannot determine exact column mapping")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)