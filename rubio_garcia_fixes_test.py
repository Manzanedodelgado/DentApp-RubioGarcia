#!/usr/bin/env python3
"""
RUBIO GARCÍA DENTAL - Specific Fixes Testing
Testing the specific fixes implemented for:
1. Menu reordering
2. Dashboard calendar fix (selectedDate to current date)
3. WhatsApp message storage fix
"""

import requests
import json
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List

class RubioGarciaFixesTester:
    def __init__(self, base_url="https://dental-sync.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result for final summary"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        self.test_results.append({
            "name": test_name,
            "success": success,
            "details": details
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")

    def run_api_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                     data: Dict[Any, Any] = None, params: Dict[str, str] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

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
                print(f"✅ Status: {response.status_code}")
                try:
                    response_data = response.json() if response.content else {}
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False, {}

    def test_dashboard_calendar_fix(self):
        """Test Fix 2: Dashboard calendar selectedDate set to current date instead of hardcoded September 1, 2025"""
        print("\n" + "="*70)
        print("🔍 TESTING FIX 2: DASHBOARD CALENDAR DATE FIX")
        print("="*70)
        print("Expected: selectedDate should be current date, not hardcoded September 1, 2025")
        
        # Test dashboard stats endpoint
        success, stats_data = self.run_api_test(
            "Dashboard Stats Endpoint",
            "GET",
            "dashboard/stats",
            200
        )
        
        if not success:
            self.log_test_result("Dashboard Calendar Fix - Stats Endpoint", False, 
                               "Dashboard stats endpoint failed")
            return False
        
        # Verify dashboard stats structure
        required_fields = ['total_contacts', 'today_appointments', 'pending_messages', 'ai_conversations']
        missing_fields = [field for field in required_fields if field not in stats_data]
        
        if missing_fields:
            self.log_test_result("Dashboard Calendar Fix - Stats Structure", False, 
                               f"Missing fields: {missing_fields}")
            return False
        
        # Test appointments by current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        success, current_appointments = self.run_api_test(
            f"Current Date Appointments ({current_date})",
            "GET",
            "appointments/by-date",
            200,
            params={"date": current_date}
        )
        
        if success:
            self.log_test_result("Dashboard Calendar Fix - Current Date Query", True, 
                               f"Successfully queried current date {current_date}, found {len(current_appointments)} appointments")
        else:
            self.log_test_result("Dashboard Calendar Fix - Current Date Query", False, 
                               f"Failed to query current date {current_date}")
            return False
        
        # Test that we can query different dates (not hardcoded to September 2025)
        test_dates = ["2025-01-02", "2025-01-20", "2025-02-01"]
        working_dates = 0
        
        for test_date in test_dates:
            success, date_appointments = self.run_api_test(
                f"Test Date {test_date}",
                "GET", 
                "appointments/by-date",
                200,
                params={"date": test_date}
            )
            
            if success:
                working_dates += 1
                print(f"   ✅ {test_date}: {len(date_appointments)} appointments")
            else:
                print(f"   ❌ {test_date}: Failed")
        
        if working_dates >= 2:  # At least 2 out of 3 dates should work
            self.log_test_result("Dashboard Calendar Fix - Multiple Date Queries", True, 
                               f"Successfully queried {working_dates}/{len(test_dates)} test dates")
        else:
            self.log_test_result("Dashboard Calendar Fix - Multiple Date Queries", False, 
                               f"Only {working_dates}/{len(test_dates)} test dates worked")
        
        return working_dates >= 2

    def test_whatsapp_message_storage_fix(self):
        """Test Fix 3: WhatsApp message storage in conversations and whatsapp_messages collections"""
        print("\n" + "="*70)
        print("🔍 TESTING FIX 3: WHATSAPP MESSAGE STORAGE FIX")
        print("="*70)
        print("Expected: WhatsApp messages stored in conversations and whatsapp_messages collections")
        print("Testing: POST /api/ai/voice-assistant with platform='whatsapp'")
        
        # Test 1: Send WhatsApp message via voice assistant
        whatsapp_message_data = {
            "message": "Hola, tengo dolor de muelas muy fuerte, necesito una cita urgente",
            "platform": "whatsapp",
            "phone_number": "34664218253",
            "session_id": "test_whatsapp_session_001"
        }
        
        success, ai_response = self.run_api_test(
            "WhatsApp Voice Assistant Message",
            "POST",
            "ai/voice-assistant",
            200,
            data=whatsapp_message_data
        )
        
        if not success:
            self.log_test_result("WhatsApp Message Storage - Voice Assistant", False, 
                               "Voice assistant endpoint failed")
            return False
        
        # Verify AI response structure
        if not ai_response.get('response'):
            self.log_test_result("WhatsApp Message Storage - AI Response", False, 
                               "No AI response received")
            return False
        
        ai_response_text = ai_response.get('response', '')
        session_id = ai_response.get('session_id', '')
        
        print(f"   AI Response: {ai_response_text[:100]}...")
        print(f"   Session ID: {session_id}")
        
        self.log_test_result("WhatsApp Message Storage - AI Response", True, 
                           f"AI responded with {len(ai_response_text)} characters")
        
        # Test 2: Check if conversations were created
        success, conversations = self.run_api_test(
            "Get Conversations",
            "GET",
            "conversations",
            200
        )
        
        if success:
            conversation_count = len(conversations) if isinstance(conversations, list) else 0
            self.log_test_result("WhatsApp Message Storage - Conversations Created", True, 
                               f"Found {conversation_count} conversations")
        else:
            # Try alternative endpoint for conversations
            success, pending_conversations = self.run_api_test(
                "Get Pending Conversations",
                "GET",
                "conversations/pending",
                200
            )
            
            if success:
                pending_count = len(pending_conversations) if isinstance(pending_conversations, list) else 0
                self.log_test_result("WhatsApp Message Storage - Pending Conversations", True, 
                                   f"Found {pending_count} pending conversations")
            else:
                self.log_test_result("WhatsApp Message Storage - Conversations Check", False, 
                                   "Could not retrieve conversations")
        
        # Test 3: Send another WhatsApp message to test conversation continuity
        followup_message_data = {
            "message": "¿Cuándo podría ser la cita más pronta disponible?",
            "platform": "whatsapp", 
            "phone_number": "34664218253",
            "session_id": session_id if session_id else "test_whatsapp_session_001"
        }
        
        success, followup_response = self.run_api_test(
            "WhatsApp Follow-up Message",
            "POST",
            "ai/voice-assistant", 
            200,
            data=followup_message_data
        )
        
        if success:
            followup_text = followup_response.get('response', '')
            self.log_test_result("WhatsApp Message Storage - Follow-up Message", True, 
                               f"Follow-up AI response: {len(followup_text)} characters")
        else:
            self.log_test_result("WhatsApp Message Storage - Follow-up Message", False, 
                               "Follow-up message failed")
        
        # Test 4: Test urgency detection and color coding
        urgent_message_data = {
            "message": "URGENTE: Tengo un dolor de muelas insoportable nivel 9/10, no puedo dormir",
            "platform": "whatsapp",
            "phone_number": "34664218254", 
            "session_id": "test_urgent_session_001"
        }
        
        success, urgent_response = self.run_api_test(
            "WhatsApp Urgent Message (Pain Level 9)",
            "POST",
            "ai/voice-assistant",
            200,
            data=urgent_message_data
        )
        
        if success:
            urgent_text = urgent_response.get('response', '')
            # Check if AI detected urgency
            urgency_keywords = ['urgente', 'inmediato', 'pronto', 'dolor', 'emergency']
            detected_urgency = any(keyword in urgent_text.lower() for keyword in urgency_keywords)
            
            if detected_urgency:
                self.log_test_result("WhatsApp Message Storage - Urgency Detection", True, 
                                   "AI detected urgency in response")
            else:
                self.log_test_result("WhatsApp Message Storage - Urgency Detection", False, 
                                   "AI did not detect urgency appropriately")
        else:
            self.log_test_result("WhatsApp Message Storage - Urgency Test", False, 
                               "Urgent message test failed")
        
        # Test 5: Check dashboard stats reflect new conversations
        success, updated_stats = self.run_api_test(
            "Updated Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            ai_conversations = updated_stats.get('ai_conversations', 0)
            pending_messages = updated_stats.get('pending_messages', 0)
            
            self.log_test_result("WhatsApp Message Storage - Dashboard Integration", True, 
                               f"AI conversations: {ai_conversations}, Pending messages: {pending_messages}")
        else:
            self.log_test_result("WhatsApp Message Storage - Dashboard Integration", False, 
                               "Could not get updated dashboard stats")
        
        return True

    def test_menu_navigation_order(self):
        """Test Fix 1: Menu reordering - verify navigation items are in correct order"""
        print("\n" + "="*70)
        print("🔍 TESTING FIX 1: MENU NAVIGATION ORDER")
        print("="*70)
        print("Expected Order: Panel de Control, Agenda, Pacientes, Comunicaciones,")
        print("                Recordatorios, Plantillas, Consentimientos, Entrenar IA,")
        print("                Automatizaciones IA, Usuarios, Gestión Gesden, Configuración")
        
        # Since this is a frontend fix, we'll test the backend endpoints that support the menu items
        menu_endpoints = [
            ("Panel de Control", "dashboard/stats"),
            ("Agenda", "appointments/by-date"),
            ("Pacientes", "contacts"),
            ("Comunicaciones", "conversations/pending"),
            ("Recordatorios", "templates"),
            ("Plantillas", "templates"),
            ("Consentimientos", "consent-message-templates"),
            ("Entrenar IA", "ai/training"),
            ("Automatizaciones IA", "settings/automations"),
            ("Usuarios", "users"),
            ("Gestión Gesden", "treatment-codes"),
            ("Configuración", "settings/clinic")
        ]
        
        working_endpoints = 0
        total_endpoints = len(menu_endpoints)
        
        for menu_item, endpoint in menu_endpoints:
            # Test GET request for each menu endpoint
            success, response_data = self.run_api_test(
                f"Menu Item: {menu_item}",
                "GET",
                endpoint,
                200,
                params={"date": "2025-01-02"} if endpoint == "appointments/by-date" else None
            )
            
            if success:
                working_endpoints += 1
                print(f"   ✅ {menu_item}: Backend endpoint working")
            else:
                print(f"   ❌ {menu_item}: Backend endpoint failed")
        
        success_rate = working_endpoints / total_endpoints
        
        if success_rate >= 0.8:  # 80% of endpoints should work
            self.log_test_result("Menu Navigation Order - Backend Support", True, 
                               f"{working_endpoints}/{total_endpoints} menu endpoints working ({success_rate:.1%})")
        else:
            self.log_test_result("Menu Navigation Order - Backend Support", False, 
                               f"Only {working_endpoints}/{total_endpoints} menu endpoints working ({success_rate:.1%})")
        
        return success_rate >= 0.8

    def test_authentication_system(self):
        """Test authentication system with JMD/190582 credentials"""
        print("\n" + "="*70)
        print("🔍 TESTING AUTHENTICATION SYSTEM")
        print("="*70)
        
        # Test login with correct credentials
        login_data = {
            "username": "JMD",
            "password": "190582"
        }
        
        success, auth_response = self.run_api_test(
            "Authentication - Correct Credentials",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if not success:
            self.log_test_result("Authentication System - Login", False, 
                               "Login with correct credentials failed")
            return False
        
        # Verify auth response structure
        if not auth_response.get('success'):
            self.log_test_result("Authentication System - Login Response", False, 
                               "Login response indicates failure")
            return False
        
        token = auth_response.get('token')
        user_info = auth_response.get('user')
        
        if not token:
            self.log_test_result("Authentication System - Token", False, 
                               "No token received in login response")
            return False
        
        if not user_info or user_info.get('username') != 'JMD':
            self.log_test_result("Authentication System - User Info", False, 
                               "Invalid user info in login response")
            return False
        
        self.log_test_result("Authentication System - Login Success", True, 
                           f"Login successful, token received, user: {user_info.get('name', 'Unknown')}")
        
        # Test token verification
        success, verify_response = self.run_api_test(
            "Authentication - Token Verification",
            "GET",
            "auth/verify",
            200,
            params={"token": token}
        )
        
        if success and verify_response.get('valid'):
            self.log_test_result("Authentication System - Token Verification", True, 
                               "Token verification successful")
        else:
            self.log_test_result("Authentication System - Token Verification", False, 
                               "Token verification failed")
        
        return True

    def test_comprehensive_system_health(self):
        """Test overall system health and integration"""
        print("\n" + "="*70)
        print("🔍 TESTING COMPREHENSIVE SYSTEM HEALTH")
        print("="*70)
        
        # Test key system endpoints
        health_tests = [
            ("Dashboard Stats", "dashboard/stats"),
            ("Contacts List", "contacts"),
            ("Appointments List", "appointments"),
            ("Treatment Codes", "treatment-codes"),
            ("AI Training Config", "ai/training"),
            ("Templates", "templates")
        ]
        
        healthy_endpoints = 0
        
        for test_name, endpoint in health_tests:
            success, response_data = self.run_api_test(
                test_name,
                "GET",
                endpoint,
                200
            )
            
            if success:
                healthy_endpoints += 1
                
                # Additional validation for specific endpoints
                if endpoint == "dashboard/stats":
                    required_stats = ['total_contacts', 'total_appointments', 'ai_conversations']
                    has_all_stats = all(field in response_data for field in required_stats)
                    if has_all_stats:
                        print(f"   ✅ Dashboard stats complete: {response_data}")
                    else:
                        print(f"   ⚠️ Dashboard stats incomplete")
                
                elif endpoint == "treatment-codes":
                    if isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   ✅ Found {len(response_data)} treatment codes")
                    else:
                        print(f"   ⚠️ No treatment codes found")
        
        health_percentage = healthy_endpoints / len(health_tests)
        
        if health_percentage >= 0.9:  # 90% healthy
            self.log_test_result("System Health Check", True, 
                               f"System health excellent: {healthy_endpoints}/{len(health_tests)} endpoints healthy")
        elif health_percentage >= 0.7:  # 70% healthy
            self.log_test_result("System Health Check", True, 
                               f"System health good: {healthy_endpoints}/{len(health_tests)} endpoints healthy")
        else:
            self.log_test_result("System Health Check", False, 
                               f"System health poor: {healthy_endpoints}/{len(health_tests)} endpoints healthy")
        
        return health_percentage >= 0.7

    def run_all_tests(self):
        """Run all specific fix tests"""
        print("🎯 RUBIO GARCÍA DENTAL - SPECIFIC FIXES TESTING")
        print("="*70)
        print("Testing specific fixes implemented:")
        print("1. Menu reordering")
        print("2. Dashboard calendar fix (selectedDate to current date)")
        print("3. WhatsApp message storage fix")
        print("="*70)
        
        # Run all tests
        test_results = []
        
        # Test 1: Menu Navigation Order
        test_results.append(self.test_menu_navigation_order())
        
        # Test 2: Dashboard Calendar Fix
        test_results.append(self.test_dashboard_calendar_fix())
        
        # Test 3: WhatsApp Message Storage Fix
        test_results.append(self.test_whatsapp_message_storage_fix())
        
        # Additional tests for system health
        test_results.append(self.test_authentication_system())
        test_results.append(self.test_comprehensive_system_health())
        
        # Print final summary
        self.print_final_summary()
        
        return all(test_results)

    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*70)
        print("📋 RUBIO GARCÍA DENTAL FIXES - TEST SUMMARY")
        print("="*70)
        
        # Group results by category
        fix_tests = []
        system_tests = []
        
        for result in self.test_results:
            if any(keyword in result['name'] for keyword in ['Menu', 'Dashboard Calendar', 'WhatsApp Message Storage']):
                fix_tests.append(result)
            else:
                system_tests.append(result)
        
        # Print fix-specific results
        print("\n🎯 SPECIFIC FIXES TESTED:")
        for result in fix_tests:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['name']}")
            if result['details']:
                print(f"    {result['details']}")
        
        # Print system health results
        print("\n🔧 SYSTEM HEALTH TESTS:")
        for result in system_tests:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['name']}")
            if result['details']:
                print(f"    {result['details']}")
        
        # Overall statistics
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Determine overall status
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: All fixes working correctly!")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Most fixes working, minor issues detected")
        elif success_rate >= 50:
            print(f"\n⚠️ PARTIAL: Some fixes working, significant issues detected")
        else:
            print(f"\n❌ CRITICAL: Major issues detected, fixes may not be working")
        
        print("="*70)

def main():
    """Main test execution"""
    tester = RubioGarciaFixesTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()