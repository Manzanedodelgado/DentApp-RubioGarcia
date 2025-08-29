import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

class OmniDeskAPITester:
    def __init__(self, base_url="https://omnidesk-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {
            'contacts': [],
            'appointments': [],
            'messages': [],
            'templates': [],
            'campaigns': []
        }

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

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD ENDPOINTS")
        print("="*50)
        
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            required_fields = ['total_contacts', 'active_contacts', 'total_appointments', 
                             'today_appointments', 'pending_messages', 'active_campaigns']
            for field in required_fields:
                if field in response:
                    print(f"   ✓ {field}: {response[field]}")
                else:
                    print(f"   ❌ Missing field: {field}")
        
        return success

    def test_contacts_crud(self):
        """Test complete CRUD operations for contacts"""
        print("\n" + "="*50)
        print("TESTING CONTACTS CRUD OPERATIONS")
        print("="*50)
        
        # Test CREATE contact
        contact_data = {
            "name": "Test Contact",
            "email": "test@example.com",
            "phone": "+1234567890",
            "whatsapp": "+1234567890",
            "tags": ["test", "automation"],
            "notes": "Created by automated test"
        }
        
        success, contact = self.run_test(
            "Create Contact",
            "POST",
            "contacts",
            200,
            data=contact_data
        )
        
        if not success:
            return False
            
        contact_id = contact.get('id')
        if contact_id:
            self.created_resources['contacts'].append(contact_id)
            print(f"   Created contact ID: {contact_id}")
        
        # Test GET all contacts
        success, contacts = self.run_test(
            "Get All Contacts",
            "GET",
            "contacts",
            200
        )
        
        if success:
            print(f"   Found {len(contacts)} contacts")
        
        # Test GET specific contact
        if contact_id:
            success, retrieved_contact = self.run_test(
                "Get Specific Contact",
                "GET",
                f"contacts/{contact_id}",
                200
            )
            
            if success and retrieved_contact.get('name') == contact_data['name']:
                print(f"   ✓ Contact retrieved correctly")
        
        # Test UPDATE contact
        if contact_id:
            update_data = {
                "name": "Updated Test Contact",
                "status": "inactive"
            }
            
            success, updated_contact = self.run_test(
                "Update Contact",
                "PUT",
                f"contacts/{contact_id}",
                200,
                data=update_data
            )
            
            if success and updated_contact.get('name') == update_data['name']:
                print(f"   ✓ Contact updated correctly")
        
        # Test filtering contacts
        success, filtered_contacts = self.run_test(
            "Filter Contacts by Status",
            "GET",
            "contacts",
            200,
            params={"status": "active"}
        )
        
        if success:
            print(f"   Found {len(filtered_contacts)} active contacts")
        
        return True

    def test_appointments_crud(self):
        """Test appointments CRUD operations"""
        print("\n" + "="*50)
        print("TESTING APPOINTMENTS CRUD OPERATIONS")
        print("="*50)
        
        # First ensure we have a contact to link to
        if not self.created_resources['contacts']:
            print("❌ No contacts available for appointment testing")
            return False
        
        contact_id = self.created_resources['contacts'][0]
        
        # Test CREATE appointment
        appointment_data = {
            "contact_id": contact_id,
            "title": "Test Appointment",
            "description": "Automated test appointment",
            "date": datetime.now(timezone.utc).isoformat(),
            "duration_minutes": 60
        }
        
        success, appointment = self.run_test(
            "Create Appointment",
            "POST",
            "appointments",
            200,
            data=appointment_data
        )
        
        if not success:
            return False
            
        appointment_id = appointment.get('id')
        if appointment_id:
            self.created_resources['appointments'].append(appointment_id)
            print(f"   Created appointment ID: {appointment_id}")
        
        # Test GET all appointments
        success, appointments = self.run_test(
            "Get All Appointments",
            "GET",
            "appointments",
            200
        )
        
        if success:
            print(f"   Found {len(appointments)} appointments")
        
        # Test GET specific appointment
        if appointment_id:
            success, retrieved_appointment = self.run_test(
                "Get Specific Appointment",
                "GET",
                f"appointments/{appointment_id}",
                200
            )
            
            if success and retrieved_appointment.get('title') == appointment_data['title']:
                print(f"   ✓ Appointment retrieved correctly")
        
        # Test UPDATE appointment
        if appointment_id:
            update_data = {
                "title": "Updated Test Appointment",
                "status": "confirmed"
            }
            
            success, updated_appointment = self.run_test(
                "Update Appointment",
                "PUT",
                f"appointments/{appointment_id}",
                200,
                data=update_data
            )
            
            if success and updated_appointment.get('title') == update_data['title']:
                print(f"   ✓ Appointment updated correctly")
        
        return True

    def test_messages_crud(self):
        """Test messages CRUD operations"""
        print("\n" + "="*50)
        print("TESTING MESSAGES CRUD OPERATIONS")
        print("="*50)
        
        # First ensure we have a contact to link to
        if not self.created_resources['contacts']:
            print("❌ No contacts available for message testing")
            return False
        
        contact_id = self.created_resources['contacts'][0]
        
        # Test CREATE message
        message_data = {
            "contact_id": contact_id,
            "channel": "whatsapp",
            "content": "Test message from automated testing",
            "is_from_contact": False
        }
        
        success, message = self.run_test(
            "Create Message",
            "POST",
            "messages",
            200,
            data=message_data
        )
        
        if not success:
            return False
            
        message_id = message.get('id')
        if message_id:
            self.created_resources['messages'].append(message_id)
            print(f"   Created message ID: {message_id}")
        
        # Test GET all messages
        success, messages = self.run_test(
            "Get All Messages",
            "GET",
            "messages",
            200
        )
        
        if success:
            print(f"   Found {len(messages)} messages")
        
        # Test filtering messages by contact
        success, contact_messages = self.run_test(
            "Filter Messages by Contact",
            "GET",
            "messages",
            200,
            params={"contact_id": contact_id}
        )
        
        if success:
            print(f"   Found {len(contact_messages)} messages for contact")
        
        # Test filtering messages by channel
        success, channel_messages = self.run_test(
            "Filter Messages by Channel",
            "GET",
            "messages",
            200,
            params={"channel": "whatsapp"}
        )
        
        if success:
            print(f"   Found {len(channel_messages)} WhatsApp messages")
        
        return True

    def test_templates_crud(self):
        """Test templates CRUD operations"""
        print("\n" + "="*50)
        print("TESTING TEMPLATES CRUD OPERATIONS")
        print("="*50)
        
        # Test CREATE template
        template_data = {
            "name": "Test Template",
            "content": "Hello {{name}}, this is a test template with {{variable}}",
            "channel": "whatsapp",
            "variables": ["name", "variable"]
        }
        
        success, template = self.run_test(
            "Create Template",
            "POST",
            "templates",
            200,
            data=template_data
        )
        
        if not success:
            return False
            
        template_id = template.get('id')
        if template_id:
            self.created_resources['templates'].append(template_id)
            print(f"   Created template ID: {template_id}")
        
        # Test GET all templates
        success, templates = self.run_test(
            "Get All Templates",
            "GET",
            "templates",
            200
        )
        
        if success:
            print(f"   Found {len(templates)} templates")
        
        # Test filtering templates by channel
        success, channel_templates = self.run_test(
            "Filter Templates by Channel",
            "GET",
            "templates",
            200,
            params={"channel": "whatsapp"}
        )
        
        if success:
            print(f"   Found {len(channel_templates)} WhatsApp templates")
        
        return True

    def test_campaigns_crud(self):
        """Test campaigns CRUD operations"""
        print("\n" + "="*50)
        print("TESTING CAMPAIGNS CRUD OPERATIONS")
        print("="*50)
        
        # First ensure we have a template to link to
        if not self.created_resources['templates']:
            print("❌ No templates available for campaign testing")
            return False
        
        template_id = self.created_resources['templates'][0]
        
        # Test CREATE campaign
        campaign_data = {
            "name": "Test Campaign",
            "template_id": template_id,
            "channel": "whatsapp",
            "target_tags": ["test"],
            "scheduled_at": datetime.now(timezone.utc).isoformat()
        }
        
        success, campaign = self.run_test(
            "Create Campaign",
            "POST",
            "campaigns",
            200,
            data=campaign_data
        )
        
        if not success:
            return False
            
        campaign_id = campaign.get('id')
        if campaign_id:
            self.created_resources['campaigns'].append(campaign_id)
            print(f"   Created campaign ID: {campaign_id}")
        
        # Test GET all campaigns
        success, campaigns = self.run_test(
            "Get All Campaigns",
            "GET",
            "campaigns",
            200
        )
        
        if success:
            print(f"   Found {len(campaigns)} campaigns")
        
        return True

    def test_ai_training_crud(self):
        """Test AI training CRUD operations"""
        print("\n" + "="*50)
        print("TESTING AI TRAINING CRUD OPERATIONS")
        print("="*50)
        
        # Test GET AI training (might not exist initially)
        success, existing_training = self.run_test(
            "Get AI Training Configuration",
            "GET",
            "ai/training",
            200
        )
        
        if success and existing_training:
            print(f"   Found existing AI training config")
        else:
            print(f"   No existing AI training config found")
        
        # Test CREATE/UPDATE AI training
        training_data = {
            "practice_name": "RUBIO GARCÍA DENTAL",
            "system_prompt": "Eres un asistente virtual profesional de la clínica dental RUBIO GARCÍA DENTAL.",
            "specialties": ["Implantología", "Estética dental", "Ortodoncia", "Endodoncia"],
            "services": ["Consultas generales", "Limpiezas", "Implantes", "Blanqueamientos", "Ortodoncia"],
            "working_hours": "Lunes a Viernes 9:00-18:00, Sábados 9:00-14:00",
            "emergency_contact": "Para emergencias llame al +34 123 456 789",
            "appointment_instructions": "Para agendar citas necesitamos su nombre completo, teléfono y preferencia de horario.",
            "policies": "Recordamos confirmar las citas 24 horas antes. Cancelaciones con menos de 2 horas tienen recargo.",
            "personality": "profesional y amigable",
            "language": "español"
        }
        
        success, training = self.run_test(
            "Create/Update AI Training",
            "POST",
            "ai/training",
            200,
            data=training_data
        )
        
        if not success:
            return False
        
        if training and training.get('id'):
            print(f"   Created/Updated AI training ID: {training.get('id')}")
        
        # Test GET AI training after creation
        success, retrieved_training = self.run_test(
            "Get AI Training After Creation",
            "GET",
            "ai/training",
            200
        )
        
        if success and retrieved_training:
            if retrieved_training.get('practice_name') == training_data['practice_name']:
                print(f"   ✓ AI training retrieved correctly")
            else:
                print(f"   ❌ AI training data mismatch")
        
        # Test UPDATE AI training
        update_data = {
            "personality": "muy profesional y empático",
            "working_hours": "Lunes a Viernes 8:00-19:00"
        }
        
        success, updated_training = self.run_test(
            "Update AI Training",
            "PUT",
            "ai/training",
            200,
            data=update_data
        )
        
        if success and updated_training:
            if updated_training.get('personality') == update_data['personality']:
                print(f"   ✓ AI training updated correctly")
        
        return True

    def test_chat_functionality(self):
        """Test AI chat functionality"""
        print("\n" + "="*50)
        print("TESTING AI CHAT FUNCTIONALITY")
        print("="*50)
        
        # First ensure we have a contact for chat
        if not self.created_resources['contacts']:
            print("❌ No contacts available for chat testing")
            return False
        
        contact_id = self.created_resources['contacts'][0]
        
        # Test CREATE chat session
        session_params = {
            "contact_id": contact_id,
            "contact_name": "Test Contact",
            "contact_phone": "+1234567890"
        }
        
        success, session = self.run_test(
            "Create Chat Session",
            "POST",
            "chat/sessions",
            200,
            params=session_params
        )
        
        if not success:
            return False
        
        session_id = session.get('id')
        if session_id:
            print(f"   Created chat session ID: {session_id}")
        else:
            print("❌ No session ID returned")
            return False
        
        # Test GET all chat sessions
        success, sessions = self.run_test(
            "Get All Chat Sessions",
            "GET",
            "chat/sessions",
            200
        )
        
        if success:
            print(f"   Found {len(sessions)} chat sessions")
        
        # Test GET specific chat session
        success, retrieved_session = self.run_test(
            "Get Specific Chat Session",
            "GET",
            f"chat/sessions/{session_id}",
            200
        )
        
        if success and retrieved_session.get('id') == session_id:
            print(f"   ✓ Chat session retrieved correctly")
        
        # Test SEND chat message (AI integration test)
        message_data = {
            "content": "Hola, necesito agendar una cita para limpieza dental",
            "is_from_patient": True
        }
        
        success, ai_response = self.run_test(
            "Send Chat Message (AI Integration)",
            "POST",
            f"chat/message?session_id={session_id}",
            200,
            data=message_data
        )
        
        if success:
            if ai_response.get('ai_response'):
                print(f"   ✓ AI responded: {ai_response['ai_response'][:100]}...")
                if ai_response.get('should_schedule_appointment'):
                    print(f"   ✓ AI detected appointment request")
            else:
                print(f"   ❌ No AI response received")
                return False
        
        # Test another message in Spanish
        message_data2 = {
            "content": "¿Cuáles son sus horarios de atención?",
            "is_from_patient": True
        }
        
        success, ai_response2 = self.run_test(
            "Send Spanish Query Message",
            "POST",
            f"chat/message?session_id={session_id}",
            200,
            data=message_data2
        )
        
        if success and ai_response2.get('ai_response'):
            print(f"   ✓ AI responded to Spanish query: {ai_response2['ai_response'][:100]}...")
        
        return True

    def test_tags_endpoint(self):
        """Test tags aggregation endpoint"""
        print("\n" + "="*50)
        print("TESTING TAGS ENDPOINT")
        print("="*50)
        
        success, tags = self.run_test(
            "Get Available Tags",
            "GET",
            "tags",
            200
        )
        
        if success:
            print(f"   Found {len(tags)} unique tags")
            for tag in tags[:5]:  # Show first 5 tags
                print(f"   - {tag.get('name', 'Unknown')}: {tag.get('count', 0)} contacts")
        
        return success

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n" + "="*50)
        print("CLEANING UP TEST RESOURCES")
        print("="*50)
        
        # Delete contacts (this will cascade to related appointments/messages)
        for contact_id in self.created_resources['contacts']:
            success, _ = self.run_test(
                f"Delete Contact {contact_id}",
                "DELETE",
                f"contacts/{contact_id}",
                200
            )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting OmniDesk API Testing Suite")
        print(f"Backend URL: {self.base_url}")
        
        # Test dashboard first
        if not self.test_dashboard_stats():
            print("❌ Dashboard tests failed, stopping")
            return 1
        
        # Test CRUD operations
        if not self.test_contacts_crud():
            print("❌ Contacts CRUD tests failed")
            return 1
        
        if not self.test_appointments_crud():
            print("❌ Appointments CRUD tests failed")
            return 1
        
        if not self.test_messages_crud():
            print("❌ Messages CRUD tests failed")
            return 1
        
        if not self.test_templates_crud():
            print("❌ Templates CRUD tests failed")
            return 1
        
        if not self.test_campaigns_crud():
            print("❌ Campaigns CRUD tests failed")
            return 1
        
        # Test additional endpoints
        self.test_tags_endpoint()
        
        # Cleanup
        self.cleanup_resources()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = OmniDeskAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())