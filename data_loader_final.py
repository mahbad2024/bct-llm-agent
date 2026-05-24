# data_loader_final.py - Loads Amazon, Yelp, and Goodreads datasets
import pandas as pd
import json
import random
import os
from typing import Dict, List, Any, Optional
from sentence_transformers import SentenceTransformer

class DataLoader:
    def __init__(self, data_path: str = "./data"):
        self.data_path = data_path
        self.amazon_reviews = []
        self.yelp_reviews = []
        self.goodreads_reviews = []
        self.all_reviews = []
        self.embedding_model = None  
        
    def load_amazon_data(self):
        """Load Gift_Cards.csv"""
        try:
            df = pd.read_csv(f"{self.data_path}/Gift_Cards.csv")
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
    
    def load_yelp_data(self, limit: int = 20000):
        """Load Yelp reviews"""
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
    
    def load_goodreads_data(self, limit: int = 5000):
        """Load Goodreads book reviews"""
        self.goodreads_reviews = []
        try:
            count = 0
            goodreads_path = f"{self.data_path}/goodreads_reviews.json"
            
            if not os.path.exists(goodreads_path):
                print("⚠ Goodreads file not found - skipping")
                return
            
            with open(goodreads_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if count >= limit:
                        break
                    try:
                        data = json.loads(line.strip())
                        review = {
                            "source": "goodreads",
                            "rating": data.get("rating", 4),
                            "review_text": data.get("review_text", str(data.get("text", ""))),
                            "product_name": data.get("title", data.get("book_title", "Book")),
                            "user_id": str(data.get("user_id", "unknown")),
                            "category": "book"
                        }
                        self.goodreads_reviews.append(review)
                        count += 1
                    except:
                        pass
            print(f"✓ Loaded {len(self.goodreads_reviews)} Goodreads reviews")
        except Exception as e:
            print(f"Goodreads load error: {e}")
    
    def merge_datasets(self):
        """Combine all three datasets"""
        self.all_reviews = self.amazon_reviews + self.yelp_reviews + self.goodreads_reviews
        print(f"✓ Total merged reviews: {len(self.all_reviews)}")
        return self.all_reviews
    
    def load_all(self):
        """Load all datasets at once"""
        self.load_amazon_data()
        self.load_yelp_data(limit=20000)
        self.load_goodreads_data(limit=5000)
        self.merge_datasets()
    
    def get_embedding(self, text: str):
        """Get embedding for a text using sentence-transformers"""
        if self.embedding_model is None:
            print("   Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model.encode(text)
    
    def find_similar_reviews_by_embedding(self, product_details: Dict, limit: int = 3) -> List[Dict]:
        """Find reviews using semantic similarity (better than random)"""
        if not self.all_reviews:
            return []
        
        # Create query text from product details
        query = f"{product_details.get('name', '')} {product_details.get('category', '')} {product_details.get('description', '')}"
        
        # Get query embedding
        query_emb = self.get_embedding(query)
        
        # Calculate similarity with first 1000 reviews (faster)
        similarities = []
        for i, review in enumerate(self.all_reviews[:1000]):
            review_text = f"{review.get('product_name', '')} {review.get('category', '')} {review.get('review_text', '')[:200]}"
            review_emb = self.get_embedding(review_text)
            similarity = query_emb.dot(review_emb)
            similarities.append((similarity, review))
        
        # Sort by similarity and return top matches
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [review for _, review in similarities[:limit]]
    
    def get_similar_reviews(self, product_category: str, limit: int = 3) -> List[Dict]:
        """Get reviews similar to product category (fallback method)"""
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
        """Create prompt with semantically similar examples (embedding-based)"""
        # Try embedding-based retrieval first
        similar_reviews = self.find_similar_reviews_by_embedding(product_details, limit=2)
        
        # Fallback to category-based if embedding fails
        if not similar_reviews or len(similar_reviews) < 2:
            category = product_details.get("category", "general")
            similar_reviews = self.get_similar_reviews(category, limit=2)
        
        prompt = """Here are REAL reviews from the Amazon/Yelp/Goodreads datasets for similar products:

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
    loader.load_all()