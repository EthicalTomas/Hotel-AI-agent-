"""
Quick Test Script for Hotel AI Agent

This script tests the basic structure without requiring external API keys.
Run this after installing dependencies to verify the setup.
"""

import sys
import json

def test_hotel_info():
    """Test that hotel_info.json is valid and well-formed"""
    print("Testing hotel_info.json...")
    try:
        with open('hotel_info.json', 'r') as f:
            data = json.load(f)
        
        required_fields = ['name', 'location', 'phone', 'email', 'rooms', 'facilities', 'policies']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"  ✗ Missing required fields: {missing_fields}")
            return False
        
        print(f"  ✓ Hotel name: {data['name']}")
        print(f"  ✓ Number of room types: {len(data['rooms'])}")
        print(f"  ✓ Number of facilities: {len(data['facilities'])}")
        print(f"  ✓ All required fields present")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_python_files():
    """Test that all Python files have valid syntax"""
    print("\nTesting Python files syntax...")
    files = ['ai_agent.py', 'whatsapp_handler.py', 'email_handler.py', 'email_monitor.py', 'app.py']
    
    for file in files:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"  ✓ {file} - Valid syntax")
        except SyntaxError as e:
            print(f"  ✗ {file} - Syntax error: {e}")
            return False
    
    return True

def test_env_example():
    """Test that .env.example exists and has required variables"""
    print("\nTesting .env.example...")
    try:
        with open('.env.example', 'r') as f:
            content = f.read()
        
        required_vars = [
            'OPENAI_API_KEY',
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',
            'HOTEL_EMAIL_ADDRESS',
            'HOTEL_EMAIL_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if var not in content]
        
        if missing_vars:
            print(f"  ✗ Missing environment variables: {missing_vars}")
            return False
        
        print(f"  ✓ All required environment variables documented")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Hotel AI Agent - Structure Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Hotel Info JSON", test_hotel_info()))
    results.append(("Python Syntax", test_python_files()))
    results.append(("Environment Config", test_env_example()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All structural tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and fill in your credentials")
        print("3. Customize hotel_info.json with your hotel's information")
        print("4. Run the application: python app.py")
        print("\nSee your-part.md for detailed setup instructions.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
