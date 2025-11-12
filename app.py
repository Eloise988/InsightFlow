import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import io

# Set up the page
st.set_page_config(
    page_title="InsightFlow - Maintenance AI",
    page_icon="🔧",
    layout="wide"
)

# Title and description
st.title("🔧 InsightFlow - AI Maintenance Assistant")
st.markdown("Upload equipment photos, describe issues, get AI-powered diagnosis and repair instructions.")

# Sidebar for API key
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")
    if api_key:
        os.environ['GOOGLE_API_KEY'] = api_key
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")

# Main application tabs
tab1, tab2, tab3 = st.tabs(["📷 Image Analysis", "🎤 Audio Notes", "📝 Text Diagnosis"])

with tab1:
    st.header("Image Analysis")
    uploaded_image = st.file_uploader("Upload equipment photo", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_image and api_key:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", width=300)
        
        if st.button("Analyze Image"):
            with st.spinner("🔍 AI is analyzing the image..."):
                try:
                    model = genai.GenerativeModel('gemini-pro-vision')
                    response = model.generate_content([
                        "You are a maintenance expert. Analyze this equipment image and provide: "
                        "1. Visible faults or damage\n"
                        "2. Potential causes\n" 
                        "3. Repair suggestions\n"
                        "4. Safety precautions\n"
                        "5. Urgency level (Low/Medium/High/Critical)",
                        image
                    ])
                    st.success("Analysis Complete!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.header("Audio Notes (Text Input Alternative)")
    st.info("Audio feature coming soon! For now, describe the issue in text below.")
    audio_text = st.text_area("Describe what you hear or the issue details:")
    
    if audio_text and api_key:
        if st.button("Analyze Description"):
            with st.spinner("🔍 AI is analyzing the description..."):
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    prompt = f"""
                    As a maintenance expert, analyze this technician's description:
                    
                    {audio_text}
                    
                    Provide:
                    1. Likely equipment issues
                    2. Diagnostic steps to verify
                    3. Repair recommendations
                    4. Tools needed
                    5. Estimated repair time
                    """
                    response = model.generate_content(prompt)
                    st.success("Analysis Complete!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab3:
    st.header("Text-Based Diagnosis")
    equipment_type = st.selectbox("Equipment Type", [
        "HVAC System", "Electrical Panel", "Mechanical Equipment", 
        "Plumbing System", "Structural Component", "Other"
    ])
    
    issue_description = st.text_area("Describe the issue in detail:", height=150)
    severity = st.select_slider("Issue Severity", ["Low", "Medium", "High", "Critical"])
    
    if issue_description and api_key:
        if st.button("Get AI Diagnosis"):
            with st.spinner("🔍 AI is diagnosing the issue..."):
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    prompt = f"""
                    Equipment: {equipment_type}
                    Severity: {severity}
                    Issue Description: {issue_description}
                    
                    As a maintenance expert, provide:
                    1. Root cause analysis
                    2. Step-by-step repair instructions
                    3. Required tools and parts
                    4. Safety precautions
                    5. Estimated repair time and cost
                    6. Prevention tips for future
                    """
                    response = model.generate_content(prompt)
                    st.success("Diagnosis Complete!")
                    
                    # Display results in a nice format
                    st.subheader("🔬 AI Diagnosis Results")
                    st.write(response.text)
                    
                    # Quick stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Severity", severity)
                    with col2:
                        st.metric("Equipment", equipment_type)
                    with col3:
                        st.metric("Status", "Diagnosis Ready")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("### 💡 Tips for Best Results:")
st.markdown("- Take clear, well-lit photos of equipment")
- Describe symptoms in detail (unusual sounds, error codes, recent changes)
- Include equipment model numbers if available")