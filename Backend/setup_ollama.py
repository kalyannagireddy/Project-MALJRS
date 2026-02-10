import requests
import json
import time
import sys

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "mistral"

def check_ollama_running():
    print(f"🔍 Checking if Ollama is running at {OLLAMA_BASE_URL}...")
    try:
        response = requests.get(OLLAMA_BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running!")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama. Is it running?")
        print("   (WinError 10061 usually means the service is stopped or blocked)")
    return False

def check_model_exists():
    print(f"🔍 Checking if model '{MODEL_NAME}' is installed...")
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                if model['name'].startswith(MODEL_NAME):
                    print(f"✅ Model '{model['name']}' is already installed.")
                    return True
            print(f"⚠️ Model '{MODEL_NAME}' not found in installed models.")
    except Exception as e:
        print(f"❌ Error checking models: {e}")
    return False

def pull_model():
    print(f"⬇️ Attempting to pull '{MODEL_NAME}' via API...")
    url = f"{OLLAMA_BASE_URL}/api/pull"
    payload = {"name": MODEL_NAME}
    
    try:
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            print("   (This may take a while, please wait...)")
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        status = data.get('status', '')
                        completed = data.get('completed', 0)
                        total = data.get('total', 0)
                        
                        if total > 0:
                            percent = (completed / total) * 100
                            # Simple progress indicator
                            sys.stdout.write(f"\r   Status: {status} - {percent:.1f}%")
                            sys.stdout.flush()
                        else:
                            sys.stdout.write(f"\r   Status: {status}")
                            sys.stdout.flush()
                            
                        if data.get('error'):
                            print(f"\n❌ Error pulling model: {data['error']}")
                            return False
                    except json.JSONDecodeError:
                        pass
            print(f"\n✅ Successfully pulled '{MODEL_NAME}'!")
            return True
    except Exception as e:
        print(f"\n❌ Failed to pull model: {e}")
        return False

def main():
    if not check_ollama_running():
        sys.exit(1)
        
    if check_model_exists():
        print("🎉 Setup complete. You can now run the backend tests.")
        sys.exit(0)
        
    print("⏳ Model missing. Starting download...")
    if pull_model():
        print("🎉 Setup complete. You can now run the backend tests.")
    else:
        print("❌ Setup failed. Please try running 'ollama pull mistral' manually in a terminal where 'ollama' is recognized.")
        sys.exit(1)

if __name__ == "__main__":
    main()
