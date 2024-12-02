from app.database import Base 
from .user import User
from .user_preference import UserPreference
from .document import Document
from .audiobook import Audiobook
from .user_bookmark import UserBookmark
from .scanning_history import ScanningHistory
from .accessibility import Accessibility
from .language import Language
from .document_language import DocumentLanguage
from .audiobook_language import AudioBookLanguage
from .user_activity import UserActivity
from .feedback import Feedback
from .app_setting import AppSetting
from .donation import Donation
from .transaction import Transaction
from .subscription import Subscription


# Export all models and Base for use in migrations and elsewhere
__all__ = [
    "Base",
    "User",
    "UserPreference",
    "Document",
    "Audiobook",
    "UserBookmark",
    "ScanningHistory",
    "Accessibility",
    "Language",
    "DocumentLanguage",
    "AudioBookLanguage",
    "UserActivity",
    "Feedback",
    "AppSetting",
     "Donation",
    "Transaction",
    "Subscription",
]
# print("Initializing models: importing AudioBook")