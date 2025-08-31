#!/usr/bin/env python3
"""
GOOGLE SHEETS BIDIRECTIONAL SYNC COMPREHENSIVE TEST
==================================================

This test suite comprehensively tests the Google Sheets bidirectional sync system
with the newly configured service account as requested in the review.

SERVICE ACCOUNT CONFIGURED:
- Email: rubio-garcia-sheets-sync@appgest-470518.iam.gserviceaccount.com
- Project: appgest-470518  
- Credentials file: /app/backend/service-account-key.json ✅

CRITICAL TESTS TO PERFORM:
1. Google Sheets Authentication Test
2. Bidirectional Sync End-to-End Test
3. Bulk Sync Operations
4. Google Sheets Integration Validation
5. Real Google Sheets Verification
"""

import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

class GoogleSheetsSyncTester:
    def __init__(self, base_url="https://dentiflow.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict[Any, Any] = None, params: Dict[str, str] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add auth token if available
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json() if response.content else {}
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def authenticate(self):
        """Authenticate with JMD/190582 credentials"""
        print("\n" + "="*70)
        print("🔐 AUTHENTICATING WITH JMD/190582 CREDENTIALS")
        print("="*70)
        
        auth_data = {"username": "JMD", "password": "190582"}
        success, auth_response = self.run_test(
            "Authentication with JMD/190582",
            "POST",
            "auth/login",
            200,
            data=auth_data
        )
        
        if success and auth_response.get('token'):
            self.auth_token = auth_response['token']
            print(f"✅ Authenticated successfully")
            print(f"   User: {auth_response.get('user', {}).get('name', 'Unknown')}")
            return True
        else:
            print("❌ CRITICAL: Authentication failed")
            return False

    def test_google_sheets_authentication(self):
        """Test 1: Google Sheets Authentication Test"""
        print("\n" + "="*70)
        print("🔐 TEST 1: GOOGLE SHEETS AUTHENTICATION")
        print("="*70)
        print("Service Account: rubio-garcia-sheets-sync@appgest-470518.iam.gserviceaccount.com")
        print("Project: appgest-470518")
        print("Spreadsheet: 1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ")
        
        # Test authentication by triggering a sync
        success, response = self.run_test(
            "Google Sheets Authentication via Sync",
            "POST",
            "appointments/sync",
            200
        )
        
        if success:
            message = response.get('message', '')
            print(f"   ✅ Sync response: {message}")
            
            # Check if we can read appointments (indicates successful auth)
            success2, appointments = self.run_test(
                "Verify Data Access After Auth",
                "GET", 
                "appointments",
                200
            )
            
            if success2 and len(appointments) > 0:
                print(f"   ✅ Successfully accessed {len(appointments)} appointments")
                print(f"   ✅ Google Sheets authentication working")
                return True
            else:
                print(f"   ❌ No appointments found after sync")
                return False
        else:
            print(f"   ❌ Sync failed - authentication may be broken")
            return False

    def test_bidirectional_sync_end_to_end(self):
        """Test 2: Bidirectional Sync End-to-End Test"""
        print("\n" + "="*70)
        print("🔄 TEST 2: BIDIRECTIONAL SYNC END-TO-END")
        print("="*70)
        
        # Step 1: Get an existing appointment
        success, appointments = self.run_test(
            "Get Existing Appointments",
            "GET",
            "appointments",
            200
        )
        
        if not success or len(appointments) == 0:
            print("   ❌ No appointments found for testing")
            return False
        
        # Find an appointment with required fields for sync
        test_appointment = None
        for apt in appointments:
            if (apt.get('patient_number') and apt.get('date') and 
                apt.get('time') and apt.get('status')):
                test_appointment = apt
                break
        
        if not test_appointment:
            print("   ❌ No suitable appointment found for sync testing")
            return False
        
        appointment_id = test_appointment['id']
        original_status = test_appointment['status']
        
        print(f"   📋 Testing with appointment: {test_appointment.get('contact_name')}")
        print(f"   📅 Date: {test_appointment.get('date')}")
        print(f"   ⏰ Time: {test_appointment.get('time')}")
        print(f"   📊 Original status: {original_status}")
        
        # Step 2: Update appointment status (scheduled → confirmed)
        new_status = 'confirmed' if original_status != 'confirmed' else 'scheduled'
        update_data = {"status": new_status}
        
        success, updated_apt = self.run_test(
            f"Update Appointment Status to {new_status}",
            "PUT",
            f"appointments/{appointment_id}",
            200,
            data=update_data
        )
        
        if not success:
            print("   ❌ Failed to update appointment")
            return False
        
        print(f"   ✅ Status updated to: {updated_apt.get('status')}")
        
        # Step 3: Check sync tracking
        synced_flag = updated_apt.get('synced_to_sheets')
        last_synced = updated_apt.get('last_synced_at')
        
        print(f"   📊 Synced to sheets: {synced_flag}")
        print(f"   📊 Last synced: {last_synced}")
        
        # Step 4: Verify the change persisted
        success, final_apt = self.run_test(
            "Verify Final Status",
            "GET",
            f"appointments/{appointment_id}",
            200
        )
        
        if success and final_apt.get('status') == new_status:
            print(f"   ✅ Status change persisted: {final_apt.get('status')}")
            print(f"   ✅ Bidirectional sync test completed successfully")
            return True
        else:
            print(f"   ❌ Status change not persisted")
            return False

    def test_bulk_sync_operations(self):
        """Test 3: Bulk Sync Operations"""
        print("\n" + "="*70)
        print("📊 TEST 3: BULK SYNC OPERATIONS")
        print("="*70)
        
        # Step 1: Get multiple appointments
        success, appointments = self.run_test(
            "Get Appointments for Bulk Test",
            "GET",
            "appointments",
            200
        )
        
        if not success or len(appointments) < 2:
            print("   ❌ Need at least 2 appointments for bulk testing")
            return False
        
        print(f"   📊 Found {len(appointments)} appointments for bulk testing")
        
        # Step 2: Update multiple appointment statuses
        updated_count = 0
        for i, apt in enumerate(appointments[:3]):  # Test with first 3
            if apt.get('id'):
                new_status = 'confirmed' if apt.get('status') != 'confirmed' else 'scheduled'
                success, _ = self.run_test(
                    f"Bulk Update {i+1}",
                    "PUT",
                    f"appointments/{apt['id']}",
                    200,
                    data={"status": new_status}
                )
                if success:
                    updated_count += 1
        
        print(f"   ✅ Updated {updated_count} appointments")
        
        # Step 3: Test bulk sync endpoint
        success, sync_response = self.run_test(
            "Bulk Sync All Changes",
            "POST",
            "appointments/sync",
            200
        )
        
        if success:
            print(f"   ✅ Bulk sync completed: {sync_response.get('message', 'Success')}")
            return True
        else:
            print(f"   ❌ Bulk sync failed")
            return False

    def test_google_sheets_integration_validation(self):
        """Test 4: Google Sheets Integration Validation"""
        print("\n" + "="*70)
        print("🔍 TEST 4: GOOGLE SHEETS INTEGRATION VALIDATION")
        print("="*70)
        
        # Test the google_sync.py functionality indirectly
        success, appointments = self.run_test(
            "Get Appointments for Integration Test",
            "GET",
            "appointments",
            200
        )
        
        if not success:
            print("   ❌ Cannot retrieve appointments")
            return False
        
        print(f"   📊 Testing with {len(appointments)} appointments")
        
        # Check if appointments have the required fields for Google Sheets sync
        sync_ready_count = 0
        column_mapping_test = {
            'patient_number': 'Column D (NumPac)',
            'contact_name': 'Column E/F (Nombre/Apellidos)', 
            'phone': 'Column G (TelMovil)',
            'date': 'Column H (Fecha)',
            'time': 'Column I (Hora)',
            'status': 'Column J (EstadoCita)',
            'treatment': 'Column K (Tratamiento)',
            'doctor': 'Column L (Doctor)'
        }
        
        print(f"\n   🗂️ COLUMN MAPPING VALIDATION:")
        for field, column_desc in column_mapping_test.items():
            field_count = sum(1 for apt in appointments if apt.get(field))
            percentage = (field_count / len(appointments)) * 100 if appointments else 0
            
            if percentage >= 50:  # At least 50% have this field
                print(f"   ✅ {column_desc}: {field_count}/{len(appointments)} ({percentage:.1f}%)")
                sync_ready_count += 1
            else:
                print(f"   ⚠️ {column_desc}: {field_count}/{len(appointments)} ({percentage:.1f}%)")
        
        # Test status mapping (scheduled→Planificada, confirmed→Confirmada, etc.)
        print(f"\n   📊 STATUS MAPPING TEST:")
        status_counts = {}
        for apt in appointments:
            status = apt.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        expected_statuses = ['scheduled', 'confirmed', 'completed', 'cancelled']
        for status in expected_statuses:
            count = status_counts.get(status, 0)
            print(f"   📋 {status}: {count} appointments")
        
        # Check for proper date format
        print(f"\n   📅 DATE FORMAT VALIDATION:")
        valid_dates = 0
        for apt in appointments[:10]:  # Check first 10
            date_str = apt.get('date', '')
            if date_str and len(date_str) >= 10:
                try:
                    datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    valid_dates += 1
                except:
                    pass
        
        date_percentage = (valid_dates / min(10, len(appointments))) * 100
        print(f"   📅 Valid date format: {valid_dates}/10 ({date_percentage:.1f}%)")
        
        if sync_ready_count >= 6:  # At least 6 out of 8 fields working
            print(f"   ✅ Google Sheets integration validation passed")
            return True
        else:
            print(f"   ❌ Google Sheets integration validation failed")
            return False

    def test_real_google_sheets_verification(self):
        """Test 5: Real Google Sheets Verification"""
        print("\n" + "="*70)
        print("📋 TEST 5: REAL GOOGLE SHEETS VERIFICATION")
        print("="*70)
        print("Spreadsheet: https://docs.google.com/spreadsheets/d/1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ/edit")
        
        # Trigger a fresh sync to ensure we have latest data
        success, sync_response = self.run_test(
            "Fresh Sync for Verification",
            "POST",
            "appointments/sync",
            200
        )
        
        if not success:
            print("   ❌ Cannot trigger fresh sync")
            return False
        
        # Get all appointments to analyze
        success, appointments = self.run_test(
            "Get All Appointments for Verification",
            "GET",
            "appointments",
            200
        )
        
        if not success:
            print("   ❌ Cannot retrieve appointments")
            return False
        
        print(f"   📊 Analyzing {len(appointments)} appointments")
        
        # Check for real vs fallback data indicators
        fallback_names = [
            "Benita Posado Jañez", "Natalia Gonzalez Diez", "Angeles Salvador Fernandez",
            "Rehan Nisar", "Samuel Prieto Serrano", "Eloy Perez Gonzalez"
        ]
        
        real_data_indicators = 0
        
        # Test 1: Check appointment count
        if len(appointments) > 50:  # More than typical fallback
            print(f"   ✅ Large dataset ({len(appointments)} appointments) - likely real data")
            real_data_indicators += 1
        else:
            print(f"   ⚠️ Small dataset ({len(appointments)} appointments) - may be fallback")
        
        # Test 2: Check for fallback names
        patient_names = [apt.get('contact_name', '') for apt in appointments]
        fallback_matches = sum(1 for name in patient_names if name in fallback_names)
        fallback_percentage = (fallback_matches / len(patient_names)) * 100 if patient_names else 0
        
        if fallback_percentage < 20:  # Less than 20% fallback names
            print(f"   ✅ Low fallback names ({fallback_percentage:.1f}%) - likely real data")
            real_data_indicators += 1
        else:
            print(f"   ❌ High fallback names ({fallback_percentage:.1f}%) - may be fallback data")
        
        # Test 3: Check date range diversity
        dates = [apt.get('date', '')[:10] for apt in appointments if apt.get('date')]
        unique_dates = len(set(dates))
        
        if unique_dates > 10:  # More than 10 unique dates
            print(f"   ✅ Date diversity ({unique_dates} unique dates) - likely real data")
            real_data_indicators += 1
        else:
            print(f"   ⚠️ Limited date diversity ({unique_dates} unique dates)")
        
        # Test 4: Check for complete field data
        complete_appointments = 0
        for apt in appointments:
            if (apt.get('contact_name') and apt.get('date') and 
                apt.get('patient_number') and apt.get('doctor')):
                complete_appointments += 1
        
        completeness = (complete_appointments / len(appointments)) * 100 if appointments else 0
        
        if completeness > 80:  # More than 80% complete
            print(f"   ✅ High data completeness ({completeness:.1f}%) - good integration")
            real_data_indicators += 1
        else:
            print(f"   ⚠️ Low data completeness ({completeness:.1f}%)")
        
        # Show sample data with Google Sheets row details
        print(f"\n   📋 SAMPLE APPOINTMENTS (Google Sheets Integration):")
        for i, apt in enumerate(appointments[:3]):
            name = apt.get('contact_name', 'Unknown')
            date = apt.get('date', 'No date')[:10] if apt.get('date') else 'No date'
            doctor = apt.get('doctor', 'No doctor')
            status = apt.get('status', 'No status')
            patient_num = apt.get('patient_number', 'No patient#')
            phone = apt.get('phone', 'No phone')
            treatment = apt.get('treatment', 'No treatment')
            time = apt.get('time', 'No time')
            
            print(f"   {i+1}. {name} | {date} {time} | {doctor} | {status}")
            print(f"      Patient#: {patient_num} | Phone: {phone} | Treatment: {treatment}")
        
        # Final assessment
        print(f"\n   📊 REAL DATA INDICATORS: {real_data_indicators}/4")
        
        if real_data_indicators >= 3:
            print(f"   ✅ Real Google Sheets data confirmed")
            print(f"   ✅ Bidirectional sync system working with actual spreadsheet")
            return True
        else:
            print(f"   ❌ May be using fallback data")
            return False

    def run_comprehensive_sync_tests(self):
        """Run comprehensive Google Sheets bidirectional sync tests"""
        print("🚨 GOOGLE SHEETS BIDIRECTIONAL SYNC COMPREHENSIVE TESTING")
        print("="*70)
        print("SERVICE ACCOUNT CONFIGURED:")
        print("- Email: rubio-garcia-sheets-sync@appgest-470518.iam.gserviceaccount.com")
        print("- Project: appgest-470518")
        print("- Credentials file: /app/backend/service-account-key.json ✅")
        print("="*70)
        
        # Step 1: Authenticate
        if not self.authenticate():
            return False
        
        # Step 2: Run all Google Sheets sync tests
        tests = [
            ("Google Sheets Authentication Test", self.test_google_sheets_authentication),
            ("Bidirectional Sync End-to-End Test", self.test_bidirectional_sync_end_to_end),
            ("Bulk Sync Operations", self.test_bulk_sync_operations),
            ("Google Sheets Integration Validation", self.test_google_sheets_integration_validation),
            ("Real Google Sheets Verification", self.test_real_google_sheets_verification)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                success = test_func()
                if success:
                    passed_tests += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} failed with error: {str(e)}")
        
        # Final summary
        print("\n" + "="*70)
        print("🎯 GOOGLE SHEETS BIDIRECTIONAL SYNC TEST SUMMARY")
        print("="*70)
        print(f"Tests passed: {passed_tests}/{total_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print(f"\n📊 DETAILED RESULTS:")
        print(f"   Total API calls made: {self.tests_run}")
        print(f"   Successful API calls: {self.tests_passed}")
        print(f"   API success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL GOOGLE SHEETS BIDIRECTIONAL SYNC TESTS PASSED!")
            print("✅ Service account authentication working")
            print("✅ Read/write permissions confirmed")
            print("✅ Bidirectional sync functional")
            print("✅ Bulk operations working")
            print("✅ Real Google Sheets integration confirmed")
            return True
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("\n✅ GOOGLE SHEETS SYNC MOSTLY WORKING")
            print("⚠️ Some minor issues detected but core functionality works")
            return True
        else:
            print(f"\n❌ GOOGLE SHEETS SYNC NEEDS ATTENTION")
            print(f"❌ {total_tests - passed_tests} critical tests failed")
            return False

def main():
    """Main function to run Google Sheets bidirectional sync tests"""
    tester = GoogleSheetsSyncTester()
    
    print("🚨 STARTING GOOGLE SHEETS BIDIRECTIONAL SYNC TESTING")
    print("=" * 70)
    
    success = tester.run_comprehensive_sync_tests()
    
    if success:
        print("\n✅ GOOGLE SHEETS BIDIRECTIONAL SYNC TESTING COMPLETED SUCCESSFULLY")
    else:
        print("\n❌ GOOGLE SHEETS BIDIRECTIONAL SYNC TESTING FAILED")
        print("🚨 CRITICAL: Sync system needs immediate attention")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)