# rating_predictor.py - Improves rating accuracy (RMSE score)
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os

class RatingPredictor:
    def __init__(self, model_path="./models"):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        os.makedirs(model_path, exist_ok=True)
    
    def extract_features(self, user_persona, product_details):
        """Extract numerical features for rating prediction"""
        features = []
        
        # User features
        age = user_persona.get('age', 25)
        price_sensitive = 1 if user_persona.get('preferences', {}).get('price_sensitive', False) else 0
        likes_spicy = 1 if user_persona.get('preferences', {}).get('likes_spicy', False) else 0
        
        # Product features
        price = product_details.get('price', 1000)
        
        # Calculate price sensitivity score (higher price = lower rating for price-sensitive users)
        price_impact = price / 5000  # Normalize price to 0-1 range
        if price_sensitive:
            price_impact = price_impact * 0.7  # Reduce rating for expensive items
        
        features = [age, price_sensitive, likes_spicy, price, price_impact]
        
        # Add interest matching
        interests = user_persona.get('interests', [])
        category = product_details.get('category', 'general')
        interest_match = 1 if category in interests else 0.5
        features.append(interest_match)
        
        return np.array(features).reshape(1, -1)
    
    def predict_rating(self, user_persona, product_details):
        """Predict star rating (1-5) for a user-product pair"""
        features = self.extract_features(user_persona, product_details)
        
        # If model is trained, use it
        if self.model is not None:
            prediction = self.model.predict(features)[0]
        else:
            # Fallback: rule-based prediction
            prediction = self._rule_based_prediction(user_persona, product_details)
        
        # Clamp to 1-5 range and round to nearest 0.5 (for star ratings)
        prediction = max(1, min(5, prediction))
        return round(prediction * 2) / 2  # Round to 0.5 increments
    
    def _rule_based_prediction(self, user_persona, product_details):
        """Fallback rule-based rating prediction"""
        base_rating = 4.0
        
        # Price sensitivity adjustment
        price = product_details.get('price', 2500)
        price_sensitive = user_persona.get('preferences', {}).get('price_sensitive', False)
        
        if price_sensitive and price > 2000:
            base_rating -= 1.0
        elif price_sensitive and price > 1000:
            base_rating -= 0.5
        
        # Interest alignment
        interests = user_persona.get('interests', [])
        category = product_details.get('category', 'general')
        if category.lower() in [i.lower() for i in interests]:
            base_rating += 0.5
        
        # Spicy preference
        likes_spicy = user_persona.get('preferences', {}).get('likes_spicy', False)
        if likes_spicy and 'spicy' in product_details.get('description', '').lower():
            base_rating += 0.5
        
        return base_rating
    
    def train_model(self, training_data):
        """Train RandomForest model on existing ratings"""
        X = []
        y = []
        
        for item in training_data:
            features = self.extract_features(item['user'], item['product'])
            X.append(features.flatten())
            y.append(item['actual_rating'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save model
        with open(f"{self.model_path}/rating_model.pkl", 'wb') as f:
            pickle.dump(self.model, f)
        with open(f"{self.model_path}/scaler.pkl", 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"✓ Model trained on {len(y)} samples")
        return self.model
    
    def load_model(self):
        """Load pre-trained model"""
        try:
            with open(f"{self.model_path}/rating_model.pkl", 'rb') as f:
                self.model = pickle.load(f)
            with open(f"{self.model_path}/scaler.pkl", 'rb') as f:
                self.scaler = pickle.load(f)
            print("✓ Rating model loaded")
            return True
        except:
            print("⚠ No saved model found - using rule-based")
            return False

# Test
if __name__ == "__main__":
    predictor = RatingPredictor()
    
    # Test prediction
    user = {"age": 22, "preferences": {"price_sensitive": True, "likes_spicy": True}, "interests": ["food"]}
    product = {"name": "Jollof Rice", "category": "food", "price": 2500, "description": "spicy Nigerian rice"}
    
    rating = predictor.predict_rating(user, product)
    print(f"Predicted rating: {rating}/5")