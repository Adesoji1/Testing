# scripts/populate_languages.py

from app.database import SessionLocal
from app.models.language import Language

def populate_languages():
    db = SessionLocal()
    languages = [
        {"name": "English", "code": "en"},
        {"name": "Spanish", "code": "es"},
        {"name": "French", "code": "fr"},
        {"name": "German", "code": "de"},
        {"name": "Italian", "code": "it"},
        {"name": "Portuguese", "code": "pt"},
        {"name": "Russian", "code": "ru"},
        {"name": "Japanese", "code": "ja"},
        {"name": "Korean", "code": "ko"},
        # Add other languages as needed
    ]
    for lang in languages:
        existing_lang = db.query(Language).filter(Language.code == lang["code"]).first()
        if not existing_lang:
            db_language = Language(name=lang["name"], code=lang["code"])
            db.add(db_language)
    db.commit()
    db.close()

if __name__ == "__main__":
    populate_languages()
