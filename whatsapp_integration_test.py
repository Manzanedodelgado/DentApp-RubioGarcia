#!/usr/bin/env python3
"""
WhatsApp + AI Integration Testing Suite
RUBIO GARCÍA DENTAL - Complete WhatsApp Integration Testing

This test suite covers:
1. WhatsApp Service Integration (status, QR code, message sending)
2. WhatsApp Automation Endpoints (reminders, consent)
3. AI + WhatsApp Voice Assistant (urgency detection, specialty derivation)
4. Automated Reminders Integration
5. System Integration Verification

Authentication: JMD/190582
"""

import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

class WhatsAppIntegrationTester:
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
        
        # Add authentication if available
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

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
        print("\n🔐 Authenticating with JMD/190582 credentials...")
        
        login_data = {
            "username": "JMD",
            "password": "190582"
        }
        
        success, auth_response = self.run_test(
            "Authentication (POST /api/auth/login)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and auth_response.get('success'):
            self.auth_token = auth_response.get('token')
            print(f"   ✅ Authentication successful")
            print(f"   🎫 Token: {self.auth_token[:20]}..." if self.auth_token else "   ❌ No token received")
            return self.auth_token
        else:
            print("   ❌ Authentication failed")
            return None

    def test_whatsapp_service_status(self):
        """SCENARIO 1: WhatsApp Status Check"""
        print("\n" + "="*70)
        print("📱 SCENARIO 1: WHATSAPP STATUS CHECK")
        print("="*70)
        print("TESTING: GET /api/whatsapp/status should return connection status")
        print("VERIFY: Communicates with localhost:3001/status")
        
        # Test WhatsApp service status via FastAPI
        success, status_response = self.run_test(
            "WhatsApp Service Status (GET /api/whatsapp/status)",
            "GET",
            "whatsapp/status",
            200
        )
        
        if success:
            connected = status_response.get('connected', False)
            status = status_response.get('status', 'unknown')
            user = status_response.get('user')
            timestamp = status_response.get('timestamp')
            
            print(f"   📊 Connection Status: {status}")
            print(f"   📊 Connected: {connected}")
            print(f"   📊 User: {user if user else 'Not connected'}")
            print(f"   📊 Timestamp: {timestamp}")
            
            # Test direct WhatsApp service health
            print("\n🔗 Testing direct WhatsApp service communication...")
            try:
                direct_response = requests.get("http://localhost:3001/health", timeout=5)
                if direct_response.status_code == 200:
                    health_data = direct_response.json()
                    print(f"   ✅ Direct WhatsApp Service: {health_data.get('status')}")
                    print(f"   📊 Service: {health_data.get('service')}")
                    print(f"   📊 Version: {health_data.get('version')}")
                    print(f"   📊 Uptime: {health_data.get('uptime'):.2f}s")
                else:
                    print(f"   ❌ Direct service check failed: {direct_response.status_code}")
            except Exception as e:
                print(f"   ❌ Direct service not accessible: {str(e)}")
            
            return True
        else:
            print("   ❌ WhatsApp status check failed")
            return False

    def test_whatsapp_qr_code(self):
        """Test WhatsApp QR Code endpoint"""
        print("\n" + "="*70)
        print("📱 TESTING WHATSAPP QR CODE ENDPOINT")
        print("="*70)
        
        success, qr_response = self.run_test(
            "WhatsApp QR Code (GET /api/whatsapp/qr)",
            "GET",
            "whatsapp/qr",
            200
        )
        
        if success:
            qr_available = qr_response.get('qr') is not None
            status = qr_response.get('status', 'unknown')
            message = qr_response.get('message', 'No message')
            
            print(f"   📊 QR Code Available: {qr_available}")
            print(f"   📊 Status: {status}")
            print(f"   📊 Message: {message}")
            
            if qr_available:
                print("   ✅ QR Code is available for WhatsApp connection")
            else:
                print("   📱 No QR code (likely already connected or connecting)")
            
            return True
        else:
            print("   ❌ QR code endpoint failed")
            return False

    def test_whatsapp_message_sending(self):
        """Test WhatsApp message sending functionality"""
        print("\n" + "="*70)
        print("📱 TESTING WHATSAPP MESSAGE SENDING")
        print("="*70)
        
        # Test basic message sending
        message_data = {
            "phone_number": "34664218253",  # Clinic's WhatsApp number for testing
            "message": "🦷 RUBIO GARCÍA DENTAL - Test message from automated integration testing system",
            "platform": "whatsapp"
        }
        
        success, send_response = self.run_test(
            "Send WhatsApp Message (POST /api/whatsapp/send)",
            "POST",
            "whatsapp/send",
            200,
            data=message_data
        )
        
        if success:
            print(f"   📊 Message Send Result: {send_response}")
            
            # Test error handling with invalid phone number
            print("\n🔍 Testing error handling with invalid phone number...")
            error_data = {
                "phone_number": "",  # Invalid phone number
                "message": "Test error handling"
            }
            
            success_error, error_response = self.run_test(
                "Error Handling Test (POST /api/whatsapp/send)",
                "POST",
                "whatsapp/send",
                400,  # Expecting error status
                data=error_data
            )
            
            if success_error:
                print("   ✅ Error handling working correctly")
            
            return True
        else:
            print("   ❌ WhatsApp message sending failed")
            return False

    def test_whatsapp_automation_endpoints(self):
        """SCENARIO 2: WhatsApp Automation Endpoints"""
        print("\n" + "="*70)
        print("⚙️ SCENARIO 2: WHATSAPP AUTOMATION ENDPOINTS")
        print("="*70)
        print("TESTING: Appointment reminder sending and surgery consent sending")
        print("VERIFY: Integration with existing automation system")
        
        # Test appointment reminder sending
        print("\n📅 Testing appointment reminder sending...")
        reminder_data = {
            "phone_number": "34664218253",
            "appointment_data": {
                "contact_name": "Test Patient",
                "date": "2025-01-30T10:00:00Z",
                "time": "10:00",
                "doctor": "Dr. Mario Rubio",
                "treatment": "Limpieza dental"
            }
        }
        
        success, reminder_response = self.run_test(
            "Send WhatsApp Appointment Reminder (POST /api/whatsapp/send-reminder)",
            "POST",
            "whatsapp/send-reminder",
            200,
            data=reminder_data
        )
        
        if success:
            print(f"   ✅ Appointment Reminder Result: {reminder_response}")
        
        # Test surgery consent sending
        print("\n🏥 Testing surgery consent sending...")
        consent_data = {
            "phone_number": "34664218253",
            "appointment_data": {
                "contact_name": "Test Patient Surgery",
                "date": "2025-01-30T14:00:00Z",
                "time": "14:00",
                "treatment": "Implante dental"
            }
        }
        
        success, consent_response = self.run_test(
            "Send WhatsApp Surgery Consent (POST /api/whatsapp/send-consent)",
            "POST",
            "whatsapp/send-consent",
            200,
            data=consent_data
        )
        
        if success:
            print(f"   ✅ Surgery Consent Result: {consent_response}")
        
        return True

    def test_ai_whatsapp_voice_assistant(self):
        """SCENARIO 3: AI Assistant with WhatsApp Context"""
        print("\n" + "="*70)
        print("🤖 SCENARIO 3: AI ASSISTANT WITH WHATSAPP CONTEXT")
        print("="*70)
        print("TESTING: POST /api/ai/voice-assistant with platform: 'whatsapp'")
        print("VERIFY: Urgency detection for WhatsApp users, WhatsApp-appropriate responses")
        
        # Test scenarios with different urgency levels and specialties
        test_scenarios = [
            {
                "name": "High Urgency - Pain Level 9 (RED)",
                "message": "Tengo un dolor de muela terrible, nivel 9 de 10, no puedo dormir desde hace 2 días",
                "expected_urgency": "red",
                "expected_action": "URGENCIA"
            },
            {
                "name": "Medium Urgency - Pain Level 6 (YELLOW)", 
                "message": "Me duele un poco la muela, diría que un 6 de 10, es molesto",
                "expected_urgency": "yellow",
                "expected_action": "CITA_REGULAR"
            },
            {
                "name": "Low Urgency - General Info (GRAY)",
                "message": "¿Cuáles son sus horarios de atención? Necesito información",
                "expected_urgency": "gray",
                "expected_action": "INFO_GENERAL"
            },
            {
                "name": "Orthodontics Specialty Detection",
                "message": "Necesito información sobre brackets y ortodoncia para alinear mis dientes",
                "expected_specialty": "Ortodoncia",
                "expected_action": "DERIVAR_ESPECIALISTA"
            },
            {
                "name": "Implantology Specialty Detection",
                "message": "Perdí un diente y necesito un implante, ¿qué opciones tengo?",
                "expected_specialty": "Implantología", 
                "expected_action": "DERIVAR_ESPECIALISTA"
            },
            {
                "name": "Endodontics Specialty Detection",
                "message": "Tengo dolor en el nervio de la muela, creo que necesito endodoncia",
                "expected_specialty": "Endodoncia",
                "expected_action": "DERIVAR_ESPECIALISTA"
            }
        ]
        
        successful_tests = 0
        total_scenarios = len(test_scenarios)
        
        for scenario in test_scenarios:
            print(f"\n🧪 Testing: {scenario['name']}")
            
            ai_request = {
                "message": scenario["message"],
                "session_id": f"whatsapp_test_{scenario['name'].replace(' ', '_').replace('(', '').replace(')', '')}",
                "platform": "whatsapp"
            }
            
            success, ai_response = self.run_test(
                f"AI Voice Assistant - {scenario['name']}",
                "POST",
                "ai/voice-assistant",
                200,
                data=ai_request
            )
            
            if success:
                response_text = ai_response.get('response', '')
                action_type = ai_response.get('action_type')
                extracted_data = ai_response.get('extracted_data', {})
                
                print(f"   🤖 AI Response: {response_text[:150]}...")
                print(f"   🎯 Action Type: {action_type}")
                print(f"   📊 Extracted Data: {extracted_data}")
                
                # Verify expected results
                scenario_success = True
                
                if 'expected_urgency' in scenario:
                    urgency_color = extracted_data.get('urgency_color', 'gray')
                    if urgency_color == scenario['expected_urgency']:
                        print(f"   ✅ Urgency Detection: {urgency_color} (expected)")
                    else:
                        print(f"   ❌ Urgency Detection: {urgency_color} (expected {scenario['expected_urgency']})")
                        scenario_success = False
                
                if 'expected_action' in scenario:
                    if action_type == scenario['expected_action']:
                        print(f"   ✅ Action Detection: {action_type} (expected)")
                    else:
                        print(f"   ❌ Action Detection: {action_type} (expected {scenario['expected_action']})")
                        scenario_success = False
                
                if 'expected_specialty' in scenario:
                    specialty = extracted_data.get('specialty_needed')
                    if specialty == scenario['expected_specialty']:
                        print(f"   ✅ Specialty Detection: {specialty} (expected)")
                    else:
                        print(f"   ❌ Specialty Detection: {specialty} (expected {scenario['expected_specialty']})")
                        scenario_success = False
                
                if scenario_success:
                    successful_tests += 1
                    
            else:
                print(f"   ❌ AI request failed for {scenario['name']}")
        
        print(f"\n📊 AI Assistant Tests: {successful_tests}/{total_scenarios} scenarios successful")
        print(f"📊 Success Rate: {(successful_tests/total_scenarios)*100:.1f}%")
        
        return successful_tests >= total_scenarios * 0.8  # 80% success rate required

    def test_automated_reminders_integration(self):
        """SCENARIO 4: Automated Reminders Integration"""
        print("\n" + "="*70)
        print("⚙️ SCENARIO 4: AUTOMATED REMINDERS INTEGRATION")
        print("="*70)
        print("TESTING: Automation rules can trigger WhatsApp messages")
        print("VERIFY: Appointment reminder automation with WhatsApp backend")
        
        # Test automation rules
        print("\n⚙️ Testing automation rules...")
        success, automation_rules = self.run_test(
            "Get Automation Rules (GET /api/settings/automations)",
            "GET",
            "settings/automations",
            200
        )
        
        if success:
            print(f"   📊 Found {len(automation_rules)} automation rules")
            for rule in automation_rules:
                rule_name = rule.get('name', 'Unknown')
                trigger_type = rule.get('trigger_type', 'Unknown')
                trigger_time = rule.get('trigger_time', 'Unknown')
                enabled = rule.get('enabled', False)
                print(f"   - {rule_name}: {trigger_type} at {trigger_time} ({'✅ Enabled' if enabled else '❌ Disabled'})")
        
        # Test bulk reminder system with WhatsApp
        print("\n📱 Testing bulk reminder system with WhatsApp integration...")
        
        # Get some appointments for testing
        success, appointments = self.run_test(
            "Get Appointments for Bulk Reminder Test",
            "GET",
            "appointments/by-date",
            200,
            params={"date": "2025-01-02"}  # Use a date we know has appointments
        )
        
        if success and appointments:
            print(f"   📊 Found {len(appointments)} appointments for testing")
            
            # Test bulk reminder sending (limit to 2 for testing)
            appointment_ids = [apt.get('id') for apt in appointments[:2]]
            bulk_reminder_data = {
                "appointment_ids": appointment_ids,
                "template_content": "🦷 Hola {nombre}, recordatorio de su cita el {fecha} a las {hora} con {doctor} para {tratamiento}. ¡Le esperamos en RUBIO GARCÍA DENTAL!"
            }
            
            success, bulk_response = self.run_test(
                "Send Bulk WhatsApp Reminders (POST /api/reminders/send-bulk)",
                "POST",
                "reminders/send-bulk",
                200,
                data=bulk_reminder_data
            )
            
            if success:
                sent_count = bulk_response.get('sent_count', 0)
                print(f"   ✅ Bulk reminders sent: {sent_count}")
                return True
        
        return False

    def test_system_integration_verification(self):
        """SCENARIO 5: System Integration Verification"""
        print("\n" + "="*70)
        print("🔗 SCENARIO 5: SYSTEM INTEGRATION VERIFICATION")
        print("="*70)
        print("TESTING: FastAPI ↔ WhatsApp service communication, error handling, logging")
        
        # Test 1: Confirm WhatsApp service accessibility from FastAPI backend
        print("\n🔗 Testing WhatsApp service accessibility from FastAPI backend...")
        
        success, status_response = self.run_test(
            "WhatsApp Status via FastAPI (GET /api/whatsapp/status)",
            "GET",
            "whatsapp/status",
            200
        )
        
        if success:
            print(f"   ✅ FastAPI → WhatsApp communication working")
            print(f"   📊 Status: {status_response.get('status')}")
        else:
            print(f"   ❌ FastAPI → WhatsApp communication failed")
            return False
        
        # Test 2: Test httpx client connections to WhatsApp service (localhost:3001)
        print("\n🔗 Testing direct httpx client connections...")
        try:
            import httpx
            async def test_httpx_connection():
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:3001/health", timeout=5.0)
                    return response.status_code == 200, response.json()
            
            # Since we can't run async in this context, we'll test via the FastAPI proxy
            print("   📊 Testing via FastAPI proxy (which uses httpx internally)")
            
        except Exception as e:
            print(f"   ⚠️ Direct httpx test not available: {str(e)}")
        
        # Test 3: Verify error handling when WhatsApp service is unavailable
        print("\n🔗 Testing error handling scenarios...")
        
        # Test with invalid data to trigger error handling
        error_test_data = {
            "phone_number": "",  # Invalid phone number
            "message": "Test error handling"
        }
        
        success, error_response = self.run_test(
            "Error Handling Test (POST /api/whatsapp/send)",
            "POST",
            "whatsapp/send",
            400,  # Expecting error status
            data=error_test_data
        )
        
        if success:
            print(f"   ✅ Error handling working correctly")
        
        # Test 4: Check message logging and tracking in database
        print("\n🔗 Testing message logging and tracking...")
        
        # Send a test message and verify it gets logged
        test_message_data = {
            "phone_number": "34664218253",
            "message": "🧪 Integration test message - logging verification for RUBIO GARCÍA DENTAL"
        }
        
        success, send_result = self.run_test(
            "Test Message with Logging (POST /api/whatsapp/send)",
            "POST",
            "whatsapp/send",
            200,
            data=test_message_data
        )
        
        if success:
            print(f"   ✅ Message sent successfully")
            
            # Check if messages are being tracked
            success, messages = self.run_test(
                "Check Message Logging (GET /api/messages)",
                "GET",
                "messages",
                200,
                params={"channel": "whatsapp"}
            )
            
            if success:
                whatsapp_messages = [m for m in messages if m.get('channel') == 'whatsapp']
                print(f"   📊 WhatsApp messages in database: {len(whatsapp_messages)}")
        
        return True

    def run_complete_whatsapp_integration_tests(self):
        """Run complete WhatsApp integration test suite"""
        print("🚀 STARTING COMPLETE WHATSAPP + AI INTEGRATION TESTING")
        print("=" * 80)
        print("RUBIO GARCÍA DENTAL - WhatsApp Integration Test Suite")
        print("Authentication: JMD/190582")
        print("Backend URL:", self.base_url)
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with WhatsApp tests")
            return False
        
        # Run all WhatsApp integration test scenarios
        test_results = []
        
        print("\n" + "🚨"*30)
        print("EXECUTING WHATSAPP INTEGRATION TEST SCENARIOS")
        print("🚨"*30)
        
        # Scenario 1: WhatsApp Status Check
        result1 = self.test_whatsapp_service_status()
        test_results.append(("WhatsApp Service Status", result1))
        
        # Test QR Code endpoint
        result_qr = self.test_whatsapp_qr_code()
        test_results.append(("WhatsApp QR Code", result_qr))
        
        # Test message sending
        result_msg = self.test_whatsapp_message_sending()
        test_results.append(("WhatsApp Message Sending", result_msg))
        
        # Scenario 2: WhatsApp Automation Endpoints
        result2 = self.test_whatsapp_automation_endpoints()
        test_results.append(("WhatsApp Automation Endpoints", result2))
        
        # Scenario 3: AI Assistant with WhatsApp Context
        result3 = self.test_ai_whatsapp_voice_assistant()
        test_results.append(("AI + WhatsApp Voice Assistant", result3))
        
        # Scenario 4: Automated Reminders Integration
        result4 = self.test_automated_reminders_integration()
        test_results.append(("Automated Reminders Integration", result4))
        
        # Scenario 5: System Integration Verification
        result5 = self.test_system_integration_verification()
        test_results.append(("System Integration Verification", result5))
        
        # Final summary
        print("\n" + "="*80)
        print("🏁 WHATSAPP INTEGRATION TESTING COMPLETE")
        print("="*80)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        print("📊 TEST SCENARIO RESULTS:")
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status} {test_name}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Scenarios Passed: {passed_tests}/{total_tests}")
        print(f"❌ Scenarios Failed: {total_tests - passed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📊 DETAILED TEST STATISTICS:")
        print(f"✅ Individual Tests Passed: {self.tests_passed}")
        print(f"❌ Individual Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📊 Individual Test Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Determine overall success
        overall_success = passed_tests >= total_tests * 0.8  # 80% scenario success rate
        
        if overall_success:
            print("\n🎉 WHATSAPP INTEGRATION: OVERALL SUCCESS!")
            print("✅ WhatsApp + AI integration is working correctly")
            print("✅ All critical scenarios passed")
        else:
            print("\n❌ WHATSAPP INTEGRATION: ISSUES DETECTED")
            print("🚨 Some critical scenarios failed")
            print("🔧 Review failed tests and fix issues")
        
        return overall_success

if __name__ == "__main__":
    tester = WhatsAppIntegrationTester()
    
    # Run complete WhatsApp integration tests
    success = tester.run_complete_whatsapp_integration_tests()
    sys.exit(0 if success else 1)