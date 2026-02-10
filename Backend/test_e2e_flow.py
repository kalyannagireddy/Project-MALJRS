import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:8000/api"

def run_e2e_test():
    print(f"🚀 Starting End-to-End System Verification...")
    print(f"Target: {BASE_URL}")
    print("-" * 50)

    # 1. Create Data (Simulate CaseContext initialization)
    case_data = {
        "caseTitle": "E2E Test Case - Property Dispute",
        "caseType": "Civil",
        "stageOfCase": "Notice",
        "courtJurisdiction": "District Court",
        "plaintiffName": "Alice Smith",
        "defendantName": "Bob Jones",
        "timeline": [
            {"id": "1", "date": "2023-01-01", "description": "Agreement signed", "peopleInvolved": "Alice, Bob", "proofAvailable": True},
            {"id": "2", "date": "2023-06-01", "description": "Payment failed", "peopleInvolved": "Bob", "proofAvailable": True}
        ],
        "claims": ["Breach of contract", "Unpaid dues"],
        "reliefRequested": "Immediate payment of dues + interest",
        "evidence": [],
        "legalIssues": [],
        "lawSections": [],
        "witnesses": [],
        "aiAssistance": ["Identify legal issues", "Find relevant precedents"],
        "strengths": "",
        "weaknesses": ""
    }

    # 2. Step 1: Create Case (Draft)
    print("\n👉 Step 1: Frontend Creates Case Draft")
    try:
        create_req = urllib.request.Request(
            f"{BASE_URL}/cases",
            data=json.dumps({"data": case_data}).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(create_req) as response:
            resp_data = json.loads(response.read().decode())
            case_id = resp_data.get("caseId")
            print(f"✅ Success. Case ID: {case_id}")
    except Exception as e:
        print(f"❌ Failed to create case: {e}")
        return

    # 3. Step 2: Update Case (Simulate user filling more details)
    print("\n👉 Step 2: Frontend Updates Case (Auto-save)")
    case_data["strengths"] = "Strong documentary evidence"
    try:
        update_req = urllib.request.Request(
            f"{BASE_URL}/cases/{case_id}",
            data=json.dumps({"data": case_data}).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        with urllib.request.urlopen(update_req) as response:
            resp_data = json.loads(response.read().decode())
            print(f"✅ Success. Case Updated.")
    except Exception as e:
        print(f"❌ Failed to update case: {e}")
        return

    # 4. Step 3: AI Processing (Simulate 'Submit Case to AI System' button)
    print("\n👉 Step 3: Trigger AI Processing (Review Page)")
    # This matches the payload sent by ReviewPage.tsx: { caseData, options }
    # options defaults to caseData.aiAssistance or ["Full Analysis"]
    ai_options = case_data["aiAssistance"]
    
    ai_req_data = {
        "caseData": case_data,
        "options": ai_options
    }
    
    # We will call the specific endpoint used by ReviewPage if known, 
    # but based on my earlier check, api.ts uses /ai/process or /ai/identify-issues.
    # ReviewPage calls CaseService.processCase -> /ai/process
    
    print(f"   Calling POST {BASE_URL}/ai/process ...")
    ai_req = urllib.request.Request(
        f"{BASE_URL}/ai/process",
        data=json.dumps(ai_req_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    start_time = time.time()
    try:
        print("   ⏳ Specific AI agents working (this may take 10-20s)...")
        with urllib.request.urlopen(ai_req) as response:
            resp_data = json.loads(response.read().decode())
            duration = time.time() - start_time
            
            if resp_data.get("success"):
                print(f"✅ AI Processing Complete in {duration:.2f}s")
                report = resp_data.get("report", {})
                print(f"   Report Summary:")
                print(f"   - Executive Summary: {len(report.get('executiveSummary', ''))} chars")
                print(f"   - Key Facts: {len(report.get('keyFacts', ''))} chars")
                print(f"   - Precedents Found: {len(report.get('precedents', []))}")
            else:
                print(f"❌ AI Processing Failed: {resp_data.get('error')}")
                
    except urllib.error.HTTPError as e:
         print(f"❌ AI Request Failed: HTTP {e.code} - {e.reason}")
         print(f"   Response: {e.read().decode()}")
    except Exception as e:
        print(f"❌ AI Request Failed: {e}")

    print("\n" + "-" * 50)
    print("✅ End-to-End Verification Finished")

if __name__ == "__main__":
    run_e2e_test()
