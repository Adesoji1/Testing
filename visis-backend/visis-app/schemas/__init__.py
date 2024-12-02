#app/schemas/__init__.py
from .user import UserBase, UserCreate, UserResponse
from .document import DocumentBase, DocumentCreate, DocumentResponse
from .audiobook import AudioBookBase, AudioBookCreate, AudioBookResponse
from .user_preference import UserPreferenceBase, UserPreferenceCreate, UserPreferenceResponse
from .user_bookmark import UserBookmarkBase, UserBookmarkCreate, UserBookmarkResponse
from .scanning_history import ScanningHistoryBase, ScanningHistoryCreate, ScanningHistoryResponse
from .accessibility import AccessibilityBase, AccessibilityCreate, AccessibilityResponse
from .language import LanguageBase, LanguageCreate, LanguageResponse
from .document_language import DocumentLanguageBase, DocumentLanguageCreate, DocumentLanguageResponse
from .audiobook_language import AudioBookLanguageBase, AudioBookLanguageCreate, AudioBookLanguageResponse
from .user_activity import UserActivityBase, UserActivityCreate, UserActivityResponse
from .feedback import FeedbackBase, FeedbackCreate, FeedbackResponse
from .app_setting import AppSettingBase, AppSettingCreate, AppSettingResponse
from .enums import PlaybackSpeed, AudioFormat, FontSize, HighlightColor, ReadingMode, ContentVisibility, SupportedLanguages
