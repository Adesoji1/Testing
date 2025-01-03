# app/utils/lang_utils.py

def map_language_code_to_supported(detected_language: str) -> str:
    """
    Map the detected language to a supported AWS Comprehend language code.
    This ensures compatibility with AWS Comprehend's supported language list.
    """
    supported_languages = {
        "en": "English",  # English
        "es": "Spanish",  # Spanish
        "fr": "French",  # French
        "de": "German",  # German
        "it": "Italian",  # Italian
        "pt": "Portugese",  # Portuguese
        "ar": "Arabic",  # Arabic
        "hi": "Hindi",  # Hindi
        "ja": "Japanese",  # Japanese
        "ko": "Korean",  # Korean
        "zh": "Simplified Chinese",  # Simplified Chinese
        "zh-TW": "Traditional Chinese",  # Traditional Chinese
        "nl" : "Dutch",
    }

    # If the language is unsupported, default to English
    return supported_languages.get(detected_language, "en")


def infer_genre(text: str) -> str:
    """
    Infer genre based on predefined keywords.
    """
    genre_keywords = {
        "Fiction": ["story", "novel", "fiction", "tale", "narrative"],
        "Technology": ["technology", "tech", "software", "hardware", "AI", "robotics","ML","DL","Artificial Intelligence","Machine Learning","Deep Learning"],
        "Science": ["science", "experiment", "research", "physics", "chemistry", "biology"],
        "Health/Medicine": ["health", "medicine", "wellness", "fitness", "medical", "therapy"],
        "History": ["history", "historical", "ancient", "medieval", "war", "biography"],
        "Environment/Nature": ["environment", "nature", "ecology", "climate", "wildlife"],
        "Education": ["education", "teaching", "learning", "training", "academics", "study"],
        "Business/Finance": ["profit", "loss", "business", "finance", "investment", "marketing", "economics","Transforming Business","Digital Transformation","Business Strategy","market research","target audience","insights"],
        "Art/Culture": ["art", "culture", "painting", "sculpture", "music", "theater", "dance", "poetry"],
        "Sports/Games": ["sports", "games", "athletics", "fitness", "competition", "team", "tournament"],
        "Cover/Letter": ["dear hiring team", "hiring manager", "application", "resume", "cv"],
        "Travel/Adventure": ["travel", "adventure", "journey", "destination", "exploration", "trip"],
        "Fantasy": ["fantasy", "magic", "myth", "legend", "wizard", "dragon", "epic"],
        "Mystery/Thriller": ["mystery", "thriller", "detective", "crime", "suspense", "investigation"],
        "Romance": ["romance", "love", "passion", "relationship", "heart", "affection"],
        "Self-Help": ["self-help", "motivation", "personal development", "growth", "success", "habits"],
        "Science Fiction": ["sci-fi", "space", "alien", "future", "technology", "robot"],
        "Horror": ["horror", "scary", "ghost", "monster", "haunted", "fear"],
        "Children": ["children", "kids", "fairy tale", "adventure", "learning", "nursery"],
        "Comedy/Humor": ["comedy", "humor", "funny", "joke", "satire", "parody"],
        "Religion/Spirituality": ["religion", "spirituality", "faith", "belief", "prayer", "philosophy","spiritual","spiritual growth","church", "temple", "mosque"," image and Glory", "Jesus", "Mohammed", "Muhammad"],
        "Politics": ["politics", "government", "policy", "diplomacy", "elections", "law"],
        "Cooking/Food": ["cooking", "food", "recipe", "culinary", "kitchen", "diet", "nutrition"],
        "Travel Guides": ["travel", "destination", "guide", "itinerary", "vacation", "tour"],
    }

    for genre, keywords in genre_keywords.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return genre
    return "Unknown"
