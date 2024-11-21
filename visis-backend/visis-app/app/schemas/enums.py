# app/schemas/enums.py

# from enum import Enum

# class SupportedLanguages(str, Enum):
#     en = 'en'
#     es = 'es'
#     fr = 'fr'
#     de = 'de'
#     it = 'it'
#     pt = 'pt'


from enum import Enum

class SupportedLanguages(str, Enum):
    English = "English"
    Spanish = "Spanish"
    German = "German"
    Italian = "Italian"
    French = "French"
    Portuguese = "Portuguese"

class HighlightColor(str, Enum):
    yellow = "yellow"
    blue = "blue"
    red = "red"
    green = "green"
    orange = "orange"
    purple = "purple"
    pink = "pink"

class FontSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

class ReadingMode(str, Enum):
    light = "light"
    dark = "dark"