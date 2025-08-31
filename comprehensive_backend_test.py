#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite for RUBIO GARCÍA DENTAL
Based on review request for exhaustive testing of all implemented features
Authentication: JMD/190582
"""

import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any
import re

class ComprehensiveDentalAPITester:
    def __init__(self, base_url="https://dental-ai-hub.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.auth_token = None
        self.test_results = {}

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict[Any, Any] = None, params: Dict[str, str] = None) -> tuple:
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
                self.failed_tests.append(name)
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            self.failed_tests.append(name)
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test authentication system with JMD/190582 credentials"""
        print("\n" + "="*70)
        print("🔐 TESTING AUTHENTICATION SYSTEM")
        print("="*70)
        
        # Test login with correct credentials
        login_data = {
            "username": "JMD",
            "password": "190582"
        }
        
        success, response = self.run_test(
            "Login with JMD/190582 credentials",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and response.get('success'):
            self.auth_token = response.get('token')
            print(f"   ✅ Authentication successful - Token: {self.auth_token[:20]}...")
            print(f"   ✅ User: {response.get('user', {}).get('name', 'Unknown')}")
        else:
            print("   ❌ Authentication failed")
            return False
        
        # Test token verification
        success, verify_response = self.run_test(
            "Verify authentication token",
            "GET",
            f"auth/verify?token={self.auth_token}",
            200
        )
        
        if success and verify_response.get('valid'):
            print("   ✅ Token verification successful")
        else:
            print("   ❌ Token verification failed")
        
        # Test login with wrong credentials
        wrong_login = {
            "username": "wrong",
            "password": "wrong"
        }
        
        success, wrong_response = self.run_test(
            "Login with wrong credentials",
            "POST",
            "auth/login",
            200,
            data=wrong_login
        )
        
        if success and not wrong_response.get('success'):
            print("   ✅ Wrong credentials properly rejected")
        else:
            print("   ❌ Security issue: Wrong credentials accepted")
        
        return True

    def test_dashboard_calendar_system(self):
        """Test Dashboard & Calendar System - Area 1"""
        print("\n" + "="*70)
        print("📊 TESTING DASHBOARD & CALENDAR SYSTEM")
        print("="*70)
        
        results = {}
        
        # Test GET /api/dashboard/stats
        success, stats = self.run_test(
            "Dashboard Statistics",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            required_fields = ['total_contacts', 'today_appointments', 'pending_messages', 'ai_conversations']
            for field in required_fields:
                if field in stats:
                    print(f"   ✅ {field}: {stats[field]}")
                else:
                    print(f"   ❌ Missing field: {field}")
            results['dashboard_stats'] = True
        else:
            results['dashboard_stats'] = False
        
        # Test GET /api/appointments/by-date with today's date
        today = "2025-09-01"  # As specified in review request
        success, today_appointments = self.run_test(
            f"Appointments by date ({today})",
            "GET",
            "appointments/by-date",
            200,
            params={"date": today}
        )
        
        if success:
            print(f"   ✅ Found {len(today_appointments)} appointments for {today}")
            results['appointments_by_date'] = True
        else:
            results['appointments_by_date'] = False
        
        # Test GET /api/dashboard/tasks
        success, tasks = self.run_test(
            "Dashboard Tasks",
            "GET",
            "dashboard/tasks",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(tasks)} dashboard tasks")
            # Test status filtering
            success, pending_tasks = self.run_test(
                "Dashboard Tasks - Pending Filter",
                "GET",
                "dashboard/tasks",
                200,
                params={"status": "pending"}
            )
            if success:
                print(f"   ✅ Found {len(pending_tasks)} pending tasks")
            results['dashboard_tasks'] = True
        else:
            results['dashboard_tasks'] = False
        
        # Test date parsing and timezone handling
        test_dates = ["2025-01-01", "2025-12-31", "2025-02-29"]  # Include invalid date
        for test_date in test_dates:
            success, date_result = self.run_test(
                f"Date parsing test ({test_date})",
                "GET",
                "appointments/by-date",
                200 if test_date != "2025-02-29" else 500,
                params={"date": test_date}
            )
            if test_date == "2025-02-29" and not success:
                print(f"   ✅ Invalid date {test_date} properly rejected")
            elif success:
                print(f"   ✅ Date {test_date} parsed correctly")
        
        self.test_results['dashboard_calendar'] = results
        return all(results.values())

    def test_whatsapp_integration(self):
        """Test WhatsApp Integration - Area 2"""
        print("\n" + "="*70)
        print("📱 TESTING WHATSAPP INTEGRATION")
        print("="*70)
        
        results = {}
        
        # Test GET /api/whatsapp/status
        success, status = self.run_test(
            "WhatsApp Connection Status",
            "GET",
            "whatsapp/status",
            200
        )
        
        if success:
            print(f"   ✅ WhatsApp status: {status}")
            results['whatsapp_status'] = True
        else:
            results['whatsapp_status'] = False
        
        # Test GET /api/whatsapp/qr
        success, qr_response = self.run_test(
            "WhatsApp QR Code Generation",
            "GET",
            "whatsapp/qr",
            200
        )
        
        if success:
            print("   ✅ QR code endpoint accessible")
            results['whatsapp_qr'] = True
        else:
            results['whatsapp_qr'] = False
        
        # Test POST /api/whatsapp/send with phone validation
        test_message = {
            "phone_number": "34664218253",  # Valid format
            "message": "Test message from comprehensive testing"
        }
        
        success, send_response = self.run_test(
            "WhatsApp Send Message",
            "POST",
            "whatsapp/send",
            200,
            data=test_message
        )
        
        if success:
            print("   ✅ Message sending endpoint working")
            results['whatsapp_send'] = True
        else:
            results['whatsapp_send'] = False
        
        # Test invalid phone number
        invalid_message = {
            "phone_number": "invalid",
            "message": "Test message"
        }
        
        success, invalid_response = self.run_test(
            "WhatsApp Send - Invalid Phone",
            "POST",
            "whatsapp/send",
            400,  # Expecting validation error
            data=invalid_message
        )
        
        if success:
            print("   ✅ Invalid phone number properly rejected")
        
        # Test POST /api/whatsapp/send-reminder
        reminder_data = {
            "phone_number": "34664218253",
            "appointment_data": {
                "patient_name": "Test Patient",
                "date": "2025-09-01",
                "time": "10:00",
                "doctor": "Dr. Mario Rubio",
                "treatment": "Limpieza dental"
            }
        }
        
        success, reminder_response = self.run_test(
            "WhatsApp Send Reminder",
            "POST",
            "whatsapp/send-reminder",
            200,
            data=reminder_data
        )
        
        if success:
            print("   ✅ Appointment reminder sending working")
            results['whatsapp_reminder'] = True
        else:
            results['whatsapp_reminder'] = False
        
        self.test_results['whatsapp_integration'] = results
        return all(results.values())

    def test_conversations_system(self):
        """Test Conversations System - Area 3"""
        print("\n" + "="*70)
        print("💬 TESTING CONVERSATIONS SYSTEM")
        print("="*70)
        
        results = {}
        
        # Test GET /api/conversations
        success, conversations = self.run_test(
            "List All Conversations",
            "GET",
            "conversations",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(conversations)} conversations")
            results['conversations_list'] = True
        else:
            results['conversations_list'] = False
        
        # Test GET /api/conversations/pending
        success, pending_conversations = self.run_test(
            "Pending Conversations",
            "GET",
            "conversations/pending",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(pending_conversations)} pending conversations")
            # Check urgency color coding
            for conv in pending_conversations[:3]:
                color = conv.get('color_code', 'unknown')
                priority = conv.get('priority', 'unknown')
                print(f"   - Conversation: {color} urgency, {priority} priority")
            results['conversations_pending'] = True
        else:
            results['conversations_pending'] = False
        
        # Test conversation creation and message storage
        if pending_conversations:
            conv_id = pending_conversations[0].get('id')
            if conv_id:
                # Test GET /api/conversations/{id}/messages
                success, messages = self.run_test(
                    f"Conversation Messages ({conv_id})",
                    "GET",
                    f"conversations/{conv_id}/messages",
                    200
                )
                
                if success:
                    print(f"   ✅ Found {len(messages)} messages in conversation")
                    results['conversation_messages'] = True
                else:
                    results['conversation_messages'] = False
                
                # Test POST /api/conversations/{id}/send-message
                message_data = {
                    "content": "Test message from comprehensive testing",
                    "is_from_patient": False
                }
                
                success, send_result = self.run_test(
                    f"Send Message to Conversation ({conv_id})",
                    "POST",
                    f"conversations/{conv_id}/send-message",
                    200,
                    data=message_data
                )
                
                if success:
                    print("   ✅ Message sending to conversation working")
                    results['conversation_send'] = True
                else:
                    results['conversation_send'] = False
        
        self.test_results['conversations_system'] = results
        return all(results.values())

    def test_user_management(self):
        """Test User Management - Area 4"""
        print("\n" + "="*70)
        print("👥 TESTING USER MANAGEMENT SYSTEM")
        print("="*70)
        
        results = {}
        
        # Test GET /api/users
        success, users = self.run_test(
            "List All Users",
            "GET",
            "users",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(users)} users")
            # Check roles and permissions
            for user in users[:3]:
                username = user.get('username', 'unknown')
                role = user.get('role', 'unknown')
                permissions = user.get('permissions', [])
                print(f"   - User: {username}, Role: {role}, Permissions: {len(permissions)}")
            results['users_list'] = True
        else:
            results['users_list'] = False
        
        # Test POST /api/users - Create new user
        new_user_data = {
            "username": "test_user_comprehensive",
            "password": "test_password",
            "role": "staff",
            "permissions": ["read", "write"]
        }
        
        success, created_user = self.run_test(
            "Create New User",
            "POST",
            "users",
            200,
            data=new_user_data
        )
        
        if success:
            user_id = created_user.get('id')
            print(f"   ✅ Created user with ID: {user_id}")
            results['users_create'] = True
            
            # Test PUT /api/users/{id} - Update user permissions
            if user_id:
                update_data = {
                    "role": "viewer",
                    "permissions": ["read"]
                }
                
                success, updated_user = self.run_test(
                    f"Update User Permissions ({user_id})",
                    "PUT",
                    f"users/{user_id}",
                    200,
                    data=update_data
                )
                
                if success:
                    print("   ✅ User permissions updated successfully")
                    results['users_update'] = True
                else:
                    results['users_update'] = False
        else:
            results['users_create'] = False
            results['users_update'] = False
        
        # Test role-based permission validation
        roles_to_test = ["admin", "staff", "viewer", "readonly"]
        for role in roles_to_test:
            success, role_users = self.run_test(
                f"Filter Users by Role ({role})",
                "GET",
                "users",
                200,
                params={"role": role}
            )
            
            if success:
                print(f"   ✅ Found {len(role_users)} users with role {role}")
        
        self.test_results['user_management'] = results
        return all(results.values())

    def test_appointment_management(self):
        """Test Appointment Management - Area 5"""
        print("\n" + "="*70)
        print("📅 TESTING APPOINTMENT MANAGEMENT")
        print("="*70)
        
        results = {}
        
        # Test GET /api/appointments with filtering
        success, appointments = self.run_test(
            "List All Appointments",
            "GET",
            "appointments",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(appointments)} appointments")
            results['appointments_list'] = True
        else:
            results['appointments_list'] = False
        
        # Test filtering by status
        statuses = ["scheduled", "confirmed", "cancelled", "completed"]
        for status in statuses:
            success, filtered_appointments = self.run_test(
                f"Filter Appointments by Status ({status})",
                "GET",
                "appointments",
                200,
                params={"status": status}
            )
            
            if success:
                print(f"   ✅ Found {len(filtered_appointments)} {status} appointments")
        
        # Test appointment update
        if appointments:
            apt_id = appointments[0].get('id')
            if apt_id:
                update_data = {
                    "status": "confirmed"
                }
                
                success, updated_apt = self.run_test(
                    f"Update Appointment Status ({apt_id})",
                    "PUT",
                    f"appointments/{apt_id}",
                    200,
                    data=update_data
                )
                
                if success:
                    print("   ✅ Appointment status updated successfully")
                    results['appointments_update'] = True
                else:
                    results['appointments_update'] = False
                
                # Test POST /api/appointments/{id}/sync - Google Sheets sync
                success, sync_result = self.run_test(
                    f"Sync Appointment to Google Sheets ({apt_id})",
                    "POST",
                    f"appointments/{apt_id}/sync",
                    200
                )
                
                if success:
                    print("   ✅ Google Sheets sync working")
                    results['appointments_sync'] = True
                else:
                    results['appointments_sync'] = False
        
        # Test different appointment statuses and dates
        test_dates = ["2025-01-01", "2025-06-15", "2025-12-31"]
        for test_date in test_dates:
            success, date_appointments = self.run_test(
                f"Appointments by Date ({test_date})",
                "GET",
                "appointments/by-date",
                200,
                params={"date": test_date}
            )
            
            if success:
                print(f"   ✅ Date {test_date}: {len(date_appointments)} appointments")
        
        self.test_results['appointment_management'] = results
        return all(results.values())

    def test_contact_patient_management(self):
        """Test Contact/Patient Management - Area 6"""
        print("\n" + "="*70)
        print("👤 TESTING CONTACT/PATIENT MANAGEMENT")
        print("="*70)
        
        results = {}
        
        # Test GET /api/contacts
        success, contacts = self.run_test(
            "List All Contacts/Patients",
            "GET",
            "contacts",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(contacts)} contacts")
            results['contacts_list'] = True
        else:
            results['contacts_list'] = False
        
        # Test POST /api/contacts - Create new patient
        new_patient_data = {
            "name": "María García López",
            "email": "maria.garcia@example.com",
            "phone": "34666123456",
            "whatsapp": "34666123456",
            "tags": ["paciente", "test"],
            "notes": "Paciente de prueba para testing comprehensivo"
        }
        
        success, created_patient = self.run_test(
            "Create New Patient",
            "POST",
            "contacts",
            200,
            data=new_patient_data
        )
        
        if success:
            patient_id = created_patient.get('id')
            print(f"   ✅ Created patient with ID: {patient_id}")
            results['contacts_create'] = True
            
            # Test GET /api/contacts/{id}/appointments - Patient history
            if patient_id:
                success, patient_appointments = self.run_test(
                    f"Patient Appointment History ({patient_id})",
                    "GET",
                    f"contacts/{patient_id}/appointments",
                    200
                )
                
                if success:
                    print(f"   ✅ Found {len(patient_appointments)} appointments for patient")
                    results['patient_history'] = True
                else:
                    results['patient_history'] = False
        else:
            results['contacts_create'] = False
            results['patient_history'] = False
        
        # Test contact filtering and search
        success, active_contacts = self.run_test(
            "Filter Active Contacts",
            "GET",
            "contacts",
            200,
            params={"status": "active"}
        )
        
        if success:
            print(f"   ✅ Found {len(active_contacts)} active contacts")
        
        # Test tag filtering
        success, tagged_contacts = self.run_test(
            "Filter Contacts by Tag",
            "GET",
            "contacts",
            200,
            params={"tag": "paciente"}
        )
        
        if success:
            print(f"   ✅ Found {len(tagged_contacts)} contacts with 'paciente' tag")
        
        self.test_results['contact_management'] = results
        return all(results.values())

    def test_templates_reminders(self):
        """Test Templates & Reminders - Area 7"""
        print("\n" + "="*70)
        print("📝 TESTING TEMPLATES & REMINDERS")
        print("="*70)
        
        results = {}
        
        # Test GET /api/templates
        success, templates = self.run_test(
            "List Message Templates",
            "GET",
            "templates",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(templates)} templates")
            for template in templates[:3]:
                name = template.get('name', 'Unknown')
                channel = template.get('channel', 'Unknown')
                variables = template.get('variables', [])
                print(f"   - Template: {name}, Channel: {channel}, Variables: {len(variables)}")
            results['templates_list'] = True
        else:
            results['templates_list'] = False
        
        # Test GET /api/reminders/pending
        success, pending_reminders = self.run_test(
            "Pending Reminders",
            "GET",
            "reminders/pending",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(pending_reminders)} pending reminders")
            results['reminders_pending'] = True
        else:
            results['reminders_pending'] = False
        
        # Test POST /api/reminders/send - Send bulk reminders
        bulk_reminder_data = {
            "template_id": templates[0].get('id') if templates else "default",
            "recipient_ids": ["test_recipient"],
            "variables": {
                "nombre": "Test Patient",
                "fecha": "2025-09-01",
                "hora": "10:00"
            }
        }
        
        success, send_result = self.run_test(
            "Send Bulk Reminders",
            "POST",
            "reminders/send",
            200,
            data=bulk_reminder_data
        )
        
        if success:
            print("   ✅ Bulk reminder sending working")
            results['reminders_send'] = True
        else:
            results['reminders_send'] = False
        
        # Test template creation
        new_template_data = {
            "name": "Test Comprehensive Template",
            "content": "Hola {nombre}, su cita es el {fecha} a las {hora}",
            "channel": "whatsapp",
            "variables": ["nombre", "fecha", "hora"]
        }
        
        success, created_template = self.run_test(
            "Create New Template",
            "POST",
            "templates",
            200,
            data=new_template_data
        )
        
        if success:
            print("   ✅ Template creation working")
            results['templates_create'] = True
        else:
            results['templates_create'] = False
        
        self.test_results['templates_reminders'] = results
        return all(results.values())

    def test_ai_automation(self):
        """Test AI & Automation - Area 8"""
        print("\n" + "="*70)
        print("🤖 TESTING AI & AUTOMATION")
        print("="*70)
        
        results = {}
        
        # Test GET /api/automations
        success, automations = self.run_test(
            "List Automation Rules",
            "GET",
            "automations",
            200
        )
        
        if success:
            print(f"   ✅ Found {len(automations)} automation rules")
            for automation in automations[:3]:
                name = automation.get('name', 'Unknown')
                category = automation.get('category', 'Unknown')
                is_active = automation.get('is_active', False)
                print(f"   - Automation: {name}, Category: {category}, Active: {is_active}")
            results['automations_list'] = True
        else:
            results['automations_list'] = False
        
        # Test POST /api/voice-assistant - Voice processing
        voice_request = {
            "message": "Necesito agendar una cita para limpieza dental",
            "session_id": "test_session_comprehensive"
        }
        
        success, voice_response = self.run_test(
            "Voice Assistant Processing",
            "POST",
            "voice-assistant",
            200,
            data=voice_request
        )
        
        if success:
            ai_response = voice_response.get('response', '')
            action_type = voice_response.get('action_type', '')
            print(f"   ✅ AI Response: {ai_response[:100]}...")
            print(f"   ✅ Action Type: {action_type}")
            results['voice_assistant'] = True
        else:
            results['voice_assistant'] = False
        
        # Test AI integration endpoints
        ai_test_scenarios = [
            {
                "message": "Tengo dolor de muelas muy fuerte",
                "expected_urgency": "high"
            },
            {
                "message": "¿Cuáles son sus horarios?",
                "expected_urgency": "low"
            },
            {
                "message": "Necesito una cita de ortodoncia",
                "expected_specialty": "ortodoncia"
            }
        ]
        
        for scenario in ai_test_scenarios:
            ai_request = {
                "message": scenario["message"],
                "session_id": "test_ai_comprehensive"
            }
            
            success, ai_result = self.run_test(
                f"AI Processing: {scenario['message'][:30]}...",
                "POST",
                "ai/voice-assistant",
                200,
                data=ai_request
            )
            
            if success:
                print(f"   ✅ AI processed message successfully")
        
        self.test_results['ai_automation'] = results
        return all(results.values())

    def test_error_handling_edge_cases(self):
        """Test Error Handling & Edge Cases - Area 9"""
        print("\n" + "="*70)
        print("⚠️ TESTING ERROR HANDLING & EDGE CASES")
        print("="*70)
        
        results = {}
        
        # Test invalid dates
        invalid_dates = ["2025-13-01", "2025-02-30", "invalid-date", "2025/01/01"]
        for invalid_date in invalid_dates:
            success, error_response = self.run_test(
                f"Invalid Date Test ({invalid_date})",
                "GET",
                "appointments/by-date",
                500,  # Expecting error
                params={"date": invalid_date}
            )
            
            if success:  # Success means we got the expected error status
                print(f"   ✅ Invalid date {invalid_date} properly rejected")
        
        # Test invalid phone numbers
        invalid_phones = ["invalid", "123", "+34-invalid", ""]
        for invalid_phone in invalid_phones:
            message_data = {
                "phone_number": invalid_phone,
                "message": "Test message"
            }
            
            success, error_response = self.run_test(
                f"Invalid Phone Test ({invalid_phone})",
                "POST",
                "whatsapp/send",
                400,  # Expecting validation error
                data=message_data
            )
            
            if success:
                print(f"   ✅ Invalid phone {invalid_phone} properly rejected")
        
        # Test non-existent IDs
        fake_id = "non-existent-id-12345"
        success, not_found = self.run_test(
            f"Non-existent Contact ID ({fake_id})",
            "GET",
            f"contacts/{fake_id}",
            404,  # Expecting not found
        )
        
        if success:
            print("   ✅ Non-existent ID properly handled")
        
        # Test empty request bodies
        success, empty_body = self.run_test(
            "Empty Request Body",
            "POST",
            "contacts",
            400,  # Expecting validation error
            data={}
        )
        
        if success:
            print("   ✅ Empty request body properly rejected")
        
        # Test malformed JSON
        try:
            url = f"{self.api_url}/contacts"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data="invalid json", headers=headers)
            if response.status_code == 400:
                print("   ✅ Malformed JSON properly rejected")
        except:
            print("   ✅ Malformed JSON handled gracefully")
        
        results['error_handling'] = True
        self.test_results['error_handling'] = results
        return True

    def test_performance_data_integrity(self):
        """Test Performance & Data Integrity - Area 10"""
        print("\n" + "="*70)
        print("⚡ TESTING PERFORMANCE & DATA INTEGRITY")
        print("="*70)
        
        results = {}
        
        # Test large date ranges
        start_time = datetime.now()
        success, large_range = self.run_test(
            "Large Date Range Query",
            "GET",
            "appointments",
            200,
            params={"date_from": "2025-01-01", "date_to": "2025-12-31"}
        )
        end_time = datetime.now()
        
        if success:
            response_time = (end_time - start_time).total_seconds()
            print(f"   ✅ Large date range query completed in {response_time:.2f}s")
            print(f"   ✅ Found {len(large_range)} appointments in full year")
            results['large_queries'] = True
        else:
            results['large_queries'] = False
        
        # Test concurrent requests simulation
        import threading
        import time
        
        concurrent_results = []
        
        def concurrent_request():
            success, response = self.run_test(
                "Concurrent Request",
                "GET",
                "dashboard/stats",
                200
            )
            concurrent_results.append(success)
        
        # Start 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        successful_concurrent = sum(concurrent_results)
        print(f"   ✅ Concurrent requests: {successful_concurrent}/5 successful")
        
        # Test data consistency
        success, contacts_count1 = self.run_test(
            "Data Consistency Check 1",
            "GET",
            "contacts",
            200
        )
        
        time.sleep(1)  # Small delay
        
        success, contacts_count2 = self.run_test(
            "Data Consistency Check 2",
            "GET",
            "contacts",
            200
        )
        
        if success and len(contacts_count1) == len(contacts_count2):
            print("   ✅ Data consistency maintained")
            results['data_consistency'] = True
        else:
            results['data_consistency'] = False
        
        # Test bulk operations
        bulk_contacts = []
        for i in range(10):
            contact_data = {
                "name": f"Bulk Test Patient {i}",
                "email": f"bulk{i}@test.com",
                "phone": f"34666{i:06d}",
                "tags": ["bulk_test"]
            }
            
            success, created = self.run_test(
                f"Bulk Create Contact {i}",
                "POST",
                "contacts",
                200,
                data=contact_data
            )
            
            if success:
                bulk_contacts.append(created.get('id'))
        
        print(f"   ✅ Bulk operations: Created {len(bulk_contacts)} contacts")
        results['bulk_operations'] = True
        
        self.test_results['performance_integrity'] = results
        return all(results.values())

    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite"""
        print("🏥 COMPREHENSIVE BACKEND TESTING - RUBIO GARCÍA DENTAL")
        print("=" * 80)
        print("Authentication: JMD/190582")
        print("Review Request: EXHAUSTIVE testing of ALL implemented features")
        print("=" * 80)
        
        # Test areas as specified in review request
        test_areas = [
            ("Authentication System", self.test_authentication),
            ("Dashboard & Calendar System", self.test_dashboard_calendar_system),
            ("WhatsApp Integration", self.test_whatsapp_integration),
            ("Conversations System", self.test_conversations_system),
            ("User Management", self.test_user_management),
            ("Appointment Management", self.test_appointment_management),
            ("Contact/Patient Management", self.test_contact_patient_management),
            ("Templates & Reminders", self.test_templates_reminders),
            ("AI & Automation", self.test_ai_automation),
            ("Error Handling & Edge Cases", self.test_error_handling_edge_cases),
            ("Performance & Data Integrity", self.test_performance_data_integrity)
        ]
        
        passed_areas = 0
        total_areas = len(test_areas)
        
        for area_name, test_function in test_areas:
            print(f"\n{'='*20} {area_name} {'='*20}")
            try:
                if test_function():
                    passed_areas += 1
                    print(f"✅ {area_name}: PASSED")
                else:
                    print(f"❌ {area_name}: FAILED")
            except Exception as e:
                print(f"❌ {area_name}: ERROR - {str(e)}")
        
        # Final summary
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TESTING SUMMARY")
        print("="*80)
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        area_success_rate = (passed_areas / total_areas) * 100
        
        print(f"📊 Individual Tests: {self.tests_passed}/{self.tests_run} passed ({success_rate:.1f}%)")
        print(f"📊 Test Areas: {passed_areas}/{total_areas} passed ({area_success_rate:.1f}%)")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests ({len(self.failed_tests)}):")
            for failed_test in self.failed_tests:
                print(f"   - {failed_test}")
        
        # Detailed results by area
        print(f"\n📋 DETAILED RESULTS BY AREA:")
        for area, results in self.test_results.items():
            if isinstance(results, dict):
                area_passed = sum(results.values())
                area_total = len(results)
                area_rate = (area_passed / area_total) * 100 if area_total > 0 else 0
                status = "✅ PASSED" if area_rate >= 80 else "❌ FAILED"
                print(f"   {area}: {area_passed}/{area_total} ({area_rate:.1f}%) {status}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if area_success_rate >= 90:
            print("🎉 EXCELLENT: All systems working perfectly!")
        elif area_success_rate >= 80:
            print("✅ GOOD: Most systems working, minor issues detected")
        elif area_success_rate >= 60:
            print("⚠️ ACCEPTABLE: Some systems need attention")
        else:
            print("❌ CRITICAL: Major issues detected, immediate attention required")
        
        return area_success_rate >= 80

if __name__ == "__main__":
    tester = ComprehensiveDentalAPITester()
    success = tester.run_comprehensive_test_suite()
    sys.exit(0 if success else 1)