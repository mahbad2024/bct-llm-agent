# test_api_v2.py - Actually tests your API endpoints
import requests
import json

API_BASE = "http://localhost:8000"

# Test Task A: Review Generation
print("=" * 50)
print("Testing Task A - Review Generation")
print("=" * 50)

task_a_payload = {
    "user_persona": {
        "age": 22,
        "location": "Lagos",
        "interests": ["tech", "food", "movies"],
        "preferences": {"price_sensitive": True, "likes_spicy": True}
    },
    "product_details": {
        "name": "Jollof Rice Special",
        "category": "food",
        "price": 2500,
        "description": "Authentic Nigerian jollof rice with chicken"
    }
}

print(f"Request payload: {json.dumps(task_a_payload, indent=2)}")
print("\nSending request to /task_a/review...")

try:
    response = requests.post(f"{API_BASE}/task_a/review", json=task_a_payload)
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test Task B: Recommendation
print("\n" + "=" * 50)
print("Testing Task B - Recommendation")
print("=" * 50)

task_b_payload = {
    "user_persona": {
        "age": 22,
        "location": "Lagos",
        "interests": ["tech", "food", "movies"],
        "preferences": {"price_sensitive": True, "likes_spicy": True}
    },
    "conversation_history": []
}

print(f"Request payload: {json.dumps(task_b_payload, indent=2)}")
print("\nSending request to /task_b/recommend...")

try:
    response = requests.post(f"{API_BASE}/task_b/recommend", json=task_b_payload)
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Test completed!")