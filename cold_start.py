# cold_start.py - Handles users with no history (20 competition points)
import random
from typing import Dict, List, Any, Optional
import numpy as np

class ColdStartHandler:
    """
    Handles recommendations for new users with no history.
    Uses demographic and contextual information to make intelligent guesses.
    """
    
    def __init__(self):
        # Popular items for cold-start users (from your datasets)
        self.popular_items = {
            "tech": [
                {"name": "Amazon Gift Card", "category": "gift_card", "reason": "Perfect for buying tech accessories", "score": 0.95},
                {"name": "Anker Power Bank", "category": "tech", "reason": "Keep your devices charged on the go", "score": 0.92},
                {"name": "Wireless Earbuds", "category": "tech", "reason": "Great for music and calls", "score": 0.89},
                {"name": "Phone Case", "category": "tech", "reason": "Protect your phone in style", "score": 0.85}
            ],
            "food": [
                {"name": "Jollof Rice Special", "category": "food", "reason": "Nigerian classic everyone loves", "score": 0.94},
                {"name": "Pounded Yam & Egusi", "category": "food", "reason": "Rich and satisfying meal", "score": 0.91},
                {"name": "Suya Spice Kit", "category": "food", "reason": "Make authentic Nigerian suya at home", "score": 0.88},
                {"name": "Maltina Drink", "category": "drink", "reason": "Refreshing non-alcoholic malt", "score": 0.84}
            ],
            "movies": [
                {"name": "Netflix Gift Card", "category": "gift_card", "reason": "Stream movies and series", "score": 0.93},
                {"name": "The Wedding Party", "category": "movie", "reason": "Top Nigerian comedy", "score": 0.90},
                {"name": "Showmax Subscription", "category": "streaming", "reason": "African content library", "score": 0.87}
            ],
            "shopping": [
                {"name": "Jumia Voucher", "category": "gift_card", "reason": "Shop online with discount", "score": 0.92},
                {"name": "Fashion Store Credit", "category": "shopping", "reason": "Update your wardrobe", "score": 0.88}
            ]
        }
        
        # Location-based recommendations (Nigerian context)
        self.location_recommendations = {
            "Lagos": [
                {"name": "Lagos Restaurant Week Voucher", "category": "food", "reason": "Explore top Lagos restaurants", "score": 0.91},
                {"name": "Lekki Mall Gift Card", "category": "shopping", "reason": "Shop at popular Lagos mall", "score": 0.88}
            ],
            "Abuja": [
                {"name": "Jabi Lake Mall Card", "category": "shopping", "reason": "Premium shopping experience", "score": 0.89},
                {"name": "Abuja Food Tour", "category": "food", "reason": "Discover local cuisine", "score": 0.86}
            ],
            "default": [
                {"name": "Amazon Gift Card", "category": "gift_card", "reason": "Universal shopping", "score": 0.85},
                {"name": "Local Restaurant Find", "category": "food", "reason": "Discover nearby eateries", "score": 0.82}
            ]
        }
    
    def get_cold_start_recommendations(self, user_persona: Dict[str, Any], limit: int = 5) -> List[Dict]:
        """
        Generate recommendations for users with no history.
        Uses demographics, location, and stated interests.
        """
        recommendations = []
        
        # Get user info
        age = user_persona.get('age', 25)
        location = user_persona.get('location', 'Lagos')
        interests = user_persona.get('interests', [])
        preferences = user_persona.get('preferences', {})
        price_sensitive = preferences.get('price_sensitive', True)
        
        # If user has no interests, ask clarifying questions (multi-turn)
        if not interests or len(interests) == 0:
            return self._ask_clarifying_questions()
        
        # Recommend based on interests
        for interest in interests[:3]:  # Top 3 interests
            interest_lower = interest.lower()
            if interest_lower in self.popular_items:
                for item in self.popular_items[interest_lower][:2]:
                    if item not in recommendations:
                        # Adjust score for price sensitivity
                        adjusted_score = item['score']
                        if price_sensitive:
                            adjusted_score = item['score'] * 0.95  # Slight penalty
                        item_copy = item.copy()
                        item_copy['score'] = round(adjusted_score, 2)
                        recommendations.append(item_copy)
        
        # Add location-based recommendations
        location_items = self.location_recommendations.get(location, self.location_recommendations['default'])
        for item in location_items[:2]:
            if item not in recommendations:
                recommendations.append(item)
        
        # Age-based adjustments
        if age < 25:  # Students/young adults
            student_deals = [
                {"name": "Student Discount Card", "category": "shopping", "reason": "Save money on purchases", "score": 0.87},
                {"name": "Data Bundle Package", "category": "tech", "reason": "Stay connected affordably", "score": 0.85}
            ]
            for item in student_deals:
                if item not in recommendations:
                    recommendations.append(item)
        
        # Limit and return
        recommendations = recommendations[:limit]
        
        # Add item IDs
        for i, rec in enumerate(recommendations):
            rec['item_id'] = i + 1
        
        return recommendations
    
    def _ask_clarifying_questions(self) -> List[Dict]:
        """
        Multi-turn interaction for users with no interests.
        This handles the multi-turn scenario requirement.
        """
        # Return a special response that asks questions
        return [
            {
                "item_id": -1,
                "name": "CLARIFYING_QUESTION",
                "category": "interaction",
                "reason": "What kind of products interest you? (food, tech, movies, shopping)",
                "score": 1.0,
                "requires_response": True
            },
            {
                "item_id": -2,
                "name": "FOLLOW_UP",
                "category": "interaction",
                "reason": "Also, what's your budget range? (low/medium/high)",
                "score": 0.95,
                "requires_response": True
            }
        ]
    
    def handle_multi_turn(self, user_response: str, previous_context: Dict) -> List[Dict]:
        """
        Process user responses to clarifying questions.
        This enables true multi-turn conversational recommendation.
        """
        response_lower = user_response.lower()
        
        # Parse user response for interests
        detected_interests = []
        if 'food' in response_lower or 'eat' in response_lower or 'restaurant' in response_lower:
            detected_interests.append('food')
        if 'tech' in response_lower or 'gadget' in response_lower or 'phone' in response_lower:
            detected_interests.append('tech')
        if 'movie' in response_lower or 'film' in response_lower or 'netflix' in response_lower:
            detected_interests.append('movies')
        if 'shop' in response_lower or 'buy' in response_lower or 'store' in response_lower:
            detected_interests.append('shopping')
        
        # Parse budget
        budget = "medium"
        if 'low' in response_lower or 'cheap' in response_lower or 'affordable' in response_lower:
            budget = "low"
        elif 'high' in response_lower or 'expensive' in response_lower or 'premium' in response_lower:
            budget = "high"
        
        # Generate recommendations based on detected interests
        updated_persona = {
            'interests': detected_interests if detected_interests else ['shopping', 'food'],
            'budget': budget,
            'location': previous_context.get('location', 'Lagos')
        }
        
        return self.get_cold_start_recommendations(updated_persona)
    
    def cross_domain_recommendations(self, source_domain: str, user_persona: Dict) -> List[Dict]:
        """
        Cross-domain recommendation (competition requirement).
        Recommends items from different domains than user's stated interests.
        """
        cross_domain_map = {
            "food": ["movie", "gift_card"],
            "tech": ["gift_card", "food"],
            "movies": ["food", "shopping"],
            "shopping": ["gift_card", "food"]
        }
        
        recommendations = []
        source_lower = source_domain.lower()
        
        if source_lower in cross_domain_map:
            for target_domain in cross_domain_map[source_lower]:
                if target_domain in self.popular_items:
                    for item in self.popular_items[target_domain][:2]:
                        item_copy = item.copy()
                        item_copy['reason'] = f"You like {source_domain}, you might also enjoy this {target_domain} item: " + item_copy['reason']
                        recommendations.append(item_copy)
        
        return recommendations[:5]

# Test
if __name__ == "__main__":
    handler = ColdStartHandler()
    
    # Test cold-start (no interests)
    print("Cold-start (no interests):")
    user = {"age": 22, "location": "Lagos", "interests": []}
    recs = handler.get_cold_start_recommendations(user)
    for r in recs:
        print(f"  - {r.get('name')}: {r.get('reason')}")
    
    print("\n" + "="*50)
    
    # Test cross-domain
    print("Cross-domain (from food to other domains):")
    cross_recs = handler.cross_domain_recommendations("food", user)
    for r in cross_recs:
        print(f"  - {r.get('name')}: {r.get('reason')}")