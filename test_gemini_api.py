import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: No Google API key found in .env file")
    exit(1)

print(f"Using API key: {api_key[:4]}...{api_key[-4:]} (truncated for security)")

try:
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Initialize model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Make a simple request
    response = model.generate_content("Hello, this is a test of the Google Gemini API connection. Please respond with a short confirmation.")
    
    print("\nAPI CONNECTION SUCCESSFUL!")
    print("Response from Google Gemini:")
    print(response.text)
    
except Exception as e:
    print("\nAPI CONNECTION FAILED")
    print(f"Error details: {str(e)}")
    
    # More detailed troubleshooting
    print("\nTROUBLESHOOTING TIPS:")
    print("1. Check that your API key is correct")
    print("2. Verify your internet connection")
    print("3. Check if your network blocks API connections")
    print("4. Make sure you've enabled the Gemini API in your Google Cloud Console")
    print("5. Verify that your Google account has billing set up with free credits")