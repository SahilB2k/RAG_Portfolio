import requests
import re
from pathlib import Path

# Configuration
NGROK_DASHBOARDS = ["http://127.0.0.1:4040", "http://127.0.0.1:4041", "http://127.0.0.1:4042"]
API_TS_PATH = Path("mobile/services/api.ts")

def get_ngrok_url():
    for base_url in NGROK_DASHBOARDS:
        try:
            print(f"Checking Dashboard: {base_url}")
            response = requests.get(f"{base_url}/api/tunnels")
            if response.status_code != 200:
                continue
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            for tunnel in tunnels:
                addr = tunnel.get('config', {}).get('addr', '')
                print(f"  Tunnel: {tunnel.get('public_url')} -> {addr}")
                if '5000' in str(addr):
                    return tunnel['public_url']
        except Exception:
            continue
    
    print("❌ No tunnel for port 5000 found across all dashboards.")
    return None

def update_api_ts(new_url):
    if not API_TS_PATH.exists():
        print(f"Error: {API_TS_PATH} not found.")
        return

    content = API_TS_PATH.read_text()
    
    # Regex to find the BASE_URL assignment
    pattern = r"const BASE_URL = '.*';"
    replacement = f"const BASE_URL = '{new_url}';"
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        API_TS_PATH.write_text(new_content)
        print(f"✅ Updated BASE_URL to: {new_url}")
    else:
        print("ℹ️ BASE_URL is already up to date.")

if __name__ == "__main__":
    url = get_ngrok_url()
    if url:
        update_api_ts(url)
    else:
        print("❌ Could not find an active ngrok tunnel.")
