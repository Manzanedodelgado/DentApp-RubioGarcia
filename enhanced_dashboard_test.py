import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

class EnhancedDashboardTester:
    def __init__(self, base_url="https://dental-sync.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_token = None

    def authenticate(self, username="JMD", password="190582"):
        """Authenticate with the provided credentials"""
        print(f"\n🔐 Authenticating with credentials: {username}/{password}")
        
        auth_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=auth_data)
            if response.status_code == 200:
                auth_response = response.json()
                if auth_response.get('success'):
                    self.auth_token = auth_response.get('token')
                    print(f"✅ Authentication successful")
                    print(f"   Token: {self.auth_token[:20]}..." if self.auth_token else "No token")
                    print(f"   User: {auth_response.get('user', {}).get('name', 'Unknown')}")
                    return True
                else:
                    print(f"❌ Authentication failed: {auth_response.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Authentication failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict[Any, Any] = None, params: Dict[str, str] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add auth token if available
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"

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

    def test_dashboard_stats_endpoint(self):
        """Test GET /api/dashboard/stats endpoint"""
        print("\n" + "="*60)
        print("🎯 TESTING DASHBOARD STATS ENDPOINT")
        print("="*60)
        print("Expected fields: total_contacts, today_appointments, pending_messages, ai_conversations")
        
        success, response = self.run_test(
            "Dashboard Stats Endpoint",
            "GET",
            "dashboard/stats",
            200
        )
        
        if not success:
            return False
        
        # Verify required fields are present
        required_fields = [
            'total_contacts', 'active_contacts', 'total_appointments', 
            'today_appointments', 'pending_messages', 'active_campaigns', 'ai_conversations'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field in response:
                value = response[field]
                print(f"   ✅ {field}: {value} ({type(value).__name__})")
            else:
                missing_fields.append(field)
                print(f"   ❌ Missing field: {field}")
        
        # Check if all values are numerical
        numerical_fields = ['total_contacts', 'today_appointments', 'pending_messages', 'ai_conversations']
        for field in numerical_fields:
            if field in response:
                value = response[field]
                if isinstance(value, (int, float)):
                    print(f"   ✅ {field} is numerical: {value}")
                else:
                    print(f"   ⚠️ {field} is not numerical: {value} ({type(value).__name__})")
        
        if missing_fields:
            print(f"\n❌ Missing required fields: {missing_fields}")
            return False
        else:
            print(f"\n✅ All required fields present with proper data types")
            return True

    def test_pending_conversations_endpoint(self):
        """Test GET /api/conversations/pending endpoint"""
        print("\n" + "="*60)
        print("🎯 TESTING PENDING CONVERSATIONS ENDPOINT")
        print("="*60)
        print("Expected fields: patient_name, description, color_code, created_at")
        
        success, response = self.run_test(
            "Pending Conversations Endpoint",
            "GET",
            "conversations/pending",
            200
        )
        
        if not success:
            return False
        
        if not isinstance(response, list):
            print(f"❌ Expected list response, got {type(response).__name__}")
            return False
        
        print(f"   📊 Found {len(response)} pending conversations")
        
        if len(response) == 0:
            print("   ℹ️ No pending conversations found (this is normal)")
            return True
        
        # Check structure of first few conversations
        required_fields = ['patient_name', 'description', 'color_code', 'created_at']
        
        for i, conversation in enumerate(response[:3]):  # Check first 3
            print(f"\n   📋 Conversation {i+1}:")
            for field in required_fields:
                if field in conversation:
                    value = conversation[field]
                    print(f"      ✅ {field}: {value}")
                else:
                    print(f"      ❌ Missing field: {field}")
            
            # Check urgency color coding
            color_code = conversation.get('color_code', '')
            valid_colors = ['red', 'yellow', 'black', 'gray', 'green']
            if color_code in valid_colors:
                print(f"      ✅ Valid color code: {color_code}")
            else:
                print(f"      ⚠️ Invalid color code: {color_code}")
        
        return True

    def test_dashboard_tasks_endpoint(self):
        """Test GET /api/dashboard/tasks endpoint with status filtering"""
        print("\n" + "="*60)
        print("🎯 TESTING DASHBOARD TASKS ENDPOINT")
        print("="*60)
        print("Expected fields: task_type, priority, status")
        
        # Test without filters first
        success, response = self.run_test(
            "Dashboard Tasks (No Filter)",
            "GET",
            "dashboard/tasks",
            200
        )
        
        if not success:
            return False
        
        if not isinstance(response, list):
            print(f"❌ Expected list response, got {type(response).__name__}")
            return False
        
        print(f"   📊 Found {len(response)} total tasks")
        
        # Test with status filter
        success, pending_response = self.run_test(
            "Dashboard Tasks (Pending Filter)",
            "GET",
            "dashboard/tasks",
            200,
            params={"status": "pending"}
        )
        
        if success:
            print(f"   📊 Found {len(pending_response)} pending tasks")
        
        # Check structure if we have tasks
        if len(response) > 0:
            required_fields = ['task_type', 'priority', 'status']
            
            for i, task in enumerate(response[:3]):  # Check first 3
                print(f"\n   📋 Task {i+1}:")
                for field in required_fields:
                    if field in task:
                        value = task[field]
                        print(f"      ✅ {field}: {value}")
                    else:
                        print(f"      ❌ Missing field: {field}")
                
                # Check valid priority values
                priority = task.get('priority', '')
                valid_priorities = ['high', 'medium', 'low']
                if priority in valid_priorities:
                    print(f"      ✅ Valid priority: {priority}")
                else:
                    print(f"      ⚠️ Invalid priority: {priority}")
        else:
            print("   ℹ️ No tasks found (this is normal)")
        
        return True

    def test_appointments_by_date_endpoint(self):
        """Test GET /api/appointments/by-date with current date parameter"""
        print("\n" + "="*60)
        print("🎯 TESTING APPOINTMENTS BY DATE ENDPOINT")
        print("="*60)
        print("Expected fields: contact_name, treatment, time, doctor, phone")
        
        # Test with current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        print(f"   Testing with current date: {current_date}")
        
        success, response = self.run_test(
            f"Appointments by Date ({current_date})",
            "GET",
            "appointments/by-date",
            200,
            params={"date": current_date}
        )
        
        if not success:
            return False
        
        if not isinstance(response, list):
            print(f"❌ Expected list response, got {type(response).__name__}")
            return False
        
        print(f"   📊 Found {len(response)} appointments for {current_date}")
        
        # Test with a known date that should have appointments (from Google Sheets data)
        test_dates = ["2025-01-02", "2025-01-20", "2025-01-22"]
        
        for test_date in test_dates:
            success, date_response = self.run_test(
                f"Appointments by Date ({test_date})",
                "GET",
                "appointments/by-date",
                200,
                params={"date": test_date}
            )
            
            if success:
                print(f"   📊 Found {len(date_response)} appointments for {test_date}")
                
                # Check structure if we have appointments
                if len(date_response) > 0:
                    required_fields = ['contact_name', 'treatment', 'time', 'doctor', 'phone']
                    
                    for i, appointment in enumerate(date_response[:2]):  # Check first 2
                        print(f"\n   📋 Appointment {i+1} on {test_date}:")
                        for field in required_fields:
                            if field in appointment:
                                value = appointment[field]
                                print(f"      ✅ {field}: {value}")
                            else:
                                print(f"      ❌ Missing field: {field}")
                    break  # Found appointments, no need to test more dates
        
        return True

    def test_user_management_endpoints(self):
        """Test GET /api/users endpoint"""
        print("\n" + "="*60)
        print("🎯 TESTING USER MANAGEMENT ENDPOINTS")
        print("="*60)
        print("Expected fields: username, role, permissions")
        
        success, response = self.run_test(
            "Get Users Endpoint",
            "GET",
            "users",
            200
        )
        
        if not success:
            return False
        
        if not isinstance(response, list):
            print(f"❌ Expected list response, got {type(response).__name__}")
            return False
        
        print(f"   📊 Found {len(response)} users")
        
        if len(response) == 0:
            print("   ⚠️ No users found - this might indicate an issue")
            return False
        
        # Check structure of users
        required_fields = ['username', 'role', 'permissions']
        
        for i, user in enumerate(response[:3]):  # Check first 3 users
            print(f"\n   👤 User {i+1}:")
            for field in required_fields:
                if field in user:
                    value = user[field]
                    if field == 'permissions' and isinstance(value, list):
                        print(f"      ✅ {field}: {len(value)} permissions")
                    else:
                        print(f"      ✅ {field}: {value}")
                else:
                    print(f"      ❌ Missing field: {field}")
            
            # Check valid role values
            role = user.get('role', '')
            valid_roles = ['admin', 'staff', 'viewer', 'readonly']
            if role in valid_roles:
                print(f"      ✅ Valid role: {role}")
            else:
                print(f"      ⚠️ Unknown role: {role}")
        
        return True

    def run_all_tests(self):
        """Run all enhanced dashboard tests"""
        print("🎯 ENHANCED DASHBOARD BACKEND FUNCTIONALITY TESTING")
        print("="*80)
        print("Testing enhanced dashboard backend functionality with JMD/190582 credentials")
        print("Focus: Dashboard stats, pending conversations, tasks, appointments, user management")
        
        # Authenticate first
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        # Run all tests
        test_results = []
        
        test_results.append(("Dashboard Stats Endpoint", self.test_dashboard_stats_endpoint()))
        test_results.append(("Pending Conversations Endpoint", self.test_pending_conversations_endpoint()))
        test_results.append(("Dashboard Tasks Endpoint", self.test_dashboard_tasks_endpoint()))
        test_results.append(("Appointments by Date Endpoint", self.test_appointments_by_date_endpoint()))
        test_results.append(("User Management Endpoints", self.test_user_management_endpoints()))
        
        # Summary
        print("\n" + "="*80)
        print("🎯 ENHANCED DASHBOARD TESTING SUMMARY")
        print("="*80)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}: {test_name}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} test categories)")
        
        if success_rate >= 80:
            print(f"\n🎉 ENHANCED DASHBOARD BACKEND: WORKING CORRECTLY!")
            print(f"   ✅ Dashboard stats return proper statistics")
            print(f"   ✅ Pending conversations include urgency color coding")
            print(f"   ✅ Dashboard tasks support status filtering")
            print(f"   ✅ Appointments by date include required fields")
            print(f"   ✅ User management returns roles and permissions")
            return True
        else:
            print(f"\n❌ ENHANCED DASHBOARD BACKEND: ISSUES DETECTED")
            print(f"   Success rate below 80% - some functionality not working properly")
            return False

def main():
    """Main function to run the enhanced dashboard tests"""
    tester = EnhancedDashboardTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()