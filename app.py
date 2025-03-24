import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import io
import base64
import time
import os
from datetime import datetime
from camera_input_live import camera_input_live

from src.utils import encode_image_to_base64, validate_image
from src.gemini_handler import HandwritingAnalyzer
from src.qr_generator import generate_qr_code
from config import (
    STREAMLIT_TITLE, 
    MAX_IMAGE_SIZE, 
    SUPPORTED_FORMATS, 
    PERSONALITY_TRAITS,
    TRAIT_DESCRIPTIONS,
    HANDWRITING_FEATURES
)

# Initialize the analyzer
analyzer = HandwritingAnalyzer()

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_TITLE,
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimal design
st.markdown("""
<style>
    /* Base styles */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #fff;
    }
    
    /* Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-align: center;
        color: #2c3e50;
        padding: 0.5rem 0;
        letter-spacing: -0.5px;
    }
    
    /* Tagline */
    .tagline {
        font-size: 1.2rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 2rem;
        color: #555;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Steps */
    .step-number {
        background-color: #4e89ae;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Results section */
    .result-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .profession-title {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .profession-name {
        font-size: 2rem;
        font-weight: 800;
        color: #4e89ae;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* QR Code */
    .qr-container {
        text-align: center;
        margin: 2rem auto;
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        max-width: 280px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .scan-instruction {
        font-size: 1.1rem;
        margin-bottom: 1rem;
        color: #333;
        font-weight: 500;
    }
    
    /* Camera/Upload section */
    .input-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #eee;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .tagline {
            font-size: 1rem;
        }
        .step-number {
            width: 40px;
            height: 40px;
            font-size: 1rem;
        }
        .profession-name {
            font-size: 1.8rem;
        }
    }
    
    /* Hiding unnecessary elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styles */
    .stButton button {
        background-color: #4e89ae;
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        font-size: 1rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Card styles */
    .feature-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 3px solid #4e89ae;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #4e89ae;
    }
    
    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #f0f2f6;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4e89ae !important;
        color: white !important;
    }
    
    /* Expander styling */
    .stExpander {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Camera button styling */
    .camera-button {
        display: inline-block;
        background-color: #4e89ae;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 500;
        margin: 15px auto;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .camera-button:hover {
        background-color: #3d7a9a;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .camera-icon {
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Session state to track current state
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
    
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
    
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
    
if "camera_on" not in st.session_state:
    st.session_state.camera_on = False

# Function to toggle camera state
def toggle_camera():
    st.session_state.camera_on = not st.session_state.camera_on

# Function to handle image analysis
def analyze_handwriting_image(image_data):
    with st.spinner("Analyzing handwriting..."):
        # Create a progress bar to simulate analysis
        progress_bar = st.progress(0)
        for i in range(101):
            time.sleep(0.02)  # Simulate processing time
            progress_bar.progress(i)
        
        # Encode image to base64
        base64_image = encode_image_to_base64(image_data)
        
        # Send the image for analysis
        try:
            analysis_result = analyzer.analyze_handwriting(base64_image)
            st.session_state.analysis_result = analysis_result
            
            # Remove the progress bar
            progress_bar.empty()
            return True
            
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            return False

# App header
st.markdown("<h1 class='main-header'>AI Handwriting Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>Uncover personality insights hidden in your handwriting</p>", unsafe_allow_html=True)

# Main content - Two columns layout
left_col, right_col = st.columns([3, 2])

with left_col:
    # Simple steps
    st.subheader("How It Works")
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("""
        <div style="text-align: center;">
            <div class="step-number">1</div>
            <div style="font-weight: 500;">Capture</div>
            <div style="font-size: 0.9rem; color: #666;">Take a photo of your handwriting</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("""
        <div style="text-align: center;">
            <div class="step-number">2</div>
            <div style="font-weight: 500;">Analyze</div>
            <div style="font-size: 0.9rem; color: #666;">Our AI examines writing patterns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown("""
        <div style="text-align: center;">
            <div class="step-number">3</div>
            <div style="font-weight: 500;">Discover</div>
            <div style="font-size: 0.9rem; color: #666;">Get your personality insights</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Image input section
    st.subheader("Capture Your Handwriting")
    
    # Create tabs for capturing or uploading image
    image_tab1, image_tab2 = st.tabs(["📷 Take a Photo", "📁 Upload Image"])
    
    with image_tab1:
        st.markdown("<div class='input-section'>", unsafe_allow_html=True)
        st.markdown("""
        <p style="margin-bottom: 1rem; text-align: center;">
            <strong>For best results:</strong> Write 3-4 lines on unlined paper with good lighting
        </p>
        """, unsafe_allow_html=True)
        
        # Camera button instead of automatic camera
        if not st.session_state.camera_on:
            st.markdown("""
            <div style="text-align: center; margin: 20px 0;">
                <div class="camera-button" onclick="document.getElementById('camera-button').click()">
                    <span class="camera-icon">📷</span> Take a Photo of Your Handwriting
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden button to handle the click
            if st.button("Camera", key="camera-button", help="Turn on camera"):
                st.session_state.camera_on = True
                st.experimental_rerun()
        else:
            # Camera input only shown when button is clicked
            img_file_buffer = camera_input_live()
            
            if img_file_buffer is not None:
                # Save the captured image
                bytes_data = img_file_buffer.getvalue()
                st.session_state.captured_image = bytes_data
                st.session_state.uploaded_file = None
                st.session_state.camera_on = False  # Turn off camera after taking photo
                
                # Display the captured image
                image = Image.open(io.BytesIO(bytes_data))
                st.image(image, caption="Captured Handwriting Sample", use_container_width=True)
                
                # Auto-analyze
                analyze_handwriting_image(io.BytesIO(bytes_data))
            
            # Button to cancel camera
            if st.button("Cancel", key="cancel-camera"):
                st.session_state.camera_on = False
                st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with image_tab2:
        st.markdown("<div class='input-section'>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose an image...", type=SUPPORTED_FORMATS)
        
        st.markdown("""
        <p style="text-align: center;"><strong>For best results:</strong></p>
        <ul style="margin-left: 2rem;">
            <li>Write at least 3-4 lines of text</li>
            <li>Use your natural handwriting style</li>
            <li>Ensure good lighting</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Save the uploaded file
            st.session_state.uploaded_file = uploaded_file
            st.session_state.captured_image = None
            
            # Validate the image
            is_valid, error_message = validate_image(uploaded_file, SUPPORTED_FORMATS, MAX_IMAGE_SIZE)
            
            if not is_valid:
                st.error(error_message)
            else:
                # Display the image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Handwriting Sample", use_container_width=True)
                
                # Auto-analyze
                uploaded_file.seek(0)
                analyze_handwriting_image(uploaded_file)

with right_col:
    # Always show QR code (booth mode always enabled)
    st.subheader("Try on Your Phone")
    
    # Get the URL of the current app
    try:
        # For deployed app
        app_url = st.query_params.get("url", ["http://localhost:8501"])[0]
    except:
        try:
            # Alternative method for older Streamlit versions
            app_url = st.experimental_get_query_params().get("url", ["http://localhost:8501"])[0]
        except:
            # Fallback to default
            app_url = "http://localhost:8501"
    
    # Create a QR code
    qr_base64 = generate_qr_code(app_url)
    
    # Display the QR code
    st.markdown(f"""
    <div class="qr-container">
        <p class="scan-instruction">Scan to analyze on your phone:</p>
        <img src="data:image/png;base64,{qr_base64}" width="200">
        <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #666;">
            Take a photo of your handwriting directly from your mobile device
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("""
    <div style="margin-top: 1rem;">
        <h4>Instructions:</h4>
        <ol style="margin-left: 1.5rem;">
            <li>Scan the QR code with your phone</li>
            <li>Write something on paper (3-4 lines)</li>
            <li>Click "Take a Photo" and capture your handwriting</li>
            <li>Get your personalized analysis instantly!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Display results if analysis was performed
if st.session_state.analysis_result is not None:
    analysis_result = st.session_state.analysis_result
    
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    st.success("Analysis complete!")
    
    # Profession prediction headline
    if "profession" in analysis_result and "primary" in analysis_result["profession"]:
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0 2rem 0;">
            <div class="profession-title">Your handwriting suggests you'd make an excellent:</div>
            <div class="profession-name">{analysis_result['profession']['primary']}</div>
            <p style="font-style: italic; color: #555; max-width: 600px; margin: 0 auto; text-align: center;">
                {analysis_result['profession']['explanation']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for the detailed results
    tab1, tab2 = st.tabs(["Personality Traits", "Handwriting Features"])
    
    # Tab 1: Personality Traits with radar chart
    with tab1:
        # Create a radar chart for personality traits
        trait_names = []
        trait_scores = []
        
        for trait in PERSONALITY_TRAITS:
            trait_key = trait.lower()
            if trait_key in analysis_result["traits"]:
                trait_data = analysis_result["traits"][trait_key]
                trait_names.append(trait)
                # Convert score to int if it's a string
                if isinstance(trait_data["score"], str):
                    try:
                        score = int(trait_data["score"])
                    except ValueError:
                        score = float(trait_data["score"])
                else:
                    score = trait_data["score"]
                trait_scores.append(score)
        
        # Add the first trait again to close the radar chart
        if trait_names:  # Check if we have any trait names
            trait_names.append(trait_names[0])
            trait_scores.append(trait_scores[0])
        
        # Create the radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=trait_scores,
            theta=trait_names,
            fill='toself',
            name='Personality Profile',
            line_color='#4e89ae',
            fillcolor='rgba(78, 137, 174, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=False,
            height=350,
            margin=dict(l=50, r=50, t=30, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Personality profile summary
        st.markdown("<h4>Your Personality Profile</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 1rem; padding: 1rem; background-color: #f5f7f9; border-radius: 8px; border-left: 3px solid #4e89ae;'>{analysis_result['profile']}</p>", unsafe_allow_html=True)
        
        # Display trait scores with progress bars
        for trait in PERSONALITY_TRAITS:
            trait_key = trait.lower()
            if trait_key in analysis_result["traits"]:
                trait_data = analysis_result["traits"][trait_key]
                
                # Convert score to int if it's a string
                if isinstance(trait_data["score"], str):
                    try:
                        score = int(trait_data["score"])
                    except ValueError:
                        score = float(trait_data["score"])
                else:
                    score = trait_data["score"]
                
                st.markdown(f"**{trait}**: {score}/10")
                st.progress(score / 10)
                st.markdown(f"<p style='font-size: 0.9rem; color: #666;'>{trait_data['evidence']}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    # Tab 2: Handwriting Features
    with tab2:
        # Use a grid layout for features
        col1, col2 = st.columns(2)
        
        # Split features between columns
        features = list(HANDWRITING_FEATURES.items())
        half = len(features) // 2
        
        for i, (feature, feature_info) in enumerate(features):
            feature_key = feature.lower()
            if feature_key in analysis_result["features"]:
                feature_data = analysis_result["features"][feature_key]
                
                # Add to first or second column based on index
                with col1 if i < half else col2:
                    st.markdown(f"""
                    <div class='feature-card'>
                        <strong>{feature}:</strong> {feature_data['value']}
                        <p style='font-size: 0.9rem; color: #666;'>{feature_data['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Sharing section
    st.markdown("""
    <div style="margin-top: 2rem; text-align: center;">
        <h4>📱 Take a screenshot to share your results!</h4>
        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">
            Share your personality profile with friends or on social media with #AIHandwritingAnalyzer
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown(f"<p style='font-style: italic; font-size: 0.8rem; color: #999; text-align: center; margin-top: 2rem;'>{analysis_result['disclaimer']}</p>", unsafe_allow_html=True)
    
    # Reset button for trying again
    if st.button("Analyze Another Sample", use_container_width=True):
        st.session_state.analysis_result = None
        st.session_state.captured_image = None
        st.session_state.uploaded_file = None
        st.session_state.camera_on = False
        st.experimental_rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)

# Minimal footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 1rem; font-size: 0.8rem; color: #999;">
    © 2025 AI Handwriting Analyzer | For educational and entertainment purposes
</div>
""", unsafe_allow_html=True)