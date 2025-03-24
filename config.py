import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# App configuration
STREAMLIT_TITLE = "AI Handwriting Analyzer"
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
SUPPORTED_FORMATS = ["jpg", "jpeg", "png"]

# Handwriting analysis parameters
PERSONALITY_TRAITS = [
    "Openness",
    "Conscientiousness",
    "Extraversion",
    "Agreeableness",
    "Emotional Stability"
]

# Common professions for recommendations (for reference)
COMMON_PROFESSIONS = [
    "CEO",
    "Entrepreneur",
    "Creative Director",
    "Psychologist",
    "Researcher",
    "Engineer",
    "Artist",
    "Writer",
    "Teacher",
    "Manager",
    "Consultant",
    "Scientist",
    "Physician",
    "Designer",
    "Attorney"
]

# Descriptions of what each trait means
TRAIT_DESCRIPTIONS = {
    "Openness": "Openness reflects curiosity, creativity, and preference for variety and novelty.",
    "Conscientiousness": "Conscientiousness indicates organization, discipline, responsibility, and achievement-orientation.",
    "Extraversion": "Extraversion relates to sociability, assertiveness, talkativeness, and excitement-seeking.",
    "Agreeableness": "Agreeableness encompasses kindness, cooperation, warmth, and consideration for others.",
    "Emotional Stability": "Emotional Stability reflects calm, composure, and resilience in the face of stress or challenges."
}

# Handwriting features and their descriptions
HANDWRITING_FEATURES = {
    "Size": "The overall size of letters",
    "Slant": "The angle or tilt of the letters",
    "Pressure": "The darkness and thickness of the strokes",
    "Spacing": "The distance between letters and words",
    "Baseline": "How the text aligns horizontally",
    "Margins": "The space left at the edges of the page"
}