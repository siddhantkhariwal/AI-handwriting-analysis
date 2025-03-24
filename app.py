import streamlit as st
import pandas as pd
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

# Detect if we're on a mobile device (very simple check)
def is_mobile():
    try:
        # This is a very basic check that works for most devices
        user_agent = st.experimental_get_query_params().get("user_agent", [""])[0].lower()
        mobile_strings = ['mobile', 'android', 'iphone', 'ipad', 'ipod']
        return any(m in user_agent for m in mobile_strings)
    except:
        # Fallback to check screen width via JS (not perfect but helps)
        return False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-align: center;
        background: linear-gradient(90deg, #4e89ae, #43658b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
        letter-spacing: -0.5px;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .tagline {
            font-size: 1rem !important;
        }
    }
    
    .tagline {
        font-size: 1.3rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 2rem;
        color: #555;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .step-number {
        background-color: #4e89ae;
        color: white;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem auto;
        font-weight: bold;
        font-size: 1.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        position: relative;
        z-index: 5;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translate3d(0, 20px, 0);
        }
        to {
            opacity: 1;
            transform: none;
        }
    }
    
    .step-animate {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .delay-1 {
        animation-delay: 0.2s;
        animation-fill-mode: backwards;
    }
    
    .delay-2 {
        animation-delay: 0.4s;
        animation-fill-mode: backwards;
    }
    
    .profession-title {
        animation: fadeInUp 0.8s ease-out;
    }
    
    .profession-name {
        animation: fadeInUp 1s ease-out 0.3s;
        animation-fill-mode: backwards;
    }
    
    .profession-explanation {
        animation: fadeInUp 1s ease-out 0.6s;
        animation-fill-mode: backwards;
    }
    
    .sub-header {
        font-size: 1.6rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #2c3e50;
        border-bottom: 2px solid #eee;
        padding-bottom: 0.5rem;
    }
    
    .feature-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4e89ae;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .trait-value {
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .explanation {
        font-size: 0.9rem;
        color: #6c757d;
        line-height: 1.5;
    }
    
    .disclaimer {
        font-style: italic;
        color: #6c757d;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    .stProgress > div > div > div > div {
        background-color: #4e89ae;
    }
    
    .upload-section {
        background-color: #f8f9fa;
        padding: 2.5rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        border: 2px dashed #ccc;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #4e89ae;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .upload-icon {
        font-size: 3.5rem;
        color: #4e89ae;
        margin-bottom: 1.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }
    
    .info-section {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 2rem;
        border: 1px solid #eee;
    }
    
    .trait-container {
        margin-bottom: 0.5rem;
    }
    
    .trait-name {
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    
    .about-traits-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .trait-card {
        flex: 1 0 30%;
        min-width: 250px;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-top: 3px solid #4e89ae;
    }
    
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
    }
    
    .stButton button {
        background: linear-gradient(90deg, #4e89ae, #43658b);
        color: white;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(78, 137, 174, 0.3);
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, #43658b, #3d5a7d);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(78, 137, 174, 0.4);
    }
    
    footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #eee;
        text-align: center;
    }
    
    .connection-line {
        position: relative;
        height: 20px;
        margin-top: -50px;
        margin-bottom: 30px;
        z-index: 1;
    }
    
    .connection-line:before {
        content: "";
        position: absolute;
        top: 10px;
        left: 25%;
        right: 25%;
        height: 3px;
        background: linear-gradient(90deg, transparent, #4e89ae 20%, #4e89ae 80%, transparent);
    }
    
    .qr-container {
        text-align: center;
        margin: 2rem auto;
        padding: 1.5rem;
        background-color: white;
        border-radius: 10px;
        max-width: 300px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .scan-instruction {
        font-size: 1.2rem;
        margin-bottom: 1rem;
        color: #333;
        font-weight: 500;
    }
    
    .booth-mode {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #eee;
    }
    
    .sharing-container {
        background-color: #f0f7ff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        border-left: 4px solid #4e89ae;
    }
    
    .camera-container {
        margin: 2rem auto;
        text-align: center;
    }
    
    [data-testid="column"] {
        padding: 0 !important;
    }
    
    @media (max-width: 768px) {
        .step-number {
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
            margin-bottom: 1rem;
        }
        .connection-line:before {
            left: 15%;
            right: 15%;
        }
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

if "is_booth_mode" not in st.session_state:
    st.session_state.is_booth_mode = False

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
st.markdown("<div style='padding: 1.5rem 0 2rem 0;'>", unsafe_allow_html=True)
st.markdown("<h1 class='main-header'>✍️ AI Handwriting Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>Uncover the hidden insights in your handwriting with AI-powered personality analysis</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Booth Mode toggle (for event organizers)
with st.expander("🎪 Event Organizer Options"):
    booth_col1, booth_col2 = st.columns([3, 1])
    with booth_col1:
        st.markdown("""
        **Booth Mode** will show a QR code that attendees can scan to access this app directly on their phones.
        This allows visitors to:
        - Take a photo of their handwriting directly from their phone
        - Receive personalized analysis immediately
        - Engage with your booth without overcrowding
        """)
    with booth_col2:
        st.session_state.is_booth_mode = st.toggle("Activate Booth Mode", st.session_state.is_booth_mode)
        
        if st.session_state.is_booth_mode:
            # Get the app URL from Streamlit
            app_url = st.experimental_get_query_params().get("url", ["http://192.168.1.3:8501/1"])[0]
            st.markdown("**Current URL**")
            st.code(app_url)

# Display QR code in booth mode
if st.session_state.is_booth_mode:
    st.markdown("<div class='booth-mode'>", unsafe_allow_html=True)
    st.subheader("📱 Scan to analyze your handwriting")
    
    # Get the URL of the current app
    app_url = st.experimental_get_query_params().get("url", ["http://192.168.1.3:8501/"])[0]
    
    # Create a QR code
    qr_base64 = generate_qr_code(app_url)
    
    # Display the QR code
    st.markdown(f"""
    <div class="qr-container">
        <p class="scan-instruction">Scan this QR code to try it on your phone!</p>
        <img src="data:image/png;base64,{qr_base64}" width="250">
        <p style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
            Take a photo of your handwriting and receive instant personality insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <h3>Instructions for Visitors:</h3>
        <ol style="display: inline-block; text-align: left;">
            <li>Scan the QR code with your phone</li>
            <li>Write something on paper (at least 3-4 lines)</li>
            <li>Take a photo of your handwriting</li>
            <li>Click "Reveal My Personality Traits"</li>
            <li>Get your personalized handwriting analysis!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main content
container = st.container()
with container:
    # How it works section with steps using Streamlit columns
    st.markdown("<h2 class='sub-header'>How It Works</h2>", unsafe_allow_html=True)
    
    # Create three columns for the steps
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center;" class="step-animate">
            <div class="step-number">1</div>
            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">Upload</div>
            <div style="font-size: 0.9rem; color: #666;">Share a clear image of your handwriting</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;" class="step-animate delay-1">
            <div class="step-number">2</div>
            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">Analyze</div>
            <div style="font-size: 0.9rem; color: #666;">Our AI examines handwriting features</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center;" class="step-animate delay-2">
            <div class="step-number">3</div>
            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">Discover</div>
            <div style="font-size: 0.9rem; color: #666;">Reveal personality & career insights</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add connecting lines between the steps
    st.markdown("""
    <div class="connection-line"></div>
    """, unsafe_allow_html=True)
    
    # Image input section
    st.markdown("<h2 class='sub-header'>Capture Your Handwriting</h2>", unsafe_allow_html=True)
    
    # Create tabs for uploading or capturing image
    image_tab1, image_tab2 = st.tabs(["📷 Take a Photo", "📁 Upload Image"])
    
    with image_tab1:
        st.markdown("<div class='camera-container'>", unsafe_allow_html=True)
        st.markdown("""
        <p style="margin-bottom: 1rem;">
            <strong>For best results:</strong> Write 3-4 lines on unlined paper with good lighting
        </p>
        """, unsafe_allow_html=True)
        
        # Camera input component
        img_file_buffer = camera_input_live()
        
        if img_file_buffer is not None:
            # Save the captured image
            bytes_data = img_file_buffer.getvalue()
            st.session_state.captured_image = bytes_data
            st.session_state.uploaded_file = None
            
            # Display the captured image
            image = Image.open(io.BytesIO(bytes_data))
            st.image(image, caption="Captured Handwriting Sample", use_container_width=True)
            
            # Analyze button
            if st.button("✨ Reveal My Personality Traits", key="camera_analyze", use_container_width=True):
                analyze_handwriting_image(io.BytesIO(bytes_data))
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with image_tab2:
        st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
        st.markdown("<div class='upload-icon'>📄</div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose an image...", type=SUPPORTED_FORMATS)
        
        st.markdown("""
        <p><strong>For best results:</strong></p>
        <ul>
            <li>Write at least 3-4 lines of text on unlined paper</li>
            <li>Use your natural handwriting style</li>
            <li>Ensure the image is clear and well-lit</li>
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
                
                # Analysis button
                if st.button("✨ Reveal My Personality Traits", key="upload_analyze", use_container_width=True):
                    # Reset the file position to the beginning
                    uploaded_file.seek(0)
                    analyze_handwriting_image(uploaded_file)

    # Display results if analysis was performed
    if st.session_state.analysis_result is not None:
        analysis_result = st.session_state.analysis_result
        
        st.markdown("<h2 class='sub-header'>Your Analysis Results</h2>", unsafe_allow_html=True)
        st.success("Analysis complete! Here are your results:")
        
        # Profession prediction headline
        if "profession" in analysis_result and "primary" in analysis_result["profession"]:
            st.markdown(f"""
            <div style="text-align: center; margin: 2rem 0;">
                <h2 class="profession-title" style="font-size: 1.8rem; color: #2c3e50; margin-bottom: 0.5rem;">
                    Your handwriting suggests you'd make an excellent:
                </h2>
                <h1 class="profession-name" style="font-size: 2.5rem; font-weight: 800; color: #4e89ae; margin-bottom: 1rem;">
                    {analysis_result['profession']['primary']}
                </h1>
                <p class="profession-explanation" style="font-style: italic; color: #555; max-width: 700px; margin: 0 auto;">
                    {analysis_result['profession']['explanation']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Summary section with personality profile
        st.markdown("<h3 class='sub-header'>Your Personality Profile</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 1.1rem; padding: 1rem; background-color: #f5f7f9; border-radius: 10px; border-left: 4px solid #4e89ae;'>{analysis_result['profile']}</p>", unsafe_allow_html=True)
        
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
                    trait_scores.append(trait_data["score"])
            
            # Add the first trait again to close the radar chart
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
                height=400,
                margin=dict(l=80, r=80, t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display trait scores with progress bars
            for trait in PERSONALITY_TRAITS:
                trait_key = trait.lower()
                if trait_key in analysis_result["traits"]:
                    trait_data = analysis_result["traits"][trait_key]
                    
                    st.markdown(f"""
                    <div class='trait-container'>
                        <div class='trait-name'>{trait}: {trait_data['score']}/10</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(trait_data["score"] / 10)
                    st.markdown(f"<p class='explanation'>{trait_data['evidence']}</p>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
        
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
                            <p class='explanation'>{feature_data['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Sharing section
        st.markdown("<div class='sharing-container'>", unsafe_allow_html=True)
        st.subheader("📱 Take a screenshot to share your results!")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.markdown(f"**Analysis completed at:** {timestamp}")
        
        st.markdown("""
        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">
            Tag us with #AIHandwritingAnalyzer to be featured on our social media!
        </p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Disclaimer
        st.markdown(f"<p class='disclaimer'>{analysis_result['disclaimer']}</p>", unsafe_allow_html=True)
        
        # Reset button for trying again
        if st.button("✨ Analyze Another Handwriting Sample", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.captured_image = None
            st.session_state.uploaded_file = None
            st.experimental_rerun()

    # About Handwriting Analysis section (shown only when no analysis is being displayed)
    if st.session_state.analysis_result is None:
        st.markdown("<h2 class='sub-header'>About Handwriting Analysis</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown("""
            **Graphology** is the study of handwriting and how it relates to personality traits and characteristics.

            While not scientifically validated to the same degree as standardized personality assessments, many people find handwriting analysis insightful and entertaining.
            
            **How it works:**
            1. When you write, your brain sends signals to your hand, creating a unique pattern
            2. Handwriting features like size, slant, and pressure reveal aspects of your personality
            3. Our AI analyzes these features using graphology principles to create your personality profile
            
            **Important note:** This analysis is for entertainment purposes only and should not be used for making important decisions.
            """)

        with col2:
            st.image("https://via.placeholder.com/400x300.png?text=Handwriting+Analysis", caption="How handwriting reveals personality traits", use_container_width=True)

        # Trait descriptions
        st.markdown("<h3 class='sub-header'>Understanding the 'Big Five' Personality Traits</h3>", unsafe_allow_html=True)

        st.markdown("<div class='about-traits-container'>", unsafe_allow_html=True)
        for trait, description in TRAIT_DESCRIPTIONS.items():
            st.markdown(f"""
            <div class='trait-card'>
                <h4>{trait}</h4>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("<footer>", unsafe_allow_html=True)
    st.markdown("<p>© 2025 AI Handwriting Analyzer. Created for educational and entertainment purposes.</p>", unsafe_allow_html=True)
    st.markdown("<p class='disclaimer'>Disclaimer: This application is not a substitute for professional assessment. The analysis is based on graphology principles and should be considered for entertainment purposes only.</p>", unsafe_allow_html=True)
    st.markdown("</footer>", unsafe_allow_html=True)