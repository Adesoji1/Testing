# app/schemas/enums.py

from enum import Enum

class PlaybackSpeed(str, Enum):
    x0_5 = "0.5x"
    x0_75 = "0.75x"
    x1_0 = "1x"
    x1_25 = "1.25x"
    x1_5 = "1.5x"
    x2_0 = "2x"
    
class SupportedLanguages(str, Enum):
    English = "English"
    Spanish = "Spanish"
    French = "French"
    German = "German"
    Chinese = "Chinese"
    Japanese = "Japanese"
    Korean = "Korean"

class HighlightColor(str, Enum):
    yellow = "yellow"
    green = "green"
    blue = "blue"
    pink = "pink"
    purple = "purple"

class FontSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"
    x_large = "x-large"

class ReadingMode(str, Enum):
    light = "light"
    dark = "dark"
    sepia = "sepia"


class AudioFormat(str, Enum):
    MP3 = "MP3"
    WAV = "WAV"
    OGG = "OGG"

class ContentVisibility(str, Enum):
    private = "private"
    public = "public"
    shared = "shared"


# app/schemas/enums.py
from enum import Enum

class ActivityType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    VIEW_DOCUMENT = "view_document"
    CREATE_DOCUMENT = "create_document"
    UPDATE_DOCUMENT = "update_document"
    DELETE_DOCUMENT = "delete_document"
    CREATE_BOOKMARK = "create_bookmark"
    UPDATE_BOOKMARK = "update_bookmark"
    DELETE_BOOKMARK = "delete_bookmark"
    UPDATE_PREFERENCES = "update_preferences"