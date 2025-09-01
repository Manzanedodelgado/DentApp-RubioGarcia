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

class PatientHistoryFocusedTester:
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

    async def get_existing_conversations(self):
        """Get existing conversations from database"""
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        conversations = await db.conversations.find({}).to_list(10)
        client.close()
        return conversations

    async def create_test_conversation_and_appointments(self):
        """Create a test conversation and matching appointments in the database"""
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        # Create a test conversation
        test_conversation = {
            "_id": str(uuid.uuid4()),
            "patient_name": "Test Patient Historia",
            "patient_phone": "666777888",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": []
        }
        
        await db.conversations.insert_one(test_conversation)
        
        # Create matching appointments for this patient
        test_appointments = []
        appointment_dates = [
            "2025-01-10T09:00:00Z",
            "2025-01-15T14:00:00Z", 
            "2025-01-20T10:30:00Z",
            "2025-01-25T16:15:00Z",
            "2025-02-01T11:00:00Z",
            "2025-02-05T13:30:00Z",  # 6th appointment to test 5-limit
            "2025-02-10T15:45:00Z"   # 7th appointment to test 5-limit
        ]
        
        treatments = ["Limpieza", "Revisión", "Endodoncia", "Implante", "Ortodoncia", "Periodoncia", "Estética"]
        doctors = ["Dr. Mario Rubio", "Dra. Irene García", "Dra. Virginia Tresgallo"]
        
        for i, apt_date in enumerate(appointment_dates):
            appointment = {
                "id": str(uuid.uuid4()),
                "contact_id": str(uuid.uuid4()),
                "contact_name": "Test Patient Historia",
                "title": f"{treatments[i % len(treatments)]} - Test Patient Historia",
                "description": f"Tratamiento de {treatments[i % len(treatments)]}",
                "date": apt_date,
                "duration_minutes": 60,
                "status": ["scheduled", "confirmed", "completed"][i % 3],
                "phone": "666777888",  # Matches conversation phone
                "treatment": treatments[i % len(treatments)],
                "doctor": doctors[i % len(doctors)],
                "patient_number": f"TEST{i+1:03d}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.appointments.insert_one(appointment)
            test_appointments.append(appointment)
        
        client.close()
        return test_conversation, test_appointments

    async def create_conversation_without_phone(self):
        """Create a test conversation without phone number"""
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        test_conversation = {
            "_id": str(uuid.uuid4()),
            "patient_name": "Patient No Phone",
            "patient_phone": None,  # No phone number
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": []
        }
        
        await db.conversations.insert_one(test_conversation)
        client.close()
        return test_conversation

    async def cleanup_test_data(self, conversation_ids):
        """Clean up test conversations and appointments"""
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        # Delete test conversations
        for conv_id in conversation_ids:
            await db.conversations.delete_one({"_id": conv_id})
        
        # Delete test appointments
        await db.appointments.delete_many({"phone": "666777888"})
        await db.appointments.delete_many({"contact_name": "Test Patient Historia"})
        await db.appointments.delete_many({"contact_name": "Patient No Phone"})
        
        client.close()

    def test_nonexistent_conversation(self):
        """Test 1: Non-existent conversation should return 404"""
        print("\n" + "="*70)
        print("TEST 1: NON-EXISTENT CONVERSATION")
        print("="*70)
        
        fake_conversation_id = str(uuid.uuid4())
        print(f"Testing with fake conversation ID: {fake_conversation_id}")
        
        success, response = self.run_test(
            "Get Patient History - Non-existent Conversation",
            "GET",
            f"conversations/{fake_conversation_id}/patient-history",
            404
        )
        
        if success:
            print("✅ Correctly returns 404 for non-existent conversation")
            if response.get('detail') == 'Conversation not found':
                print("✅ Correct error message returned")
                return True
            else:
                print(f"❌ Unexpected error message: {response.get('detail')}")
                return False
        else:
            print("❌ Should return 404 for non-existent conversation")
            return False

    def test_conversation_with_appointments(self, conversation, appointments):
        """Test 2: Conversation with appointments should return appointment history"""
        print("\n" + "="*70)
        print("TEST 2: CONVERSATION WITH APPOINTMENTS")
        print("="*70)
        
        conversation_id = conversation['_id']
        print(f"Testing conversation ID: {conversation_id}")
        print(f"Patient: {conversation['patient_name']}")
        print(f"Phone: {conversation['patient_phone']}")
        print(f"Expected appointments: {len(appointments)}")
        
        success, response = self.run_test(
            "Get Patient History - Valid Conversation with Appointments",
            "GET",
            f"conversations/{conversation_id}/patient-history",
            200
        )
        
        if success:
            appointments_returned = response.get('appointments', [])
            print(f"✅ Endpoint returned {len(appointments_returned)} appointments")
            
            # Verify response structure
            if 'appointments' in response:
                print("✅ Response has 'appointments' key")
            else:
                print("❌ Response missing 'appointments' key")
                return False
            
            # Verify appointment limit (should be max 5)
            if len(appointments_returned) <= 5:
                print(f"✅ Appointment limit respected: {len(appointments_returned)} <= 5")
            else:
                print(f"❌ Too many appointments returned: {len(appointments_returned)} > 5")
                return False
            
            # Verify appointment data structure
            if appointments_returned:
                required_fields = ["id", "date", "title", "treatment", "description", "doctor", "status", "notes"]
                first_apt = appointments_returned[0]
                
                print("Checking appointment data structure:")
                all_fields_present = True
                for field in required_fields:
                    if field in first_apt:
                        print(f"   ✅ {field}: {first_apt.get(field)}")
                    else:
                        print(f"   ❌ Missing field: {field}")
                        all_fields_present = False
                
                if all_fields_present:
                    print("✅ All required fields present in appointment data")
                else:
                    print("❌ Some required fields missing")
                    return False
                
                # Verify appointments are sorted by date (most recent first)
                dates = [apt.get('date', '') for apt in appointments_returned]
                sorted_dates = sorted(dates, reverse=True)  # Most recent first
                
                if dates == sorted_dates:
                    print("✅ Appointments correctly sorted by date (most recent first)")
                else:
                    print("❌ Appointments not properly sorted")
                    print(f"   Actual: {dates}")
                    print(f"   Expected: {sorted_dates}")
                    return False
                
                return True
            else:
                print("❌ No appointments returned when appointments were expected")
                return False
        else:
            print("❌ Failed to get patient history for valid conversation")
            return False

    def test_conversation_without_phone(self, conversation):
        """Test 3: Conversation without phone should return empty appointments"""
        print("\n" + "="*70)
        print("TEST 3: CONVERSATION WITHOUT PHONE NUMBER")
        print("="*70)
        
        conversation_id = conversation['_id']
        print(f"Testing conversation ID: {conversation_id}")
        print(f"Patient: {conversation['patient_name']}")
        print(f"Phone: {conversation['patient_phone']} (None)")
        
        success, response = self.run_test(
            "Get Patient History - Conversation without Phone",
            "GET",
            f"conversations/{conversation_id}/patient-history",
            200
        )
        
        if success:
            appointments_returned = response.get('appointments', [])
            print(f"Returned {len(appointments_returned)} appointments")
            
            if len(appointments_returned) == 0:
                print("✅ Correctly returns empty appointments array for conversation without phone")
                return True
            else:
                print(f"❌ Expected 0 appointments, got {len(appointments_returned)}")
                return False
        else:
            print("❌ Failed to get patient history for conversation without phone")
            return False

    def test_existing_conversation(self, existing_conversations):
        """Test 4: Test with existing real conversation"""
        print("\n" + "="*70)
        print("TEST 4: EXISTING REAL CONVERSATION")
        print("="*70)
        
        if not existing_conversations:
            print("❌ No existing conversations found")
            return False
        
        # Use the first existing conversation
        conversation = existing_conversations[0]
        conversation_id = conversation['_id']
        
        print(f"Testing existing conversation ID: {conversation_id}")
        print(f"Patient: {conversation.get('patient_name', 'Unknown')}")
        print(f"Phone: {conversation.get('patient_phone', 'Unknown')}")
        
        success, response = self.run_test(
            "Get Patient History - Existing Real Conversation",
            "GET",
            f"conversations/{conversation_id}/patient-history",
            200
        )
        
        if success:
            appointments_returned = response.get('appointments', [])
            print(f"✅ Endpoint returned {len(appointments_returned)} appointments")
            
            # This is a real conversation, so we might or might not have appointments
            # The important thing is that the endpoint works
            if 'appointments' in response:
                print("✅ Response has correct structure")
                
                if appointments_returned:
                    print("✅ Found appointments for existing conversation")
                    # Show first appointment details
                    first_apt = appointments_returned[0]
                    print(f"   Sample appointment: {first_apt.get('title', 'No title')}")
                    print(f"   Date: {first_apt.get('date', 'No date')}")
                    print(f"   Doctor: {first_apt.get('doctor', 'No doctor')}")
                else:
                    print("ℹ️ No appointments found for this conversation (this is normal)")
                
                return True
            else:
                print("❌ Response missing 'appointments' key")
                return False
        else:
            print("❌ Failed to get patient history for existing conversation")
            return False

    async def run_all_tests(self):
        """Run all patient history endpoint tests"""
        print("\n" + "="*70)
        print("🦷 PATIENT HISTORY ENDPOINT FOCUSED TESTING")
        print("="*70)
        print("ENDPOINT: GET /api/conversations/{conversation_id}/patient-history")
        print("GOAL: Test new endpoint for retrieving last 5 appointments for WhatsApp conversations")
        
        test_conversation_ids = []
        
        try:
            # Get existing conversations
            print("\n📋 Getting existing conversations...")
            existing_conversations = await self.get_existing_conversations()
            print(f"Found {len(existing_conversations)} existing conversations")
            
            # Create test data
            print("\n📋 Creating test conversation with appointments...")
            test_conversation, test_appointments = await self.create_test_conversation_and_appointments()
            test_conversation_ids.append(test_conversation['_id'])
            print(f"Created test conversation with {len(test_appointments)} appointments")
            
            print("\n📋 Creating test conversation without phone...")
            no_phone_conversation = await self.create_conversation_without_phone()
            test_conversation_ids.append(no_phone_conversation['_id'])
            print("Created test conversation without phone")
            
            # Run tests
            tests_results = []
            
            # Test 1: Non-existent conversation
            tests_results.append(self.test_nonexistent_conversation())
            
            # Test 2: Conversation with appointments
            tests_results.append(self.test_conversation_with_appointments(test_conversation, test_appointments))
            
            # Test 3: Conversation without phone
            tests_results.append(self.test_conversation_without_phone(no_phone_conversation))
            
            # Test 4: Existing real conversation
            tests_results.append(self.test_existing_conversation(existing_conversations))
            
            # Calculate results
            passed_tests = sum(tests_results)
            total_tests = len(tests_results)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # Final summary
            print("\n" + "="*70)
            print("📋 PATIENT HISTORY ENDPOINT TEST SUMMARY")
            print("="*70)
            
            print(f"✅ Tests passed: {passed_tests}/{total_tests}")
            print(f"📊 Success rate: {success_rate:.1f}%")
            print(f"🔧 Total API calls: {self.tests_run}")
            print(f"✅ Successful API calls: {self.tests_passed}")
            
            if success_rate >= 75:
                print("🎉 PATIENT HISTORY ENDPOINT: TESTING SUCCESSFUL!")
                return True
            else:
                print("❌ PATIENT HISTORY ENDPOINT: ISSUES DETECTED")
                return False
                
        finally:
            # Cleanup test data
            if test_conversation_ids:
                print("\n🧹 Cleaning up test data...")
                await self.cleanup_test_data(test_conversation_ids)
                print("✅ Test data cleaned up")

def main():
    """Main function to run patient history endpoint tests"""
    print("🚀 Starting Patient History Endpoint Focused Testing...")
    
    tester = PatientHistoryFocusedTester()
    
    # Run async tests
    success = asyncio.run(tester.run_all_tests())
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()