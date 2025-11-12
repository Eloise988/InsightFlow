import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

# Set up the page
st.set_page_config(
    page_title="InsightFlow - Maintenance AI",
    page_icon="🔧",
    layout="wide"
)

# Title and description
st.title("🔧 InsightFlow - AI Maintenance Assistant")
st.markdown("Describe equipment issues and get AI-powered diagnosis and repair instructions.")

# Sidebar for API key
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")
    if api_key:
        os.environ['GOOGLE_API_KEY'] = api_key
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")

# Initialize session state
if 'diagnosis_history' not in st.session_state:
    st.session_state.diagnosis_history = []

# Main application
st.header("Equipment Diagnosis")

# Equipment information
col1, col2 = st.columns(2)
with col1:
    equipment_type = st.selectbox(
        "Equipment Type",
        ["HVAC System", "Electrical Panel", "Mechanical Equipment", 
         "Plumbing System", "Structural Component", "Other"]
    )
with col2:
    severity = st.select_slider(
        "Issue Severity",
        options=["Low", "Medium", "High", "Critical"]
    )

# Issue description
issue_description = st.text_area(
    "Describe the issue in detail:",
    placeholder="Describe symptoms, unusual sounds, error codes, visual issues, or recent changes...",
    height=150
)

# Process diagnosis
if st.button("🔍 Get AI Diagnosis", type="primary") and api_key:
    with st.spinner("🔍 AI is analyzing the issue..."):
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Equipment: {equipment_type}
            Severity: {severity}
            Issue Description: {issue_description}
            
            As an expert maintenance technician, provide a comprehensive diagnosis with:
            
            1. ROOT CAUSE ANALYSIS: What is likely causing this issue?
            2. REPAIR STEPS: Step-by-step instructions to fix it
            3. TOOLS NEEDED: Specific tools required
            4. PARTS REQUIRED: Any replacement parts needed
            5. SAFETY PRECAUTIONS: Critical safety warnings
            6. TIME ESTIMATE: How long the repair should take
            7. PREVENTION TIPS: How to prevent this issue in future
            
            Format the response clearly with headings for each section.
            """
            
            response = model.generate_content(prompt)
            
            # Store in session state
            case_data = {
                'timestamp': datetime.now().isoformat(),
                'equipment_type': equipment_type,
                'severity': severity,
                'diagnosis': response.text
            }
            st.session_state.diagnosis_history.append(case_data)
            
            # Display results
            st.success("✅ Diagnosis Complete!")
            st.subheader("🔬 AI Diagnosis Results")
            
            # Quick stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Equipment", equipment_type)
            with col2:
                st.metric("Severity", severity)
            with col3:
                st.metric("Status", "Diagnosis Ready")
            
            # Detailed analysis
            st.markdown("---")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")

# History section
if st.session_state.diagnosis_history:
    st.header("📋 Diagnosis History")
    for i, case in enumerate(reversed(st.session_state.diagnosis_history)):
        with st.expander(f"Case {len(st.session_state.diagnosis_history)-i}: {case['equipment_type']} - {case['severity']}"):
            st.write(f"**Timestamp:** {case['timestamp'][:16]}")
            st.write(f"**Diagnosis:** {case['diagnosis']}")

# Footer
st.markdown("---")
st.markdown("### 💡 Tips for Best Results:")
st.markdown("- Describe symptoms in detail (sounds, smells, performance issues)")
st.markdown("- Include any error codes or warning lights")
st.markdown("- Mention recent maintenance or changes")
st.markdown("- Note environmental conditions (temperature, humidity)")
