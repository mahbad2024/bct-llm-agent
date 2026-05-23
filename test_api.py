# test_api.py - Simple test for our API
import requests
import json

# Test Task A: Review Generation
print("Testing Task A - Review Generation...")
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

# Test Task B: Recommendation
print("\nTesting Task B - Recommendation...")
task_b_payload = {
    "user_persona": {
        "age": 22,
        "location": "Lagos",
        "interests": ["tech", "food", "movies"],
        "preferences": {"price_sensitive": True, "likes_spicy": True}
    },
    "conversation_history": []
}

print("\nTest script ready!")
print("To run this test: First run 'python main.py' in one terminal,")
print("then open another terminal and run 'python test_api.py'")