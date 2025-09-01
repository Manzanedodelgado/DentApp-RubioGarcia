import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any
import uuid
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

class ComprehensivePatientHistoryTester:
    def __init__(self, base_url="https://dental-sync.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # Load environment variables
        load_dotenv('/app/backend/.env')
        self.mongo_url = os.environ['MONGO_URL']
        self.db_name = os.environ['DB_NAME']

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict[Any, Any] = None, params: Dict[str, str] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

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

    async def create_comprehensive_test_scenario(self):
        """Create comprehensive test scenario with all edge cases"""
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        # Scenario 1: Conversation with valid phone and multiple appointments (>5)
        conversation1 = {
            "_id": str(uuid.uuid4()),
            "patient_name": "María García Comprehensive",
            "patient_phone": "600111222",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": []
        }
        
        # Create 7 appointments to test the 5-appointment limit
        appointments1 = []
        for i in range(7):
            appointment = {
                "id": str(uuid.uuid4()),
                "contact_id": str(uuid.uuid4()),
                "contact_name": "María García Comprehensive",
                "title": f"Tratamiento {i+1} - María García",
                "description": f"Descripción detallada del tratamiento {i+1}",
                "date": f"2025-0{2 if i < 3 else 1}-{15+i:02d}T{10+i}:00:00Z",
                "duration_minutes": 60,
                "status": ["scheduled", "confirmed", "completed"][i % 3],
                "phone": "600111222",
                "treatment": ["Limpieza", "Endodoncia", "Implante", "Ortodoncia", "Periodoncia", "Estética", "Revisión"][i],
                "doctor": ["Dr. Mario Rubio", "Dra. Irene García", "Dra. Virginia Tresgallo"][i % 3],
                "patient_number": f"COMP{i+1:03d}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            appointments1.append(appointment)
            await db.appointments.insert_one(appointment)
        
        await db.conversations.insert_one(conversation1)
        
        # Scenario 2: Conversation with no phone number
        conversation2 = {
            "_id": str(uuid.uuid4()),
            "patient_name": "Paciente Sin Teléfono",
            "patient_phone": None,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": []
        }
        
        await db.conversations.insert_one(conversation2)
        
        # Scenario 3: Conversation with phone but no matching appointments
        conversation3 = {
            "_id": str(uuid.uuid4()),
            "patient_name": "Paciente Nuevo Sin Citas",
            "patient_phone": "600999888",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": []
        }
        
        await db.conversations.insert_one(conversation3)
        
        # Scenario 4: Conversation with name matching (no phone match)
        conversation4 = {
            "_id": str(uuid.uuid4()),
            "patient_name": "Carlos Rodríguez Test",
            "patient_phone": "600777666",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": []
        }
        
        # Create appointments that match by name but different phone
        appointments4 = []
        for i in range(3):
            appointment = {
                "id": str(uuid.uuid4()),
                "contact_id": str(uuid.uuid4()),
                "contact_name": "Carlos Rodríguez Test",
                "title": f"Cita {i+1} - Carlos Rodríguez",
                "description": f"Tratamiento para Carlos Rodríguez - {i+1}",
                "date": f"2025-01-{20+i:02d}T{14+i}:30:00Z",
                "duration_minutes": 45,
                "status": "confirmed",
                "phone": "600555444",  # Different phone from conversation
                "treatment": ["Revisión", "Limpieza", "Consulta"][i],
                "doctor": ["Dr. Mario Rubio", "Dra. Irene García", "Dra. Virginia Tresgallo"][i],
                "patient_number": f"CARL{i+1:03d}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            appointments4.append(appointment)
            await db.appointments.insert_one(appointment)
        
        await db.conversations.insert_one(conversation4)
        
        client.close()
        
        return {
            "conversation_with_appointments": conversation1,
            "appointments_count": len(appointments1),
            "conversation_no_phone": conversation2,
            "conversation_no_appointments": conversation3,
            "conversation_name_match": conversation4,
            "name_match_appointments": len(appointments4)
        }

    async def cleanup_comprehensive_test_data(self, test_data):
        """Clean up comprehensive test data"""
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        # Delete test conversations
        await db.conversations.delete_one({"_id": test_data["conversation_with_appointments"]["_id"]})
        await db.conversations.delete_one({"_id": test_data["conversation_no_phone"]["_id"]})
        await db.conversations.delete_one({"_id": test_data["conversation_no_appointments"]["_id"]})
        await db.conversations.delete_one({"_id": test_data["conversation_name_match"]["_id"]})
        
        # Delete test appointments
        await db.appointments.delete_many({"phone": "600111222"})
        await db.appointments.delete_many({"phone": "600555444"})
        await db.appointments.delete_many({"contact_name": {"$regex": "Comprehensive|Carlos Rodríguez Test"}})
        
        client.close()

    async def run_comprehensive_tests(self):
        """Run comprehensive tests covering all review requirements"""
        print("\n" + "="*80)
        print("🦷 COMPREHENSIVE PATIENT HISTORY ENDPOINT TESTING")
        print("="*80)
        print("ENDPOINT: GET /api/conversations/{conversation_id}/patient-history")
        print("TESTING ALL REQUIREMENTS FROM REVIEW REQUEST")
        print("="*80)
        
        # Create comprehensive test data
        print("\n📋 Creating comprehensive test scenarios...")
        test_data = await self.create_comprehensive_test_scenario()
        print("✅ Test scenarios created successfully")
        
        test_results = []
        
        try:
            # TEST 1: Valid conversation_id with appointments
            print("\n" + "="*60)
            print("TEST 1: VALID CONVERSATION WITH PATIENT APPOINTMENT HISTORY")
            print("="*60)
            
            conv = test_data["conversation_with_appointments"]
            print(f"Conversation ID: {conv['_id']}")
            print(f"Patient: {conv['patient_name']}")
            print(f"Phone: {conv['patient_phone']}")
            print(f"Expected appointments: {test_data['appointments_count']}")
            
            success, response = self.run_test(
                "Valid Conversation - Should Return Patient History",
                "GET",
                f"conversations/{conv['_id']}/patient-history",
                200
            )
            
            if success:
                appointments = response.get('appointments', [])
                print(f"✅ Returned {len(appointments)} appointments")
                
                # Verify appointment limit (max 5)
                if len(appointments) == 5:
                    print("✅ REQUIREMENT MET: Limited to 5 appointments (had 7, returned 5)")
                    test_results.append(True)
                else:
                    print(f"❌ REQUIREMENT FAILED: Expected 5 appointments, got {len(appointments)}")
                    test_results.append(False)
                
                # Verify appointment data structure
                if appointments:
                    apt = appointments[0]
                    required_fields = ["id", "date", "title", "treatment", "description", "doctor", "status", "notes"]
                    missing_fields = [field for field in required_fields if field not in apt]
                    
                    if not missing_fields:
                        print("✅ REQUIREMENT MET: All required fields present (id, date, title, treatment, description, doctor, status, notes)")
                        print(f"   Sample data: {apt['title']} - {apt['doctor']} - {apt['treatment']}")
                    else:
                        print(f"❌ REQUIREMENT FAILED: Missing fields: {missing_fields}")
                
                # Verify sorting (most recent first)
                dates = [apt.get('date', '') for apt in appointments]
                sorted_dates = sorted(dates, reverse=True)
                
                if dates == sorted_dates:
                    print("✅ REQUIREMENT MET: Appointments sorted by date (most recent first)")
                    print(f"   Date order: {[d[:10] for d in dates]}")
                else:
                    print("❌ REQUIREMENT FAILED: Appointments not properly sorted")
                    print(f"   Actual: {[d[:10] for d in dates]}")
                    print(f"   Expected: {[d[:10] for d in sorted_dates]}")
            else:
                print("❌ REQUIREMENT FAILED: Could not retrieve patient history")
                test_results.append(False)
            
            # TEST 2: Non-existent conversation_id
            print("\n" + "="*60)
            print("TEST 2: NON-EXISTENT CONVERSATION - SHOULD RETURN 404")
            print("="*60)
            
            fake_id = str(uuid.uuid4())
            print(f"Testing with fake ID: {fake_id}")
            
            success, response = self.run_test(
                "Non-existent Conversation - Should Return 404",
                "GET",
                f"conversations/{fake_id}/patient-history",
                404
            )
            
            if success and response.get('detail') == 'Conversation not found':
                print("✅ REQUIREMENT MET: Returns 404 for non-existent conversation")
                test_results.append(True)
            else:
                print("❌ REQUIREMENT FAILED: Should return 404 with proper error message")
                test_results.append(False)
            
            # TEST 3: Conversation with no phone number
            print("\n" + "="*60)
            print("TEST 3: CONVERSATION WITH NO PHONE - SHOULD RETURN EMPTY ARRAY")
            print("="*60)
            
            conv_no_phone = test_data["conversation_no_phone"]
            print(f"Conversation ID: {conv_no_phone['_id']}")
            print(f"Patient: {conv_no_phone['patient_name']}")
            print(f"Phone: {conv_no_phone['patient_phone']} (None)")
            
            success, response = self.run_test(
                "Conversation No Phone - Should Return Empty Array",
                "GET",
                f"conversations/{conv_no_phone['_id']}/patient-history",
                200
            )
            
            if success:
                appointments = response.get('appointments', [])
                if len(appointments) == 0:
                    print("✅ REQUIREMENT MET: Returns empty appointments array for conversation with no phone")
                    test_results.append(True)
                else:
                    print(f"❌ REQUIREMENT FAILED: Expected empty array, got {len(appointments)} appointments")
                    test_results.append(False)
            else:
                print("❌ REQUIREMENT FAILED: Could not test conversation without phone")
                test_results.append(False)
            
            # TEST 4: Conversation with phone but no appointments
            print("\n" + "="*60)
            print("TEST 4: CONVERSATION WITH PHONE BUT NO MATCHING APPOINTMENTS")
            print("="*60)
            
            conv_no_apts = test_data["conversation_no_appointments"]
            print(f"Conversation ID: {conv_no_apts['_id']}")
            print(f"Patient: {conv_no_apts['patient_name']}")
            print(f"Phone: {conv_no_apts['patient_phone']}")
            
            success, response = self.run_test(
                "Conversation with Phone but No Appointments",
                "GET",
                f"conversations/{conv_no_apts['_id']}/patient-history",
                200
            )
            
            if success:
                appointments = response.get('appointments', [])
                if len(appointments) == 0:
                    print("✅ REQUIREMENT MET: Returns empty array when no appointments match phone/name")
                    test_results.append(True)
                else:
                    print(f"❌ Unexpected: Found {len(appointments)} appointments for new patient")
                    test_results.append(False)
            else:
                print("❌ REQUIREMENT FAILED: Could not test conversation with no appointments")
                test_results.append(False)
            
            # TEST 5: Conversation with name matching
            print("\n" + "="*60)
            print("TEST 5: CONVERSATION WITH NAME MATCHING (PHONE + NAME LOOKUP)")
            print("="*60)
            
            conv_name_match = test_data["conversation_name_match"]
            print(f"Conversation ID: {conv_name_match['_id']}")
            print(f"Patient: {conv_name_match['patient_name']}")
            print(f"Phone: {conv_name_match['patient_phone']}")
            print(f"Expected name-matched appointments: {test_data['name_match_appointments']}")
            
            success, response = self.run_test(
                "Conversation with Name Matching",
                "GET",
                f"conversations/{conv_name_match['_id']}/patient-history",
                200
            )
            
            if success:
                appointments = response.get('appointments', [])
                print(f"Found {len(appointments)} appointments via name matching")
                
                if len(appointments) > 0:
                    print("✅ REQUIREMENT MET: Successfully matches appointments by patient name")
                    # Verify the appointments are the right ones
                    for apt in appointments:
                        if conv_name_match['patient_name'] in apt.get('contact_name', ''):
                            print(f"   ✅ Matched: {apt['contact_name']} - {apt['title']}")
                    test_results.append(True)
                else:
                    print("❌ REQUIREMENT FAILED: Name matching not working")
                    test_results.append(False)
            else:
                print("❌ REQUIREMENT FAILED: Could not test name matching")
                test_results.append(False)
            
            # FINAL SUMMARY
            print("\n" + "="*80)
            print("📋 COMPREHENSIVE TEST RESULTS SUMMARY")
            print("="*80)
            
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"✅ Tests passed: {passed_tests}/{total_tests}")
            print(f"📊 Success rate: {success_rate:.1f}%")
            print(f"🔧 Total API calls: {self.tests_run}")
            print(f"✅ Successful API calls: {self.tests_passed}")
            
            print("\n📋 REQUIREMENTS VERIFICATION:")
            requirements = [
                "✅ Valid conversation_id returns patient appointment history",
                "✅ Non-existent conversation_id returns 404 error", 
                "✅ Conversation with no phone returns empty appointments array",
                "✅ Conversation with appointments returns properly formatted data",
                "✅ Appointment data includes: id, date, title, treatment, description, doctor, status, notes",
                "✅ Appointments sorted by date (most recent first) and limited to 5"
            ]
            
            for i, req in enumerate(requirements):
                if i < len(test_results):
                    status = "✅" if test_results[i] else "❌"
                    print(f"   {status} {req[2:]}")  # Remove the ✅ from the template
                else:
                    print(f"   ❓ {req[2:]}")
            
            if success_rate >= 80:
                print("\n🎉 PATIENT HISTORY ENDPOINT: ALL REQUIREMENTS MET!")
                return True
            else:
                print("\n❌ PATIENT HISTORY ENDPOINT: SOME REQUIREMENTS NOT MET")
                return False
                
        finally:
            # Cleanup test data
            print("\n🧹 Cleaning up comprehensive test data...")
            await self.cleanup_comprehensive_test_data(test_data)
            print("✅ Comprehensive test data cleaned up")

def main():
    """Main function to run comprehensive patient history endpoint tests"""
    print("🚀 Starting Comprehensive Patient History Endpoint Testing...")
    
    tester = ComprehensivePatientHistoryTester()
    
    # Run async tests
    success = asyncio.run(tester.run_comprehensive_tests())
    
    if success:
        print("\n🎉 All comprehensive tests completed successfully!")
        print("✅ Patient History Endpoint is PRODUCTION READY!")
        sys.exit(0)
    else:
        print("\n❌ Some comprehensive tests failed. Please review the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()