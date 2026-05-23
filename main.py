# BCT LLM Agent - Main API Server with Groq LLM Integration
# Task A: User Modeling (Review Generation)
# Task B: Recommendation

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Create FastAPI app
app = FastAPI(title="BCT LLM Agent", description="User Modeling & Recommendation Agent")

# ============ Request/Response Models ============

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

# ============ Helper Functions ============

def call_groq_llm(prompt: str) -> str:
    """Send prompt to Groq LLM and return response"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Error generating response"

# ============ API Endpoints ============

@app.get("/")
def root():
    return {"message": "BCT LLM Agent is running", "tasks": ["Task A: Review Generation", "Task B: Recommendation"]}

@app.post("/task_a/review", response_model=TaskAResponse)
def generate_review(request: TaskARequest):
    # Build prompt for review generation with Nigerian context
    prompt = f"""
You are simulating a Nigerian user writing a product review.

User Persona:
- Age: {request.user_persona.get('age', 'unknown')}
- Location: {request.user_persona.get('location', 'Nigeria')}
- Interests: {request.user_persona.get('interests', [])}
- Preferences: {request.user_persona.get('preferences', {})}

Product Details:
- Name: {request.product_details.get('name', 'unknown')}
- Category: {request.product_details.get('category', 'general')}
- Price: ₦{request.product_details.get('price', 'unknown')}
- Description: {request.product_details.get('description', 'No description')}

Write a realistic review from this user's perspective. Use Nigerian English/Pidgin naturally (e.g., "This food dey sweet", "The thing soft well well", "Abeg o").

Your response must be in this exact format:
RATING: [number 1-5]
REVIEW: [your review text]

Only respond with the rating and review, nothing else.
"""
    
    llm_response = call_groq_llm(prompt)
    
    # Parse LLM response
    rating = 3  # default
    review_text = llm_response
    
    try:
        lines = llm_response.split('\n')
        for line in lines:
            if line.startswith('RATING:'):
                rating = int(line.replace('RATING:', '').strip())
            elif line.startswith('REVIEW:'):
                review_text = line.replace('REVIEW:', '').strip()
    except:
        pass
    
    return TaskAResponse(rating=rating, review_text=review_text)

@app.post("/task_b/recommend", response_model=TaskBResponse)
def get_recommendations(request: TaskBRequest):
    # Build prompt for personalized recommendations
    prompt = f"""
You are a recommendation agent for Nigerian users.

User Persona:
- Age: {request.user_persona.get('age', 'unknown')}
- Location: {request.user_persona.get('location', 'Nigeria')}
- Interests: {request.user_persona.get('interests', [])}
- Preferences: {request.user_persona.get('preferences', {})}

Based on this user profile, recommend 5 products (can be movies, food, drinks, or other items).
Consider Nigerian context: price sensitivity, local brands, cultural relevance.

Return recommendations in this exact format (one per line):
ITEM: [item name] | CATEGORY: [category] | REASON: [why this user would like it]

Only return the recommendations, nothing else.
"""
    
    llm_response = call_groq_llm(prompt)
    
    # Parse LLM response into recommendations list
    recommendations = []
    lines = llm_response.strip().split('\n')
    
    for idx, line in enumerate(lines[:5]):  # max 5 recommendations
        if 'ITEM:' in line:
            parts = line.split('|')
            item_name = ""
            category = "general"
            reason = ""
            
            for part in parts:
                if part.strip().startswith('ITEM:'):
                    item_name = part.replace('ITEM:', '').strip()
                elif part.strip().startswith('CATEGORY:'):
                    category = part.replace('CATEGORY:', '').strip()
                elif part.strip().startswith('REASON:'):
                    reason = part.replace('REASON:', '').strip()
            
            recommendations.append({
                "item_id": idx + 1,
                "name": item_name,
                "category": category,
                "reason": reason,
                "score": 0.9 - (idx * 0.05)
            })
    
    # If parsing failed, provide fallback recommendations
    if not recommendations:
        recommendations = [
            {"item_id": 1, "name": "Jollof Rice Special", "category": "food", "reason": "Popular Nigerian dish", "score": 0.9},
            {"item_id": 2, "name": "Shanko Beer", "category": "drink", "reason": "Local favorite", "score": 0.85},
        ]
    
    return TaskBResponse(recommendations=recommendations)

# ============ Run Server ============
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)