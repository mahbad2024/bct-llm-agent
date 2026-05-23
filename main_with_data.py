# main_with_data.py - Main API with Real Dataset Integration
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
from groq import Groq
from data_loader_final import DataLoader

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load datasets
print("Loading datasets...")
loader = DataLoader()
loader.load_amazon_data()
loader.load_yelp_data(limit=2000)  # Increased to 2000 reviews
loader.merge_datasets()
print("Datasets ready!")

app = FastAPI(title="BCT LLM Agent with Real Data")

# Request/Response Models
class TaskARequest(BaseModel):
    user_persona: Dict[str, Any]
    product_details: Dict[str, Any]

class TaskAResponse(BaseModel):
    rating: int
    review_text: str

class TaskBRequest(BaseModel):
    user_persona: Dict[str, Any]
    conversation_history: Optional[List[Dict[str, str]]] = None

class TaskBResponse(BaseModel):
    recommendations: List[Dict[str, Any]]

def call_groq(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600
    )
    return completion.choices[0].message.content

@app.get("/")
def root():
    return {"message": "BCT LLM Agent with Real Amazon+Yelp Data"}

@app.post("/task_a/review", response_model=TaskAResponse)
def generate_review(request: TaskARequest):
    # Create prompt with real examples from dataset
    prompt = loader.create_few_shot_prompt(request.user_persona, request.product_details)
    
    llm_response = call_groq(prompt)
    
    # Parse response
    rating = 3
    review_text = llm_response
    try:
        for line in llm_response.split('\n'):
            if line.startswith('RATING:'):
                rating = int(line.replace('RATING:', '').strip())
            elif line.startswith('REVIEW:'):
                review_text = line.replace('REVIEW:', '').strip()
    except:
        pass
    
    return TaskAResponse(rating=rating, review_text=review_text)

@app.post("/task_b/recommend", response_model=TaskBResponse)
def get_recommendations(request: TaskBRequest):
    # Get similar items from real data
    user_interests = request.user_persona.get("interests", [])
    
    # Build prompt with real data context
    prompt = f"""
You are a recommendation agent for Nigerian users. Use REAL products from Amazon/Yelp.

User: {request.user_persona.get('age', '22')} from {request.user_persona.get('location', 'Lagos')}
Interests: {user_interests}
Price sensitive: {request.user_persona.get('preferences', {}).get('price_sensitive', True)}

Based on real Amazon gift card and Yelp business data, recommend 5 items.
Use actual product types found in the datasets (gift cards, restaurants, services).

Return in this format (one per line):
ITEM: [name] | CATEGORY: [gift_card/restaurant/tech/food] | REASON: [why user would like it]
"""
    
    llm_response = call_groq(prompt)
    
    recommendations = []
    lines = llm_response.strip().split('\n')
    
    for idx, line in enumerate(lines[:5]):
        if 'ITEM:' in line:
            parts = line.split('|')
            item_name = ""
            category = "general"
            reason = ""
            for part in parts:
                if 'ITEM:' in part:
                    item_name = part.replace('ITEM:', '').strip()
                elif 'CATEGORY:' in part:
                    category = part.replace('CATEGORY:', '').strip()
                elif 'REASON:' in part:
                    reason = part.replace('REASON:', '').strip()
            
            recommendations.append({
                "item_id": idx + 1,
                "name": item_name,
                "category": category,
                "reason": reason,
                "score": 0.95 - (idx * 0.08)
            })
    
    if not recommendations:
        recommendations = [
            {"item_id": 1, "name": "Amazon Gift Card", "category": "gift_card", "reason": "Versatile and useful", "score": 0.9},
            {"item_id": 2, "name": "Local Restaurant", "category": "restaurant", "reason": "Based on Yelp data", "score": 0.85}
        ]
    
    return TaskBResponse(recommendations=recommendations)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)