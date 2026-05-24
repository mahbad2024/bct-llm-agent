# train_model.py - Train rating predictor with all three datasets
from rating_predictor import RatingPredictor
from data_loader_final import DataLoader
import random

print("="*50)
print("Training Rating Predictor Model")
print("="*50)

# Load ALL datasets
print("\n1. Loading datasets...")
loader = DataLoader()
loader.load_amazon_data()
loader.load_yelp_data(limit=20000)
loader.load_goodreads_data(limit=10000)
loader.merge_datasets()
print(f"   Total reviews available: {len(loader.all_reviews)}")

# Prepare training data from all reviews
print("\n2. Preparing training data...")
training_data = []

for review in loader.all_reviews[:20000]:
    user_persona = {
        'age': random.randint(18, 45),
        'preferences': {
            'price_sensitive': random.choice([True, False]),
            'likes_spicy': random.choice([True, False])
        },
        'interests': random.sample(['food', 'tech', 'movies', 'shopping', 'books'], 2)
    }
    
    product_details = {
        'name': review.get('product_name', 'Product'),
        'category': review.get('category', 'general'),
        'price': random.randint(500, 10000),
        'description': review.get('review_text', '')[:100]
    }
    
    training_data.append({
        'user': user_persona,
        'product': product_details,
        'actual_rating': review.get('rating', 4)
    })

print(f"   Training samples: {len(training_data)}")

# Train the model
print("\n3. Training RandomForest model...")
predictor = RatingPredictor()
predictor.train_model(training_data)
print("   ✓ Model training complete!")

# Test the model
print("\n4. Testing model on sample...")
test_user = {
    'age': 22,
    'preferences': {'price_sensitive': True, 'likes_spicy': True},
    'interests': ['food', 'books']
}
test_product = {
    'name': 'Jollof Rice',
    'category': 'food',
    'price': 2500,
    'description': 'Spicy Nigerian rice'
}

predicted = predictor.predict_rating(test_user, test_product)
print(f"   Test prediction: {predicted}/5 stars")

print("\n✅ Model training complete with all three datasets!")