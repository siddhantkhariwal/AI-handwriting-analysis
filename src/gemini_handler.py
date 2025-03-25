import os
import base64
import json
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HandwritingAnalyzer:
    def __init__(self):
        """Initialize the Google Gemini API client"""
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        # Updated to use the recommended model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_handwriting(self, image_base64):
        """
        Send an image to Google Gemini and get personality traits analysis
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            dict: Parsed analysis results
        """
        system_prompt = """
            You are an expert handwriting analyst with deep knowledge of graphology. Analyze ONLY the physical characteristics and patterns of the handwriting in the provided image. IGNORE the actual content or meaning of what is written.

            Focus exclusively on these handwriting features:
            - Size (small, medium, large)
            - Slant (right, left, vertical)
            - Pressure (heavy, medium, light)
            - Spacing between letters and words (wide, normal, narrow)
            - Baseline (straight, ascending, descending, wavy)
            - Margins (wide, normal, narrow)
            - Letter formation (rounded, angular, connected, disconnected)
            - Zone emphasis (upper, middle, lower)
            - Overall rhythm and regularity

            Based ONLY on these graphological features (NOT the content), provide:

            1. Key handwriting features:
            - Size (small, medium, large)
            - Slant (right, left, vertical)
            - Pressure (heavy, medium, light)
            - Spacing (wide, normal, narrow)
            - Baseline (straight, ascending, descending, wavy)
            - Margins (wide, normal, narrow)
            
            2. Personality traits on a scale of 1-10:
            - Openness
            - Conscientiousness
            - Extraversion
            - Agreeableness
            - Emotional Stability

            3. Brief personality profile based on the handwriting style (2-3 sentences)

            4. Career/profession prediction: Based ONLY on the handwriting characteristics and NOT the content, suggest 1-3 professions that would suit this handwriting style.

            Format your response as a JSON object with the following structure:
            ```json
            {
            "features": {
                "size": {"value": "medium", "description": "explanation..."},
                "slant": {"value": "right", "description": "explanation..."},
                "pressure": {"value": "medium", "description": "explanation..."},
                "spacing": {"value": "normal", "description": "explanation..."},
                "baseline": {"value": "straight", "description": "explanation..."},
                "margins": {"value": "normal", "description": "explanation..."}
            },
            "traits": {
                "openness": {"score": 7, "evidence": "explanation..."},
                "conscientiousness": {"score": 6, "evidence": "explanation..."},
                "extraversion": {"score": 8, "evidence": "explanation..."},
                "agreeableness": {"score": 7, "evidence": "explanation..."},
                "emotional_stability": {"score": 6, "evidence": "explanation..."}
            },
            "profile": "Personality profile description here...",
            "profession": {
                "primary": "Primary profession prediction",
                "explanation": "Brief explanation of why this profession matches the handwriting style"
            },
            "disclaimer": "This analysis is based on graphology principles and should be considered for entertainment purposes."
            }
        ```
        
        Respond ONLY with the JSON object, no additional text.
        """
        
        try:
            print(f"Attempting to connect to Google Gemini API")
            
            # Convert base64 to image
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # Create the API request
            response = self.model.generate_content([
                system_prompt,
                "Analyze this handwriting sample and provide the information in the requested JSON format.",
                image
            ])
            
            # Extract the JSON response
            print("API call successful, extracting response")
            response_text = response.text
            
            # Clean the response if it contains markdown backticks or "json" declaration
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(response_text)
            
        except Exception as e:
            import traceback
            print(f"Error during API call: {str(e)}")
            print(f"Detailed error: {traceback.format_exc()}")
            return {
                "error": str(e),
                "features": {},
                "traits": {},
                "profile": "Unable to analyze the handwriting. Please try again with a clearer image."
            }