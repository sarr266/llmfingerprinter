"""
Convert Netscape cookies.txt format to cookies.json for Twikit
"""
import json
import os

def convert_netscape_to_json(cookies_txt_file='cookies.txt', output_file='cookies.json'):
    """Convert Netscape format cookies to JSON"""
    
    if not os.path.exists(cookies_txt_file):
        print(f"❌ {cookies_txt_file} not found!")
        print("\n📖 How to get cookies.txt:")
        print("1. Install browser extension: 'Get cookies.txt LOCALLY'")
        print("2. Go to twitter.com (make sure you're logged in)")
        print("3. Click extension icon → Export")
        print("4. Save as cookies.txt in this directory")
        return False
    
    cookies = {}
    
    try:
        with open(cookies_txt_file, 'r') as f:
            for line in f:
                # Skip comments and empty lines
                if line.startswith('#') or not line.strip():
                    continue
                
                # Parse Netscape format
                # domain, flag, path, secure, expiration, name, value
                parts = line.strip().split('\t')
                
                if len(parts) >= 7:
                    name = parts[5]
                    value = parts[6]
                    cookies[name] = value
        
        # Save as JSON
        with open(output_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Converted {len(cookies)} cookies")
        print(f"✅ Saved to {output_file}")
        print("\n🎯 Now run: streamlit run app.py")
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return False

def create_manual_cookies_template():
    """Create a template for manual cookie entry"""
    template = {
        "auth_token": "PASTE_YOUR_AUTH_TOKEN_HERE",
        "ct0": "PASTE_YOUR_CT0_TOKEN_HERE",
        "guest_id": "PASTE_YOUR_GUEST_ID_HERE"
    }
    
    with open('cookies_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("\n📝 Created cookies_template.json")
    print("\n🔧 To fill it manually:")
    print("1. Open Twitter in browser")
    print("2. Press F12 → Application → Cookies → twitter.com")
    print("3. Find and copy these values:")
    print("   - auth_token")
    print("   - ct0")
    print("   - guest_id")
    print("4. Paste into cookies_template.json")
    print("5. Rename to cookies.json")

if __name__ == "__main__":
    print("\n🍪 COOKIE CONVERTER")
    print("=" * 60)
    
    # Try to convert cookies.txt
    if os.path.exists('cookies.txt'):
        print("Found cookies.txt, converting...")
        convert_netscape_to_json()
    else:
        print("No cookies.txt found")
        print("\nChoose a method:")
        print("1. Export cookies.txt from browser extension")
        print("2. Manually copy cookies from DevTools")
        
        create_manual_cookies_template()