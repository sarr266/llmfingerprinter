"""
Extract Twitter cookies from your browser to bypass Cloudflare
Run this AFTER you've logged into Twitter in your browser
"""

def extract_cookies_chrome():
    """Extract cookies from Chrome (Windows/Mac/Linux)"""
    print("🍪 EXTRACTING COOKIES FROM CHROME")
    print("=" * 60)
    
    try:
        import browser_cookie3
        
        print("\n1️⃣ Getting cookies from Chrome...")
        cookies = browser_cookie3.chrome(domain_name='twitter.com')
        
        # Convert to Twikit format
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie.name] = cookie.value
        
        # Save to cookies.json
        import json
        with open('cookies.json', 'w') as f:
            json.dump(cookie_dict, f, indent=2)
        
        print("✅ Cookies extracted successfully!")
        print(f"✅ Saved to cookies.json ({len(cookie_dict)} cookies)")
        print("\n🎯 Now run: streamlit run app.py")
        return True
        
    except ImportError:
        print("❌ browser_cookie3 not installed")
        print("\n📦 Install it: pip install browser-cookie3")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try manual method below")
        return False

def manual_cookie_instructions():
    """Show manual cookie extraction instructions"""
    print("\n" + "=" * 60)
    print("📖 MANUAL COOKIE EXTRACTION METHOD")
    print("=" * 60)
    
    print("\n🔧 METHOD 1: Using Browser Extension (EASIEST)")
    print("-" * 60)
    print("1. Open Twitter in Chrome/Firefox")
    print("2. Make sure you're LOGGED IN")
    print("3. Install extension: 'Get cookies.txt LOCALLY'")
    print("   Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally")
    print("4. Click the extension icon on twitter.com")
    print("5. Click 'Export' → Save as cookies.txt")
    print("6. Run this script to convert:")
    print("   python convert_cookies.py")
    
    print("\n🔧 METHOD 2: Using Browser DevTools")
    print("-" * 60)
    print("1. Open Twitter in browser")
    print("2. Press F12 to open DevTools")
    print("3. Go to 'Application' tab")
    print("4. Click 'Cookies' → 'https://twitter.com'")
    print("5. Copy these cookies to cookies.json:")
    print("   - auth_token")
    print("   - ct0")
    print("   - guest_id")
    
    print("\n📝 Example cookies.json format:")
    print("-" * 60)
    print('''{
  "auth_token": "your_auth_token_here",
  "ct0": "your_ct0_token_here",
  "guest_id": "your_guest_id_here"
}''')
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n🎯 TWITTER COOKIE EXTRACTOR")
    print("=" * 60)
    print("This will extract cookies from your logged-in browser")
    print("to bypass Cloudflare blocks when using Twikit")
    print("=" * 60)
    
    # Try automatic extraction
    success = extract_cookies_chrome()
    
    if not success:
        # Show manual instructions
        manual_cookie_instructions()
        
        print("\n" + "=" * 60)
        print("⚠️  IMPORTANT: You must be logged into Twitter in your browser!")
        print("=" * 60)