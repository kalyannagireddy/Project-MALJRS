import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://localhost:8000/api"

def run_test():
    print(f"Testing Backend at {BASE_URL}...")
    
    # 1. Test Health
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health") as response:
            data = json.loads(response.read().decode())
            print(f"✅ Health Check: {data}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return

    # 2. Create a Case
    case_data = {
        "caseTitle": "Test Case",
        "caseType": "Civil",
        "stageOfCase": "Filed",
        "courtJurisdiction": "Test Court",
        "plaintiffName": "John Doe",
        "defendantName": "Jane Doe",
        "timeline": [],
        "claims": [],
        "evidence": [],
        "legalIssues": [],
        "lawSections": [],
        "witnesses": [],
        "aiAssistance": [],
        "reliefRequested": "",
        "strengths": "",
        "weaknesses": ""
    }
    
    create_req = urllib.request.Request(
        f"{BASE_URL}/cases",
        data=json.dumps({"data": case_data}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    case_id = None
    try:
        with urllib.request.urlopen(create_req) as response:
            data = json.loads(response.read().decode())
            case_id = data.get("caseId")
            print(f"✅ Case Created: ID {case_id}")
    except Exception as e:
        print(f"❌ Create Case Failed: {e}")
        return

    # 3. Test AI Endpoint (Identify Issues - lightweight)
    ai_req_data = {
        "caseData": case_data,
        "options": ["Identify legal issues"]
    }
    
    ai_req = urllib.request.Request(
        f"{BASE_URL}/ai/identify-issues",
        data=json.dumps(ai_req_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        print("⏳ Testing AI Endpoint (this might take a few seconds)...")
        with urllib.request.urlopen(ai_req) as response:
            data = json.loads(response.read().decode())
            print(f"✅ AI Identify Issues: Success")
            print(f"   Issues Found: {len(data.get('issues', []))}")
    except urllib.error.HTTPError as e:
         print(f"❌ AI Test Failed: HTTP {e.code} - {e.reason}")
         error_content = e.read().decode()
         print(f"   Response: {error_content}")
    except Exception as e:
        print(f"❌ AI Test Failed: {e}")

if __name__ == "__main__":
    run_test()
