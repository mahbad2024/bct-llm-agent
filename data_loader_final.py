# data_loader_final.py - Loads your actual Gift_Cards.csv and Yelp reviews
import pandas as pd
import json
import random
from typing import Dict, List, Any, Optional

class DataLoader:
    def __init__(self, data_path: str = "./data"):
        self.data_path = data_path
        self.amazon_reviews = []
        self.yelp_reviews = []
        self.all_reviews = []
        
    def load_amazon_data(self):
        """Load Gift_Cards.csv"""
        try:
            df = pd.read_csv(f"{self.data_path}/Gift_Cards.csv")
            # Convert to list of dicts
            for _, row in df.iterrows():
                review = {
                    "source": "amazon",
                    "rating": row.get("rating", row.get("star_rating", 4)),
                    "review_text": str(row.get("review", row.get("review_text", ""))),
                    "product_name": "Gift Card",
                    "user_id": str(row.get("user_id", row.get("reviewer_id", "unknown"))),
                    "category": "gift_card"
                }
                self.amazon_reviews.append(review)
            print(f"✓ Loaded {len(self.amazon_reviews)} Amazon reviews")
        except Exception as e:
            print(f"Amazon load error: {e}")
    
    def load_yelp_data(self, limit: int = 5000):
        """Load Yelp reviews (first 5000 to save memory)"""
        try:
            count = 0
            with open(f"{self.data_path}/yelp_academic_dataset_review.json", 'r', encoding='utf-8') as f:
                for line in f:
                    if count >= limit:
                        break
                    data = json.loads(line)
                    review = {
                        "source": "yelp",
                        "rating": data.get("stars", 4),
                        "review_text": data.get("text", ""),
                        "product_name": data.get("business_id", "Business"),
                        "user_id": str(data.get("user_id", "unknown")),
                        "category": "restaurant"
                    }
                    self.yelp_reviews.append(review)
                    count += 1
            print(f"✓ Loaded {len(self.yelp_reviews)} Yelp reviews")
        except Exception as e:
            print(f"Yelp load error: {e}")
    
    def merge_datasets(self):
        """Combine both datasets"""
        self.all_reviews = self.amazon_reviews + self.yelp_reviews
        print(f"✓ Total merged reviews: {len(self.all_reviews)}")
        return self.all_reviews
    
    def get_similar_reviews(self, product_category: str, limit: int = 3) -> List[Dict]:
        """Get reviews similar to product category"""
        similar = []
        for review in self.all_reviews:
            if review["category"] == product_category or review["source"] == "yelp":
                similar.append(review)
            if len(similar) >= limit:
                break
        
        if len(similar) < limit and self.all_reviews:
            random.shuffle(self.all_reviews)
            for rev in self.all_reviews:
                if rev not in similar:
                    similar.append(rev)
                if len(similar) >= limit:
                    break
        
        return similar
    
    def create_few_shot_prompt(self, user_persona: Dict, product_details: Dict) -> str:
        """Create prompt with real examples from dataset"""
        category = product_details.get("category", "general")
        similar_reviews = self.get_similar_reviews(category, limit=2)
        
        prompt = """Here are REAL reviews from the Amazon/Yelp dataset for similar products:

"""
        for i, rev in enumerate(similar_reviews, 1):
            prompt += f"[Example {i} from {rev['source'].upper()}]\n"
            prompt += f"Rating: {rev['rating']}/5\n"
            prompt += f"Review: {rev['review_text'][:400]}\n\n"
        
        prompt += f"""
Now write a new review for this product IN NIGERIAN PIDGIN/ENGLISH:

Product: {product_details.get('name', 'Unknown')}
Category: {product_details.get('category', 'general')}
Price: ₦{product_details.get('price', 'N/A')}
Description: {product_details.get('description', 'No description')}

User: {user_persona.get('age', '22')} years old from {user_persona.get('location', 'Lagos')}
Interests: {user_persona.get('interests', [])}
Preferences: {user_persona.get('preferences', {})}

Use the examples above as style guide. Write naturally like a Nigerian.
Return exactly:
RATING: [1-5]
REVIEW: [your review]
"""
        return prompt

# Test
if __name__ == "__main__":
    loader = DataLoader()
    loader.load_amazon_data()
    loader.load_yelp_data(limit=1000)  # Start with 1000 for testing
    loader.merge_datasets()