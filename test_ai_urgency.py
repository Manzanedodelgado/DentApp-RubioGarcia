#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

class AIUrgencyTester:
    def __init__(self, base_url="https://dental-clinic-app-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

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

    def test_ai_urgency_detection_system(self):
        """Test the new AI conversation urgency system and color coding"""
        print("\n" + "="*70)
        print("🚨 TESTING AI URGENCY DETECTION SYSTEM")
        print("="*70)
        print("Testing new AI conversation urgency system with pain level detection and color coding")
        
        # Step 1: Test authentication first
        print("\n🔐 Step 1: Testing authentication...")
        auth_data = {
            "username": "JMD",
            "password": "190582"
        }
        
        success, auth_response = self.run_test(
            "Authentication (JMD/190582)",
            "POST",
            "auth/login",
            200,
            data=auth_data
        )
        
        if not success or not auth_response.get('success'):
            print("❌ CRITICAL: Authentication failed")
            return False
        
        token = auth_response.get('token')
        print(f"   ✅ Authentication successful, token: {token[:20]}...")
        
        # Step 2: Test URGENCY scenarios (Pain 8-10 - RED)
        print("\n🔴 Step 2: Testing URGENCY scenarios (Pain 8-10 - RED)...")
        urgency_scenarios = [
            "Me duele muchísimo la muela, es un dolor de 9 no puedo dormir",
            "Tengo un dolor de 10 en el diente, no se me quita con nada",
            "Dolor insoportable nivel 8, necesito ayuda urgente"
        ]
        
        urgency_results = []
        for i, message in enumerate(urgency_scenarios):
            success, response = self.run_test(
                f"Urgency Scenario {i+1} (Pain 8-10)",
                "POST",
                "ai/voice-assistant",
                200,
                data={"message": message, "session_id": f"urgency_test_{i+1}"}
            )
            
            if success:
                extracted_data = response.get('extracted_data', {})
                pain_level = extracted_data.get('pain_level')
                urgency_color = extracted_data.get('urgency_color')
                action_type = response.get('action_type')
                ai_response = response.get('response', '')
                
                print(f"   📊 Pain Level: {pain_level}, Color: {urgency_color}, Action: {action_type}")
                print(f"   💬 AI Response: {ai_response[:100]}...")
                
                if pain_level and pain_level >= 8 and urgency_color == "red":
                    print(f"   ✅ Urgency correctly detected for pain level {pain_level}")
                    urgency_results.append(True)
                else:
                    print(f"   ❌ Urgency detection failed - Expected red color for pain {pain_level}")
                    urgency_results.append(False)
            else:
                urgency_results.append(False)
        
        # Step 3: Test MODERATE scenarios (Pain 5-7 - YELLOW)
        print("\n🟡 Step 3: Testing MODERATE scenarios (Pain 5-7 - YELLOW)...")
        moderate_scenarios = [
            "Me molesta el diente, diría que un 6 de dolor",
            "Tengo dolor nivel 5, no es muy fuerte pero molesta"
        ]
        
        moderate_results = []
        for i, message in enumerate(moderate_scenarios):
            success, response = self.run_test(
                f"Moderate Scenario {i+1} (Pain 5-7)",
                "POST",
                "ai/voice-assistant",
                200,
                data={"message": message, "session_id": f"moderate_test_{i+1}"}
            )
            
            if success:
                extracted_data = response.get('extracted_data', {})
                pain_level = extracted_data.get('pain_level')
                urgency_color = extracted_data.get('urgency_color')
                ai_response = response.get('response', '')
                
                print(f"   📊 Pain Level: {pain_level}, Color: {urgency_color}")
                print(f"   💬 AI Response: {ai_response[:100]}...")
                
                if pain_level and 5 <= pain_level <= 7 and urgency_color == "yellow":
                    print(f"   ✅ Moderate urgency correctly detected for pain level {pain_level}")
                    moderate_results.append(True)
                else:
                    print(f"   ⚠️ Moderate detection issue - Expected yellow color for pain {pain_level}")
                    moderate_results.append(False)
            else:
                moderate_results.append(False)
        
        # Step 4: Test REGULAR scenarios (Pain 1-4 - GRAY/BLACK)
        print("\n⚫ Step 4: Testing REGULAR scenarios (Pain 1-4 - GRAY/BLACK)...")
        regular_scenarios = [
            "Quiero agendar una cita para limpieza",
            "Me duele un poco, nivel 2 o 3",
            "Necesito información sobre precios de implantes"
        ]
        
        regular_results = []
        for i, message in enumerate(regular_scenarios):
            success, response = self.run_test(
                f"Regular Scenario {i+1} (Pain 1-4 or no pain)",
                "POST",
                "ai/voice-assistant",
                200,
                data={"message": message, "session_id": f"regular_test_{i+1}"}
            )
            
            if success:
                extracted_data = response.get('extracted_data', {})
                pain_level = extracted_data.get('pain_level')
                urgency_color = extracted_data.get('urgency_color')
                action_type = response.get('action_type')
                ai_response = response.get('response', '')
                
                print(f"   📊 Pain Level: {pain_level}, Color: {urgency_color}, Action: {action_type}")
                print(f"   💬 AI Response: {ai_response[:100]}...")
                
                if urgency_color in ["gray", "black"]:
                    print(f"   ✅ Regular priority correctly assigned")
                    regular_results.append(True)
                else:
                    print(f"   ⚠️ Regular detection issue - Expected gray/black color")
                    regular_results.append(False)
            else:
                regular_results.append(False)
        
        # Step 5: Test SPECIALTY detection
        print("\n🏥 Step 5: Testing SPECIALTY detection...")
        specialty_scenarios = [
            ("Me duele la muela, creo que necesito endodoncia", "Endodoncia"),
            ("Quiero brackets para alinear mis dientes", "Ortodoncia"),
            ("Perdí un diente y necesito un implante", "Implantología"),
            ("Quiero blanquear mis dientes", "Estética Dental")
        ]
        
        specialty_results = []
        for i, (message, expected_specialty) in enumerate(specialty_scenarios):
            success, response = self.run_test(
                f"Specialty Detection {i+1} ({expected_specialty})",
                "POST",
                "ai/voice-assistant",
                200,
                data={"message": message, "session_id": f"specialty_test_{i+1}"}
            )
            
            if success:
                extracted_data = response.get('extracted_data', {})
                specialty_needed = extracted_data.get('specialty_needed')
                action_type = response.get('action_type')
                ai_response = response.get('response', '')
                
                print(f"   📊 Detected Specialty: {specialty_needed}, Action: {action_type}")
                print(f"   💬 AI Response: {ai_response[:100]}...")
                
                if specialty_needed == expected_specialty:
                    print(f"   ✅ Specialty correctly detected: {specialty_needed}")
                    specialty_results.append(True)
                else:
                    print(f"   ⚠️ Specialty detection issue - Expected {expected_specialty}, got {specialty_needed}")
                    specialty_results.append(False)
            else:
                specialty_results.append(False)
        
        # Step 6: Test conversation status storage
        print("\n💾 Step 6: Testing conversation status storage...")
        success, pending_conversations = self.run_test(
            "Get Pending Conversations",
            "GET",
            "conversations/pending",
            200
        )
        
        if success:
            print(f"   📊 Found {len(pending_conversations)} pending conversations")
            
            # Check if our test conversations are stored
            red_conversations = [c for c in pending_conversations if c.get('urgency_color') == 'red']
            yellow_conversations = [c for c in pending_conversations if c.get('urgency_color') == 'yellow']
            
            print(f"   🔴 Red urgency conversations: {len(red_conversations)}")
            print(f"   🟡 Yellow urgency conversations: {len(yellow_conversations)}")
            
            if red_conversations or yellow_conversations:
                print("   ✅ Conversation status storage working")
            else:
                print("   ⚠️ No urgent conversations found in storage")
        
        # Step 7: Test conversation status updates
        print("\n🔄 Step 7: Testing conversation status updates...")
        if pending_conversations:
            test_conversation = pending_conversations[0]
            conversation_id = test_conversation.get('id')
            
            if conversation_id:
                update_data = {
                    "urgency_color": "green",
                    "pending_response": False,
                    "assigned_doctor": "Dr. Mario Rubio"
                }
                
                success, update_response = self.run_test(
                    f"Update Conversation Status ({conversation_id})",
                    "PUT",
                    f"conversations/{conversation_id}/status",
                    200,
                    data=update_data
                )
                
                if success:
                    print("   ✅ Conversation status update working")
                else:
                    print("   ❌ Conversation status update failed")
        
        # Step 8: Test dashboard integration
        print("\n📊 Step 8: Testing dashboard integration...")
        success, dashboard_stats = self.run_test(
            "Dashboard Stats (Check Urgent Conversations)",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            pending_messages = dashboard_stats.get('pending_messages', 0)
            ai_conversations = dashboard_stats.get('ai_conversations', 0)
            
            print(f"   📊 Pending messages (includes urgent): {pending_messages}")
            print(f"   📊 AI conversations: {ai_conversations}")
            
            if pending_messages > 0 or ai_conversations > 0:
                print("   ✅ Dashboard integration working")
            else:
                print("   ⚠️ No urgent conversations reflected in dashboard")
        
        # Final summary
        print("\n" + "="*70)
        print("📋 AI URGENCY DETECTION SYSTEM SUMMARY")
        print("="*70)
        
        total_urgency_tests = len(urgency_results)
        passed_urgency_tests = sum(urgency_results)
        
        total_moderate_tests = len(moderate_results)
        passed_moderate_tests = sum(moderate_results)
        
        total_regular_tests = len(regular_results)
        passed_regular_tests = sum(regular_results)
        
        total_specialty_tests = len(specialty_results)
        passed_specialty_tests = sum(specialty_results)
        
        print(f"🔴 Urgency Detection (Pain 8-10): {passed_urgency_tests}/{total_urgency_tests}")
        print(f"🟡 Moderate Detection (Pain 5-7): {passed_moderate_tests}/{total_moderate_tests}")
        print(f"⚫ Regular Detection (Pain 1-4): {passed_regular_tests}/{total_regular_tests}")
        print(f"🏥 Specialty Detection: {passed_specialty_tests}/{total_specialty_tests}")
        
        total_tests = total_urgency_tests + total_moderate_tests + total_regular_tests + total_specialty_tests
        passed_tests = passed_urgency_tests + passed_moderate_tests + passed_regular_tests + passed_specialty_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 80:
            print("🎉 AI URGENCY DETECTION SYSTEM: WORKING EXCELLENTLY!")
            return True
        elif success_rate >= 60:
            print("⚠️ AI URGENCY DETECTION SYSTEM: WORKING WITH MINOR ISSUES")
            return True
        else:
            print("❌ AI URGENCY DETECTION SYSTEM: MAJOR ISSUES DETECTED")
            return False

def main():
    """Main function to run AI urgency detection tests"""
    tester = AIUrgencyTester()
    
    print("🚀 Starting AI Urgency Detection System Tests")
    print("=" * 60)
    
    try:
        success = tester.test_ai_urgency_detection_system()
        
        # Print final summary
        print("\n" + "="*60)
        print("📊 FINAL TEST SUMMARY")
        print("="*60)
        print(f"Tests Run: {tester.tests_run}")
        print(f"Tests Passed: {tester.tests_passed}")
        print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "No tests run")
        
        if success:
            print("🎉 AI Urgency Detection System tests completed successfully!")
            return 0
        else:
            print("❌ AI Urgency Detection System tests failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())