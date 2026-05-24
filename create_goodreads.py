# create_goodreads.py - Create 10,000 Goodreads reviews with RICH Nigerian Pidgin
import json
import random

book_titles = [
    "The Nigerian Dream", "Lagos Noir", "A History of Nigeria", "Things Fall Apart",
    "Half of a Yellow Sun", "Americanah", "The Fishermen", "Stay With Me",
    "The Secret Lives of Baba Segi's Wives", "My Sister the Serial Killer",
    "The Girl with the Louding Voice", "Everyday Is for the Thief",
    "The Son of the House", "Butter Honey Pig Bread"
]

# Expanded Nigerian Pidgin phrases
positive_phrases = [
    "Omo! This book dey sweet well well",
    "E soft like chicken, I love am!",
    "God bless the writer for this one",
    "This one na banger, I swear",
    "The thing just dey hit different",
    "I no fit put this book down abeg",
    "Na masterpiece, God when?",
    "This book scatter my brain (in a good way)",
    "The writer na proper storyteller",
    "I go recommend this book to everybody",
    "This book choke! Full of wisdom",
    "Oya go buy am, you go thank me later",
    "The way this book dey sweet me no be small",
    "My money no waste for this one at all",
    "This book be like pure water - refreshing!"
]

negative_phrases = [
    "This one no be am at all abeg",
    "The thing just scatter, no sense",
    "My money just waste for this book",
    "Abeg, who sell this one? Very disappointing",
    "I no like this book at all, e get as e be",
    "The writer suppose try harder",
    "This book na wahala, waste of time",
    "I regret buying this one, no cap",
    "The story just dey drag too much",
    "Na so so yarning, no substance"
]

neutral_phrases = [
    "E get as e be, not bad not amazing",
    "But make I talk true, e could be better",
    "No wahala, e was okay",
    "I don read better books but this one is fine",
    "Middle of the road, nothing special",
    "The book tries but no reach there"
]

location_refs = ["Lagos", "Abuja", "Port Harcourt", "Ibadan", "Benin", "Kano", "Enugu"]
persona_refs = ["student", "working class", "corper", "business owner", "stay at home mom", "tech bro"]

reviews = []
for i in range(10000):
    book = book_titles[i % len(book_titles)]
    rating = random.choice([1, 2, 3, 4, 5])
    
    # Choose phrase based on rating
    if rating >= 4:
        phrase = random.choice(positive_phrases)
    elif rating <= 2:
        phrase = random.choice(negative_phrases)
    else:
        phrase = random.choice(neutral_phrases)
    
    location = random.choice(location_refs)
    persona = random.choice(persona_refs)
    
    review_text = f"{phrase}. I be {persona} from {location}. "
    
    if rating >= 4:
        review_text += f"'{book}' na 5 star for me. If you like good story, go for am!"
    elif rating <= 2:
        review_text += f"Honestly, '{book}' no reach standard. Make they refund my money abeg."
    else:
        review_text += f"'{book}' is okay. But make dem try improve."
    
    # Add extra cultural flavor
    extra_flavors = [
        "Na so I see am o.", "You get?", "No cap.", "E be like that sha.",
        "I swear down.", "God forgive me.", "Chai!", "Ehen!",
        "But who am I to judge?", "Walahi!", "Alhamdulillah for small thing."
    ]
    if random.random() > 0.7:
        review_text += f" {random.choice(extra_flavors)}"
    
    review = {
        "user_id": f"user_{i % 500}",
        "rating": rating,
        "review_text": review_text,
        "title": book
    }
    reviews.append(json.dumps(review))

with open("data/goodreads_reviews.json", "w") as f:
    f.write("\n".join(reviews))

print(f"✓ Created {len(reviews)} Goodreads reviews with RICH Nigerian Pidgin!")
print(f"  - Positive phrases: {len(positive_phrases)}")
print(f"  - Negative phrases: {len(negative_phrases)}")
print(f"  - Locations: {location_refs}")
print(f"  - Personas: {persona_refs}")