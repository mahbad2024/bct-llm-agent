# create_goodreads.py - Create valid Goodreads JSON data
import json

# Create 1000 realistic book reviews
reviews = []
book_titles = [
    "The Nigerian Dream", "Lagos Noir", "A History of Nigeria", "Modern African Poetry",
    "Things Fall Apart", "Half of a Yellow Sun", "Americanah", "The Fishermen",
    "Stay With Me", "The Secret Lives of Baba Segi's Wives"
]

users = [f"user_{i}" for i in range(1, 101)]

for i in range(1000):
    review = {
        "user_id": users[i % len(users)],
        "rating": (i % 5) + 1,
        "review_text": f"This book is {'amazing' if i % 3 == 0 else 'good' if i % 2 == 0 else 'okay'}. {'I highly recommend it!' if i % 4 == 0 else 'Worth reading.'}",
        "title": book_titles[i % len(book_titles)]
    }
    reviews.append(json.dumps(review))

# Save to file
with open("data/goodreads_reviews.json", "w") as f:
    f.write("\n".join(reviews))

print(f"✓ Created {len(reviews)} Goodreads reviews")