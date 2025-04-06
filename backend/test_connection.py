#!/usr/bin/env python3
import requests
import json
import sys
import os
import time
from urllib.parse import urlparse

def print_header(text):
    print("\n" + "="*50)
    print(f" {text}")
    print("="*50)

def print_result(name, result, success=True):
    if success:
        print(f"✅ {name}: {result}")
    else:
        print(f"❌ {name}: {result}")

def test_url(url, headers=None, method="GET", data=None, expected_status=200, json_response=True):
    """Test a URL and return the response"""
    print(f"\nTesting URL: {url}")
    print(f"Method: {method}")
    if headers:
        print(f"Headers: {headers}")
    
    try:
        # Add ngrok skip parameter to URL if needed
        if "ngrok" in url and "_ngrok_skip_browser_warning=true" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}_ngrok_skip_browser_warning=true"
            print(f"Modified URL: {url}")
        
        # Make the request
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "OPTIONS":
            response = requests.options(url, headers=headers, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        # Check status code
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('Content-Type', 'unknown')}")
        status_ok = response.status_code == expected_status
        
        # Check if content is HTML (might be ngrok warning)
        content_type = response.headers.get('Content-Type', '')
        if "text/html" in content_type:
            print("WARNING: Received HTML response instead of JSON!")
            print("This is likely the ngrok warning page")
            print(f"Response preview: {response.text[:100]}...")
            return {
                "status": response.status_code,
                "success": False,
                "content_type": content_type,
                "data": "HTML content (likely ngrok warning page)",
                "is_html": True
            }
        
        # Try to parse JSON
        if json_response:
            try:
                data = response.json()
                print(f"Response data: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                return {
                    "status": response.status_code,
                    "success": status_ok,
                    "content_type": content_type,
                    "data": data
                }
            except Exception as e:
                print(f"Error parsing JSON: {str(e)}")
                print(f"Response text: {response.text[:200]}...")
                return {
                    "status": response.status_code,
                    "success": False,
                    "content_type": content_type,
                    "error": str(e),
                    "data": response.text
                }
        else:
            return {
                "status": response.status_code,
                "success": status_ok,
                "content_type": content_type,
                "data": response.text
            }
    
    except Exception as e:
        print(f"Error testing URL: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def test_token(token, base_url):
    """Test if a JWT token is valid"""
    print_header("Testing JWT Token")
    
    if not token:
        print_result("Token check", "No token provided", False)
        return False
    
    print(f"Token: {token[:20]}...")
    test_auth_url = f"{base_url}/test-auth"
    
    # Set up headers with the token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Test the token
    result = test_url(test_auth_url, headers=headers)
    
    if result.get("success", False):
        data = result.get("data", {})
        if isinstance(data, dict) and data.get("authorized") == True:
            print_result("Token validation", "Valid token")
            return True
    
    print_result("Token validation", "Invalid token", False)
    return False

def test_contributions(token, base_url):
    """Test the user contributions endpoint"""
    print_header("Testing User Contributions Endpoint")
    
    # Set up headers with the token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Test the contributions endpoint
    result = test_url(f"{base_url}/user/contributions", headers=headers)
    
    if result.get("is_html", False):
        print_result("Contributions endpoint", "Received HTML instead of JSON (likely ngrok warning)", False)
        return False
    
    if result.get("success", False):
        data = result.get("data", {})
        if isinstance(data, dict) and "contributions" in data:
            count = len(data["contributions"])
            print_result("Contributions count", f"Found {count} contributions")
            if count > 0:
                print("First contribution:")
                print(json.dumps(data["contributions"][0], indent=2, ensure_ascii=False))
            return True
    
    print_result("Contributions endpoint", "Failed to get contributions", False)
    return False

def test_ngrok_confirmation(base_url):
    """Test if ngrok URL needs confirmation"""
    print_header("Testing Ngrok URL Confirmation")
    
    if "ngrok" not in base_url:
        print_result("Ngrok check", "Not using ngrok")
        return True
    
    # Test the ngrok-ready endpoint
    result = test_url(f"{base_url}/ngrok-ready")
    
    if result.get("is_html", False):
        print_result("Ngrok confirmation", "Ngrok URL needs confirmation!", False)
        print("\nOpen this URL in your browser and click 'Visit Site':")
        print(f"{base_url}/ngrok-ready")
        return False
    
    if result.get("success", False):
        print_result("Ngrok confirmation", "Ngrok URL is confirmed")
        return True
    
    print_result("Ngrok confirmation", "Could not determine ngrok status", False)
    return False

def test_uploads_access(base_url):
    """Test access to uploads directory"""
    print_header("Testing Uploads Directory Access")
    
    # Extract base URL without /api
    uploads_base = base_url.replace("/api", "")
    
    # Test access to a test file
    result = test_url(f"{uploads_base}/uploads/test-image.txt", json_response=False)
    
    if result.get("is_html", False):
        print_result("Uploads access", "Received HTML instead of file content (likely ngrok warning)", False)
        print("\nOpen this URL in your browser and click 'Visit Site':")
        print(f"{uploads_base}/uploads/test-image.txt")
        return False
    
    if result.get("success", False):
        content = result.get("data", "")
        if "test file" in content:
            print_result("Uploads access", "Successfully accessed test file")
            return True
    
    print_result("Uploads access", "Failed to access uploads directory", False)
    return False

def check_frontend_url(api_url):
    """Check if frontend environment variable is set correctly"""
    print_header("Checking Frontend Configuration")
    
    # For Azure
    if "NEXT_PUBLIC_API_URL" in os.environ:
        env_url = os.environ["NEXT_PUBLIC_API_URL"]
        print(f"NEXT_PUBLIC_API_URL environment variable: {env_url}")
        
        if env_url == api_url:
            print_result("Frontend config", "Environment variable matches the API URL")
        else:
            print_result("Frontend config", f"Environment variable ({env_url}) does not match the API URL ({api_url})", False)
            print("\nUpdate your environment variable in Azure Portal:")
            print(f"NEXT_PUBLIC_API_URL={api_url}")
    else:
        print_result("Frontend config", "NEXT_PUBLIC_API_URL environment variable not set", False)
        print("\nSet this environment variable in Azure Portal:")
        print(f"NEXT_PUBLIC_API_URL={api_url}")

def ask_for_token():
    """Ask the user for a token or try to extract it from localStorage"""
    token = input("Enter JWT token (or press Enter to skip): ").strip()
    
    if not token:
        print("No token provided.")
    
    return token

def main():
    print_header("Vietnamese Image Captioning API Test")
    
    # Ask for API URL
    default_url = "http://localhost:5000/api"
    url_input = input(f"Enter API URL [{default_url}]: ").strip()
    api_url = url_input if url_input else default_url
    
    # Ensure URL ends with /api
    if not api_url.endswith("/api"):
        if "/api" in api_url:
            # Keep URL as is
            pass
        else:
            api_url = api_url.rstrip("/") + "/api"
    
    print(f"Using API URL: {api_url}")
    
    # Extract base URL
    parsed_url = urlparse(api_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    print(f"Base URL: {base_url}")
    
    # Test basic connectivity
    print_header("Testing Basic Connectivity")
    ping_result = test_url(f"{api_url}/ngrok-ready")
    
    if not ping_result.get("success", False) and ping_result.get("is_html", False):
        print("\nNgrok warning page detected. Please confirm the URL in your browser:")
        print(f"{api_url}/ngrok-ready")
        confirm = input("Have you confirmed the URL in your browser? (y/n): ").lower()
        if confirm == 'y':
            print("Continuing with tests...")
        else:
            print("Please confirm the URL before continuing.")
            sys.exit(1)
    
    # Test if using ngrok
    is_ngrok = "ngrok" in api_url
    if is_ngrok:
        print_result("Ngrok detection", "Using ngrok URL")
        ngrok_ok = test_ngrok_confirmation(api_url)
        if not ngrok_ok:
            confirm = input("Have you confirmed the ngrok URL in your browser? (y/n): ").lower()
            if confirm != 'y':
                print("Please confirm the URL before continuing.")
                sys.exit(1)
    else:
        print_result("Ngrok detection", "Not using ngrok")
    
    # Check uploads directory
    uploads_ok = test_uploads_access(api_url)
    if not uploads_ok and is_ngrok:
        confirm = input("Have you confirmed the uploads URL in your browser? (y/n): ").lower()
        if confirm != 'y':
            print("Please access the uploads URL in your browser first.")
    
    # Ask for token
    token = ask_for_token()
    
    if token:
        # Test token
        token_ok = test_token(token, api_url)
        
        # Test contributions only if token is valid
        if token_ok:
            test_contributions(token, api_url)
    
    # Check frontend URL configuration
    check_frontend_url(api_url)
    
    # Final recommendations
    print_header("Recommendations")
    
    if is_ngrok:
        print("1. Make sure you've confirmed the ngrok URL in your browser")
        print("2. Update the NEXT_PUBLIC_API_URL environment variable in Azure Portal")
        print("3. Visit the test page: https://icy-river-037493600.6.azurestaticapps.net/test-ngrok")
    
    if not token or not test_token(token, api_url):
        print("4. Login again to get a fresh token")
    
    print("\nTest completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1) 