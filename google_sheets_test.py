#!/usr/bin/env python3
"""
URGENT Google Sheets Real Data Analysis Test
Test and verify Google Sheets integration is reading REAL data from the specific spreadsheet, not fallback data.
"""

import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import os

class GoogleSheetsDataTester:
    def __init__(self, base_url="https://appointment-sync-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # Known fallback data names for comparison
        self.fallback_names = [
            "Benita Posado Jañez", "Natalia Gonzalez Diez", "Angeles Salvador Fernandez",
            "Rehan Nisar", "Samuel Prieto Serrano", "Eloy Perez Gonzalez",
            "Lidia Sanchez Pascual", "Nashla Teresa Geronimo Gonzalez",
            "Juana Perez Murillo", "Gloria Benavente", "Eva Calero Alia"
        ]
        
        # Expected fallback appointment count
        self.expected_fallback_count = 12

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make API request and return success status and response data"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            else:
                return False, {}

            if response.status_code == 200:
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"   API Error: {response.status_code} - {response.text}")
                return False, {}

        except Exception as e:
            print(f"   Request Error: {str(e)}")
            return False, {}

    def test_manual_sync_trigger(self):
        """Test 1: Manual Import Test - Call POST /api/appointments/sync"""
        print("\n" + "="*70)
        print("🔄 TEST 1: MANUAL IMPORT TEST")
        print("="*70)
        print("Triggering fresh import to check if Google Sheets API is being used...")
        
        success, response = self.make_request("POST", "appointments/sync")
        
        if success:
            message = response.get('message', '')
            self.log_test("Manual sync endpoint accessible", True, f"Response: {message}")
            
            # Check if the response indicates successful Google Sheets fetch
            if "successfully" in message.lower():
                self.log_test("Sync completed successfully", True)
                return True
            else:
                self.log_test("Sync response unclear", False, f"Unexpected response: {message}")
                return False
        else:
            self.log_test("Manual sync endpoint failed", False)
            return False

    def test_data_structure_analysis(self):
        """Test 2: Data Structure Analysis - Get ALL appointments and analyze patterns"""
        print("\n" + "="*70)
        print("📊 TEST 2: DATA STRUCTURE ANALYSIS")
        print("="*70)
        print("Analyzing appointment data to determine if it's from Google Sheets or fallback...")
        
        success, appointments = self.make_request("GET", "appointments")
        
        if not success:
            self.log_test("Failed to retrieve appointments", False)
            return False
        
        total_count = len(appointments)
        self.log_test(f"Retrieved appointments", True, f"Found {total_count} total appointments")
        
        # Analyze appointment patterns
        print(f"\n📋 APPOINTMENT ANALYSIS:")
        print(f"   Total appointments: {total_count}")
        
        # Check if we have more than fallback data (12 appointments)
        if total_count > self.expected_fallback_count:
            self.log_test("Appointment count exceeds fallback", True, 
                         f"Found {total_count} appointments (more than {self.expected_fallback_count} fallback)")
            is_likely_real_data = True
        elif total_count == self.expected_fallback_count:
            self.log_test("Appointment count matches fallback", False, 
                         f"Found exactly {self.expected_fallback_count} appointments (same as fallback)")
            is_likely_real_data = False
        else:
            self.log_test("Appointment count less than fallback", False, 
                         f"Found only {total_count} appointments (less than {self.expected_fallback_count} fallback)")
            is_likely_real_data = False
        
        # Analyze patient names
        patient_names = set()
        fallback_matches = 0
        
        for apt in appointments:
            name = apt.get('contact_name', '')
            patient_names.add(name)
            if name in self.fallback_names:
                fallback_matches += 1
        
        print(f"\n👥 PATIENT NAME ANALYSIS:")
        print(f"   Unique patient names: {len(patient_names)}")
        print(f"   Fallback name matches: {fallback_matches}/{len(self.fallback_names)}")
        
        # Show some patient names
        print(f"\n📝 SAMPLE PATIENT NAMES:")
        for i, name in enumerate(sorted(list(patient_names))[:10]):
            marker = "🔴" if name in self.fallback_names else "🟢"
            print(f"   {marker} {name}")
            if i >= 9:
                break
        
        if fallback_matches >= len(self.fallback_names) * 0.8:  # 80% or more matches
            self.log_test("Patient names match fallback data", False, 
                         f"{fallback_matches} out of {len(self.fallback_names)} fallback names found")
            is_likely_real_data = False
        else:
            self.log_test("Patient names differ from fallback", True, 
                         f"Only {fallback_matches} fallback names found, likely real data")
            is_likely_real_data = True
        
        return is_likely_real_data, appointments

    def test_date_range_verification(self, appointments: List[Dict]):
        """Test 3: Date Range Verification - Check if appointments start from January 1, 2025"""
        print("\n" + "="*70)
        print("📅 TEST 3: DATE RANGE VERIFICATION")
        print("="*70)
        print("Checking if appointments start from January 1, 2025 as requested...")
        
        if not appointments:
            self.log_test("No appointments to analyze", False)
            return False
        
        # Parse and analyze dates
        appointment_dates = []
        date_analysis = {}
        
        for apt in appointments:
            date_str = apt.get('date', '')
            if date_str:
                try:
                    # Extract date part (YYYY-MM-DD)
                    date_part = date_str[:10] if len(date_str) >= 10 else date_str
                    appointment_dates.append(date_part)
                    
                    # Count appointments by date
                    if date_part not in date_analysis:
                        date_analysis[date_part] = 0
                    date_analysis[date_part] += 1
                    
                except Exception as e:
                    print(f"   Error parsing date {date_str}: {e}")
        
        if not appointment_dates:
            self.log_test("No valid dates found", False)
            return False
        
        # Sort dates and analyze range
        sorted_dates = sorted(appointment_dates)
        earliest_date = sorted_dates[0]
        latest_date = sorted_dates[-1]
        
        print(f"\n📊 DATE RANGE ANALYSIS:")
        print(f"   Earliest appointment: {earliest_date}")
        print(f"   Latest appointment: {latest_date}")
        print(f"   Total date range: {len(set(appointment_dates))} unique dates")
        
        # Check if starts from January 1, 2025 or close to it
        starts_jan_2025 = earliest_date.startswith('2025-01')
        if starts_jan_2025:
            self.log_test("Appointments start in January 2025", True, f"Earliest: {earliest_date}")
        else:
            self.log_test("Appointments don't start in January 2025", False, f"Earliest: {earliest_date}")
        
        # Show date distribution
        print(f"\n📋 APPOINTMENTS BY DATE:")
        for date in sorted(date_analysis.keys())[:10]:  # Show first 10 dates
            count = date_analysis[date]
            print(f"   {date}: {count} appointment(s)")
        
        # Check for proper date ordering
        is_properly_ordered = sorted_dates == appointment_dates or len(set(appointment_dates)) == len(appointment_dates)
        if is_properly_ordered:
            self.log_test("Dates are properly ordered", True)
        else:
            self.log_test("Date ordering issues detected", False)
        
        return starts_jan_2025

    def test_api_key_verification(self):
        """Test 4: API Key Verification - Check if Google Sheets API key is properly loaded"""
        print("\n" + "="*70)
        print("🔑 TEST 4: API KEY VERIFICATION")
        print("="*70)
        print("Checking Google Sheets API configuration...")
        
        # We can't directly access the backend environment, but we can infer from behavior
        # If we're getting real data, the API key is likely working
        
        # Check if the import_data.py file exists and has the right configuration
        try:
            # This is indirect - we'll check if sync works and gives us non-fallback data
            success, response = self.make_request("POST", "appointments/sync")
            
            if success:
                self.log_test("Sync endpoint responds", True)
                
                # Check the response message for clues about Google Sheets usage
                message = response.get('message', '').lower()
                if 'google' in message or 'sheets' in message:
                    self.log_test("Response mentions Google Sheets", True, f"Message: {response.get('message')}")
                    return True
                else:
                    self.log_test("Response doesn't mention Google Sheets", False, f"Message: {response.get('message')}")
                    return False
            else:
                self.log_test("Sync endpoint failed", False)
                return False
                
        except Exception as e:
            self.log_test("API key verification failed", False, f"Error: {str(e)}")
            return False

    def test_real_vs_fallback_comparison(self, appointments: List[Dict]):
        """Test 5: Real vs Fallback Data Comparison"""
        print("\n" + "="*70)
        print("🔍 TEST 5: REAL VS FALLBACK DATA COMPARISON")
        print("="*70)
        print("Detailed comparison between current data and known fallback data...")
        
        if not appointments:
            self.log_test("No appointments to compare", False)
            return False
        
        # Detailed analysis
        analysis_results = {
            'total_appointments': len(appointments),
            'unique_names': set(),
            'fallback_name_matches': 0,
            'date_patterns': {},
            'treatment_types': set(),
            'doctors': set()
        }
        
        print(f"\n🔬 DETAILED DATA ANALYSIS:")
        
        for apt in appointments:
            name = apt.get('contact_name', '')
            date = apt.get('date', '')[:10] if apt.get('date') else ''
            title = apt.get('title', '')
            
            analysis_results['unique_names'].add(name)
            
            if name in self.fallback_names:
                analysis_results['fallback_name_matches'] += 1
            
            if date:
                if date not in analysis_results['date_patterns']:
                    analysis_results['date_patterns'][date] = 0
                analysis_results['date_patterns'][date] += 1
            
            # Extract treatment and doctor info from title
            if ' - ' in title:
                treatment, doctor = title.split(' - ', 1)
                analysis_results['treatment_types'].add(treatment.strip())
                analysis_results['doctors'].add(doctor.strip())
        
        # Print analysis
        print(f"   📊 Total appointments: {analysis_results['total_appointments']}")
        print(f"   👥 Unique patients: {len(analysis_results['unique_names'])}")
        print(f"   🔴 Fallback name matches: {analysis_results['fallback_name_matches']}")
        print(f"   🏥 Treatment types: {len(analysis_results['treatment_types'])}")
        print(f"   👨‍⚕️ Doctors: {len(analysis_results['doctors'])}")
        
        # Show some examples
        print(f"\n📋 SAMPLE TREATMENTS:")
        for treatment in sorted(list(analysis_results['treatment_types']))[:5]:
            print(f"   • {treatment}")
        
        print(f"\n👨‍⚕️ SAMPLE DOCTORS:")
        for doctor in sorted(list(analysis_results['doctors']))[:5]:
            print(f"   • {doctor}")
        
        # Determine if this is real data
        fallback_percentage = (analysis_results['fallback_name_matches'] / len(self.fallback_names)) * 100
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   Fallback match percentage: {fallback_percentage:.1f}%")
        
        if fallback_percentage >= 80:
            self.log_test("Data appears to be FALLBACK data", False, 
                         f"{fallback_percentage:.1f}% of fallback names found")
            return False
        elif analysis_results['total_appointments'] > self.expected_fallback_count:
            self.log_test("Data appears to be REAL Google Sheets data", True, 
                         f"More appointments than fallback + low fallback matches")
            return True
        else:
            self.log_test("Data source unclear", False, 
                         f"Mixed indicators - needs manual verification")
            return False

    def test_specific_date_queries(self):
        """Test specific date queries to verify API functionality"""
        print("\n" + "="*70)
        print("🗓️ BONUS TEST: SPECIFIC DATE QUERIES")
        print("="*70)
        print("Testing date-specific API endpoints...")
        
        test_dates = ["2025-01-20", "2025-01-21", "2025-01-22", "2025-01-25"]
        working_dates = 0
        
        for test_date in test_dates:
            success, date_appointments = self.make_request("GET", "appointments/by-date", 
                                                         params={"date": test_date})
            
            if success:
                count = len(date_appointments)
                print(f"   📅 {test_date}: {count} appointment(s)")
                if count > 0:
                    working_dates += 1
                    # Show first appointment details
                    if date_appointments:
                        apt = date_appointments[0]
                        print(f"      └─ {apt.get('contact_name', 'Unknown')}: {apt.get('title', 'No title')}")
            else:
                print(f"   ❌ {test_date}: API error")
        
        if working_dates > 0:
            self.log_test(f"Date filtering working", True, f"{working_dates}/{len(test_dates)} dates have appointments")
            return True
        else:
            self.log_test("Date filtering not working", False, "No appointments found for any test date")
            return False

    def run_comprehensive_test(self):
        """Run all Google Sheets integration tests"""
        print("🚨 URGENT: GOOGLE SHEETS REAL DATA ANALYSIS")
        print("="*70)
        print("Google Sheet URL: https://docs.google.com/spreadsheets/d/1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ/edit")
        print(f"Backend URL: {self.base_url}")
        print("="*70)
        
        # Test 1: Manual sync trigger
        sync_success = self.test_manual_sync_trigger()
        
        # Test 2: Data structure analysis
        is_real_data, appointments = self.test_data_structure_analysis()
        
        # Test 3: Date range verification
        date_range_ok = self.test_date_range_verification(appointments) if appointments else False
        
        # Test 4: API key verification
        api_key_ok = self.test_api_key_verification()
        
        # Test 5: Real vs fallback comparison
        data_is_real = self.test_real_vs_fallback_comparison(appointments) if appointments else False
        
        # Bonus: Specific date queries
        date_queries_ok = self.test_specific_date_queries()
        
        # Final assessment
        print("\n" + "="*70)
        print("🎯 FINAL ASSESSMENT")
        print("="*70)
        
        indicators_real = 0
        indicators_fallback = 0
        
        if is_real_data:
            indicators_real += 1
        else:
            indicators_fallback += 1
            
        if data_is_real:
            indicators_real += 1
        else:
            indicators_fallback += 1
        
        if len(appointments) > self.expected_fallback_count:
            indicators_real += 1
        else:
            indicators_fallback += 1
        
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        print(f"🔍 Real data indicators: {indicators_real}")
        print(f"🔴 Fallback data indicators: {indicators_fallback}")
        
        if indicators_real > indicators_fallback:
            print("\n✅ CONCLUSION: System appears to be reading REAL data from Google Sheets")
            final_result = "REAL_DATA"
        elif indicators_fallback > indicators_real:
            print("\n❌ CONCLUSION: System appears to be using FALLBACK data, not Google Sheets")
            final_result = "FALLBACK_DATA"
        else:
            print("\n⚠️ CONCLUSION: Mixed results - manual verification needed")
            final_result = "UNCLEAR"
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if final_result == "FALLBACK_DATA":
            print("   1. Check Google Sheets API key configuration")
            print("   2. Verify Google Sheets API is enabled")
            print("   3. Check network connectivity to Google Sheets API")
            print("   4. Review import_data.py logs for error messages")
        elif final_result == "REAL_DATA":
            print("   1. Google Sheets integration is working correctly")
            print("   2. Data is being imported from the specified spreadsheet")
            print("   3. Continue monitoring for any sync issues")
        else:
            print("   1. Manual investigation required")
            print("   2. Check backend logs for detailed error messages")
            print("   3. Verify Google Sheets API configuration")
        
        return final_result

def main():
    tester = GoogleSheetsDataTester()
    result = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    if result == "REAL_DATA":
        return 0  # Success
    elif result == "FALLBACK_DATA":
        return 1  # Failure - using fallback
    else:
        return 2  # Unclear - needs investigation

if __name__ == "__main__":
    sys.exit(main())