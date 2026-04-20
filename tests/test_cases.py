import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agent import ask


test_cases = [
    # 1️⃣ Basic Legal Knowledge (RAG)
    {
        "name": "Basic Definition",
        "query": "What is a contract?",
        "expected_contains": ["agreement", "legally", "parties"]
    },

    # 2️⃣ Legal Advice (Advise capability)
    {
        "name": "Legal Advice",
        "query": "Is a non-compete clause enforceable in India?",
        "expected_contains": ["depends", "law", "enforceable"]
    },

    # 3️⃣ Risk Analysis
    {
        "name": "Risk Analysis",
        "query": "What are the risks in unlimited liability clause?",
        "expected_contains": ["risk", "liability", "exposure"]
    },

    # 4️⃣ Tool — Deadline Calculator
    {
        "name": "Deadline Tool",
        "query": "Calculate deadline for contract starting 2026-01-01 duration 12 months notice 30 days",
        "expected_contains": ["Contract End", "Notice"]
    },

    # 5️⃣ Tool — Risk Scorer
    {
        "name": "Risk Scorer Tool",
        "query": "Score these clauses: unlimited liability, no force majeure, mutual NDA",
        "expected_contains": ["HIGH RISK", "LOW RISK", "Overall Risk"]
    },

    # 6️⃣ Tool — Legal Math
    {
        "name": "Legal Math",
        "query": "Calculate 10% penalty on 50000",
        "expected_contains": ["Penalty", "5000"]
    },

    # 7️⃣ Drafting Capability
    {
        "name": "Draft NDA",
        "query": "Draft a mutual NDA between ABC Pvt Ltd and XYZ Ltd",
        "expected_contains": ["AGREEMENT", "CONFIDENTIAL", "PARTIES"]
    },

    # 8️⃣ Document Analysis
    {
        "name": "Analyze Clause",
        "query": "Analyze this: Employee agrees to a 5-year worldwide non-compete",
        "expected_contains": ["non-compete", "risk", "analysis"]
    },
]


def run_tests():
    print("\n Running Legal Assistant Test Suite\n")
    passed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\n🔹 Test {i}: {test['name']}")
        print(f"Q: {test['query']}")

        try:
            response = ask(test["query"])
            response_lower = response.lower()

            # Check expected keywords
            success = all(word.lower() in response_lower for word in test["expected_contains"])

            if success:
                print("✅ PASSED")
                passed += 1
            else:
                print("⚠️ FAILED (missing expected keywords)")
                print("Expected:", test["expected_contains"])

            print("Response Preview:")
            print(response[:300], "...")

        except Exception as e:
            print("❌ ERROR:", str(e))

    print("\n" + "="*50)
    print(f"📊 RESULT: {passed}/{len(test_cases)} tests passed")
    print("="*50)



if __name__ == "__main__":
    run_tests()