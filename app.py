
import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import json
import re
import base64
from io import BytesIO
from PIL import Image

# Load custom CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Set up the page
st.set_page_config(
    page_title="InsightFlow - AI Maintenance Assistant",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    <div style="text-align: left;">
        <h1>🔧 InsightFlow</h1>
        <p style="font-size: 1.2rem; color: #94a3b8; margin-top: -10px;">
        AI-Powered Maintenance Diagnosis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div style="text-align: right; padding: 10px; background: rgba(16, 185, 129, 0.1); 
                border-radius: 10px; border: 1px solid #10b981;">
        <div style="font-size: 0.9rem; color: #10b981;">🟢 SYSTEM ONLINE</div>
        <div style="font-size: 0.8rem; color: #94a3b8;">Gemini AI Powered</div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with modern styling
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">⚙️</div>
        <div style="font-size: 1.1rem; font-weight: 600;">Configuration</div>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key Input
    api_key = st.text_input("🔑 Google AI Studio API Key:", type="password", 
                           placeholder="Enter your API key...")
    if api_key:
        os.environ['GOOGLE_API_KEY'] = api_key
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        if 'diagnosis_history' in st.session_state:
            st.metric("Cases", len(st.session_state.diagnosis_history))
        else:
            st.metric("Cases", 0)
    with col2:
        if 'learned_patterns' in st.session_state:
            st.metric("Patterns", len(st.session_state.learned_patterns))
        else:
            st.metric("Patterns", 0)
    
    st.markdown("---")
    
    # Features
    st.markdown("### 🚀 Features")
    features = [
        "🤖 AI-Powered Diagnosis",
        "🖼️ Multi-Modal Analysis", 
        "🧠 Learning System",
        "🔧 Repair Instructions",
        "⚠️ Safety Alerts"
    ]
    for feature in features:
        st.markdown(f"<div style='padding: 5px 0;'>{feature}</div>", unsafe_allow_html=True)

# Initialize session state
if 'diagnosis_history' not in st.session_state:
    st.session_state.diagnosis_history = []
if 'expert_mode' not in st.session_state:
    st.session_state.expert_mode = False
if 'learned_patterns' not in st.session_state:
    st.session_state.learned_patterns = {}
if 'equipment_insights' not in st.session_state:
    st.session_state.equipment_insights = {}
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []

# Your existing functions here (keep all your existing functions exactly as they were)
def process_uploaded_image(uploaded_file):
    """Process uploaded image and return PIL Image object"""
    try:
        image = Image.open(uploaded_file)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
        return None

def analyze_image_with_gemini(image, equipment_type, context):
    """Analyze image using Gemini Vision"""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
        Analyze this {equipment_type} image for maintenance issues.
        
        Context: {context}
        
        Please identify:
        1. Visible damage, wear, or faults
        2. Potential safety hazards
        3. Components that may need repair/replacement
        4. Any unusual conditions or patterns
        5. Urgency level (Low/Medium/High/Critical)
        
        Provide specific, actionable observations.
        """
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"❌ Image analysis failed: {str(e)}"

def extract_key_issues(diagnosis_text):
    """Extract key issues from diagnosis for learning"""
    issues = []
    patterns = [
        r'[Cc]ause[s]?[:\s]+([^\.]+)',
        r'[Pp]roblem[s]?[:\s]+([^\.]+)',
        r'[Ii]ssue[s]?[:\s]+([^\.]+)',
        r'[Ff]ault[s]?[:\s]+([^\.]+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, diagnosis_text)
        issues.extend(matches)
    return issues[:3]

def learn_from_case(equipment_type, symptoms, environment, diagnosis_text, severity, has_images=False):
    """Learn from each case and update patterns"""
    symptom_key = "_".join(sorted(symptoms)) if symptoms else "no_symptoms"
    env_key = "_".join(sorted(environment)) if environment else "normal_env"
    pattern_key = f"{equipment_type}|{symptom_key}|{env_key}"
    
    key_issues = extract_key_issues(diagnosis_text)
    
    if pattern_key in st.session_state.learned_patterns:
        st.session_state.learned_patterns[pattern_key]['count'] += 1
        st.session_state.learned_patterns[pattern_key]['last_used'] = datetime.now().isoformat()
        
        if severity in st.session_state.learned_patterns[pattern_key]['severity_dist']:
            st.session_state.learned_patterns[pattern_key]['severity_dist'][severity] += 1
        else:
            st.session_state.learned_patterns[pattern_key]['severity_dist'][severity] = 1
            
        for issue in key_issues:
            if issue not in st.session_state.learned_patterns[pattern_key]['common_issues']:
                st.session_state.learned_patterns[pattern_key]['common_issues'].append(issue)
                
        if has_images:
            st.session_state.learned_patterns[pattern_key]['has_images'] = True
                
    else:
        st.session_state.learned_patterns[pattern_key] = {
            'count': 1,
            'equipment_type': equipment_type,
            'symptoms': symptoms,
            'environment': environment,
            'common_issues': key_issues,
            'severity_dist': {severity: 1},
            'first_seen': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'has_images': has_images
        }
    
    if equipment_type in st.session_state.equipment_insights:
        st.session_state.equipment_insights[equipment_type]['total_cases'] += 1
        st.session_state.equipment_insights[equipment_type]['common_symptoms'].extend(symptoms)
        if has_images:
            st.session_state.equipment_insights[equipment_type]['cases_with_images'] = st.session_state.equipment_insights[equipment_type].get('cases_with_images', 0) + 1
    else:
        st.session_state.equipment_insights[equipment_type] = {
            'total_cases': 1,
            'common_symptoms': symptoms,
            'first_case': datetime.now().isoformat(),
            'cases_with_images': 1 if has_images else 0
        }

def get_learned_insights(equipment_type, symptoms, environment):
    """Get relevant insights from learned patterns"""
    relevant_patterns = []
    symptom_key = "_".join(sorted(symptoms)) if symptoms else "no_symptoms"
    env_key = "_".join(sorted(environment)) if environment else "normal_env"
    
    for pattern_key, pattern_data in st.session_state.learned_patterns.items():
        if pattern_data['equipment_type'] == equipment_type:
            symptom_similarity = len(set(symptoms) & set(pattern_data['symptoms'])) if symptoms else 0
            env_similarity = len(set(environment) & set(pattern_data['environment'])) if environment else 0
            
            if symptom_similarity > 0 or env_similarity > 0:
                pattern_data['similarity_score'] = symptom_similarity + env_similarity
                relevant_patterns.append(pattern_data)
    
    relevant_patterns.sort(key=lambda x: (x['similarity_score'], x['count']), reverse=True)
    return relevant_patterns[:2]

def enhance_prompt_with_learning(base_prompt, equipment_type, symptoms, environment, image_analysis=None):
    """Enhance the AI prompt with learned insights"""
    insights = get_learned_insights(equipment_type, symptoms, environment)
    
    learning_section = ""
    if insights:
        learning_section = "\n\n🎯 **LEARNED INSIGHTS FROM SIMILAR CASES:**\n"
        for i, insight in enumerate(insights, 1):
            learning_section += f"""
            Pattern #{i} (Seen {insight['count']} times):
            • Common Issues: {', '.join(insight['common_issues'][:3])}
            • Typical Severity: {max(insight['severity_dist'].items(), key=lambda x: x[1])[0]}
            • Similar Symptoms: {', '.join(insight['symptoms'])}
            """
        learning_section += "\nConsider these patterns in your analysis."
    
    image_section = ""
    if image_analysis:
        image_section = f"\n\n📷 **IMAGE ANALYSIS RESULTS:**\n{image_analysis}\n\nIntegrate these visual observations with the text description."
    
    return base_prompt + learning_section + image_section

# Main application tabs with modern styling
tab1, tab2, tab3, tab4 = st.tabs(["🔍 New Diagnosis", "📋 Case History", "🧠 AI Learning", "⚙️ Settings"])

with tab1:
    st.markdown("""
    <div class="card">
        <h2>🆕 New Maintenance Case</h2>
        <p style="color: #94a3b8;">Complete the form below to get AI-powered diagnosis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Equipment information in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        equipment_type = st.selectbox(
            "🏭 Equipment Type",
            ["HVAC System", "Electrical Panel", "Mechanical Equipment", 
             "Plumbing System", "Structural Component", "Industrial Machine", "Vehicle", "Network Equipment", "Other"]
        )
    
    with col2:
        severity = st.select_slider(
            "⚠️ Issue Severity",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium"
        )
    
    with col3:
        urgency = st.select_slider(
            "⏰ Repair Urgency",
            options=["Routine", "Soon", "Urgent", "Emergency"],
            value="Soon"
        )

    # Image Upload Section
    st.markdown("""
    <div class="card">
        <h3>🖼️ Upload Equipment Images</h3>
        <p style="color: #94a3b8;">Upload clear photos showing the issue (optional but recommended)</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose images...",
        type=['jpg', 'jpeg', 'png', 'bmp'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    # Process and display uploaded images
    st.session_state.uploaded_images = []
    image_analysis_results = []
    
    if uploaded_files:
        st.subheader("📸 Uploaded Images")
        cols = st.columns(min(3, len(uploaded_files)))
        
        for i, uploaded_file in enumerate(uploaded_files):
            with cols[i % 3]:
                st.image(uploaded_file, caption=f"Image {i+1}", use_column_width=True)
                processed_image = process_uploaded_image(uploaded_file)
                if processed_image:
                    st.session_state.uploaded_images.append(processed_image)
                    
                    # Quick image analysis
                    with st.spinner(f"🔍 Analyzing image {i+1}..."):
                        analysis = analyze_image_with_gemini(
                            processed_image, 
                            equipment_type,
                            f"Equipment: {equipment_type}, Severity: {severity}"
                        )
                        image_analysis_results.append(analysis)
                        
                    with st.expander(f"📊 Image {i+1} Analysis"):
                        st.write(analysis)

    # Enhanced issue description
    st.markdown("""
    <div class="card">
        <h3>📝 Issue Description</h3>
        <p style="color: #94a3b8;">Provide detailed information for better diagnosis</p>
    </div>
    """, unsafe_allow_html=True)
    
    issue_description = st.text_area(
        "Describe the issue:",
        placeholder="""🚨 FOR BEST RESULTS - Describe:

• WHAT: Specific symptoms you're seeing
• WHEN: When did it start? Is it constant or intermittent?  
• WHERE: Which component/area is affected?
• IMPACT: How is performance affected?
• RECENT CHANGES: Any recent maintenance or environmental changes?
• ERROR CODES: Specific codes or warning messages""",
        height=150,
        label_visibility="collapsed"
    )
    
    # Real-time feedback
    if issue_description:
        char_count = len(issue_description)
        if char_count < 50:
            st.warning("🔍 More details needed! Try to provide specific symptoms and timing.")
        elif char_count < 100:
            st.info("📝 Good start! Consider adding error codes or performance impact.")
        else:
            st.success(f"✅ Excellent detail! ({char_count} characters)")

    # Additional context
    col4, col5 = st.columns(2)
    
    with col4:
        environment = st.multiselect(
            "🌍 Environmental Factors",
            ["High Temperature", "High Humidity", "Dusty Environment", "Vibration", "Corrosive Atmosphere", "Network Storm", "Power Fluctuations", "None"]
        )

with col5:
        symptoms = st.multiselect(
            "🔍 Observed Symptoms", 
            ["Unusual Noise", "Overheating", "Reduced Performance", "Leaks", "Error Codes", "Smell", "Visual Damage", "Intermittent Operation", "High Error Rate", "Network Issues", "Slow Response", "Complete Failure"]
        )

    # Show learning insights if available
    if equipment_type and (symptoms or environment):
        insights = get_learned_insights(equipment_type, symptoms, environment)
        if insights:
            st.markdown("""
            <div class="card">
                <h3>🧠 Learning Insights</h3>
            </div>
            """, unsafe_allow_html=True)
            for insight in insights:
                image_info = " 📷" if insight.get('has_images') else ""
                st.info(f"""
                **Pattern Recognition**: This combination seen **{insight['count']} times** before{image_info}
                **Common Issues**: {', '.join(insight['common_issues'][:2])}
                **Typical Severity**: {max(insight['severity_dist'].items(), key=lambda x: x[1])[0]}
                """)

    # Expert mode toggle
    st.session_state.expert_mode = st.checkbox("🔬 Expert Mode (Detailed Technical Analysis)")

    # Process diagnosis
    if st.button("🚀 Get AI Diagnosis", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please enter your Google AI Studio API Key in the sidebar")
        elif not issue_description.strip():
            st.error("❌ Please describe the issue")
        else:
            with st.spinner("🔍 AI is analyzing the issue... This may take 30-45 seconds"):
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro-latest')
                    
                    # Combine image analyses
                    combined_image_analysis = ""
                    if image_analysis_results:
                        combined_image_analysis = "IMAGE ANALYSIS SUMMARY:\n" + "\n".join([f"Image {i+1}: {analysis}" for i, analysis in enumerate(image_analysis_results)])
                    
                    # Enhanced prompt for better diagnosis
                    base_prompt = f"""
                    MAINTENANCE DIAGNOSIS REQUEST

                    EQUIPMENT: {equipment_type}
                    SEVERITY: {severity}
                    URGENCY: {urgency}
                    ENVIRONMENT: {', '.join(environment) if environment else 'Normal'}
                    SYMPTOMS: {', '.join(symptoms) if symptoms else 'Not specified'}
                    IMAGES UPLOADED: {len(uploaded_files)} image(s)

                    ISSUE DESCRIPTION:
                    {issue_description}
                    """
                    
                    # Enhance prompt with learned insights and image analysis
                    enhanced_prompt = enhance_prompt_with_learning(
                        base_prompt, equipment_type, symptoms, environment, combined_image_analysis
                    )
                    
                    if st.session_state.expert_mode:
                        prompt = enhanced_prompt + """
                        As an expert maintenance engineer with 20+ years of experience, provide a COMPREHENSIVE technical analysis:

                        1. INTEGRATED ANALYSIS:
                           - Combine visual evidence from images with described symptoms
                           - Root cause identification considering all available data
                           - Failure mechanism analysis

                        2. TECHNICAL DIAGNOSIS:
                           - Step-by-step verification procedure
                           - Required diagnostic tools and measurements
                           - Correlation between visual signs and performance issues

                        3. REPAIR PROCEDURE:
                           - Detailed step-by-step instructions
                           - Required tools and equipment
                           - Replacement parts with specifications
                           - Integration of visual findings with repair steps

                        4. SAFETY PROTOCOLS:
                           - Lockout/tagout requirements
                           - Personal protective equipment
                           - Hazardous material handling
                           - Emergency procedures

                        5. TIME & COST ESTIMATION:
                           - Labor hours breakdown
                           - Parts cost estimation
                           - Total repair timeline

                        6. PREVENTION & MAINTENANCE:
                           - Preventive maintenance schedule
                           - Visual inspection guidelines
                           - Early warning signs
                           - Spare parts recommendation

                        Format with clear technical headings and bullet points.
                        Integrate image findings throughout your analysis.
                        """
                    else:
                        prompt = enhanced_prompt + """
                        As a maintenance expert, provide a clear and practical diagnosis:

                        1. COMBINED ASSESSMENT: Integrate image findings with described issues
                        2. LIKELY CAUSE: What's probably wrong based on all evidence
                        3. QUICK CHECKS: Simple things to verify first  
                        4. REPAIR STEPS: Step-by-step fix incorporating visual clues
                        5. TOOLS NEEDED: What you'll need
                        6. SAFETY FIRST: Important warnings
                        7. TIME & COST: Rough estimates
                        8. PREVENTION: How to avoid future issues

                        Use simple language and focus on actionable steps.
                        Reference image findings where relevant.
                        """
                    
                    response = model.generate_content(prompt)
                    
                    # Store case data
                    case_data = {
                        'id': len(st.session_state.diagnosis_history) + 1,
                        'timestamp': datetime.now().isoformat(),
                        'equipment_type': equipment_type,
                        'severity': severity,
                        'urgency': urgency,
                        'symptoms': symptoms,
                        'environment': environment,
                        'issue_description': issue_description,
                        'diagnosis': response.text,
                        'expert_mode': st.session_state.expert_mode,
                        'images_count': len(uploaded_files),
                        'has_images': len(uploaded_files) > 0
                    }
                    st.session_state.diagnosis_history.append(case_data)
                    
                    # Learn from this case
                    learn_from_case(equipment_type, symptoms, environment, response.text, severity, len(uploaded_files) > 0)
                    
                    # Display results
                    st.success("✅ Diagnosis Complete!")
                    st.balloons()
                    
                    # Results header with metrics
                    st.markdown("""
                    <div class="card">
                        <h2>📊 Diagnosis Summary</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Equipment", equipment_type)
                    with col2:
                        st.metric("Severity", severity, delta=None)
                    with col3:
                        st.metric("Urgency", urgency)
                    with col4:
                        st.metric("Images Used", len(uploaded_files))
                    
                    # Show learning impact
                    if get_learned_insights(equipment_type, symptoms, environment):
                        st.success("🧠 **AI Learning Applied**: This diagnosis was enhanced with insights from similar historical cases!")

if uploaded_files:
                        st.success("🖼️ **Image Analysis Integrated**: Visual evidence was incorporated into the diagnosis!")
                    
                    # Detailed analysis
                    st.markdown("---")
                    st.markdown("""
                    <div class="card">
                        <h2>🔬 Detailed Analysis & Recommendations</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(response.text)
                    
                    # Quick actions
                    st.markdown("---")
                    st.markdown("""
                    <div class="card">
                        <h2>🚀 Quick Actions</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    action_col1, action_col2, action_col3 = st.columns(3)
                    
                    with action_col1:
                        if st.button("📋 Save to History", use_container_width=True):
                            st.success("✅ Case saved to history!")
                    
                    with action_col2:
                        st.download_button(
                            label="📄 Export Report",
                            data=response.text,
                            file_name=f"insightflow_diagnosis_{case_data['id']}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with action_col3:
                        if st.button("🆕 New Diagnosis", use_container_width=True):
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.info("💡 Tip: Check your API key and try again. If issues persist, the AI service might be temporarily unavailable.")

# Continue with the other tabs (Tab2, Tab3, Tab4) - keep your existing code for these
# [Include your existing code for tabs 2, 3, and 4 here...]

with tab2:
    st.markdown("""
    <div class="card">
        <h2>📋 Case History</h2>
        <p style="color: #94a3b8;">Review past maintenance cases and diagnoses</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.diagnosis_history:
        st.info("📭 No cases yet. Complete your first diagnosis to see history here!")
    else:
        # Filter and search
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search cases...")
        with col2:
            equipment_filter = st.selectbox("Filter by equipment", ["All"] + list(set([case['equipment_type'] for case in st.session_state.diagnosis_history])))
        
        # Display cases
        for case in reversed(st.session_state.diagnosis_history):
            # Apply filters
            if search_term and search_term.lower() not in str(case).lower():
                continue
            if equipment_filter != "All" and case['equipment_type'] != equipment_filter:
                continue
                
            with st.expander(f"Case #{case['id']} - {case['equipment_type']} ({case['timestamp'][:10]})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Severity:** {case['severity']}")
                with col2:
                    st.write(f"**Urgency:** {case['urgency']}")
                with col3:
                    st.write(f"**Images:** {case['images_count']}")
                
                st.write(f"**Issue:** {case['issue_description'][:200]}...")
                
                if st.button(f"View Full Analysis", key=f"view_{case['id']}"):
                    st.markdown(case['diagnosis'])
                
                if st.button(f"Delete Case", key=f"delete_{case['id']}"):
                    st.session_state.diagnosis_history = [c for c in st.session_state.diagnosis_history if c['id'] != case['id']]
                    st.rerun()

with tab3:
    st.markdown("""
    <div class="card">
        <h2>🧠 AI Learning Insights</h2>
        <p style="color: #94a3b8;">See what the AI has learned from your cases</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.learned_patterns:
        st.info("🤖 AI hasn't learned any patterns yet. Complete a few diagnoses to see insights here!")
    else:
        st.markdown("""
        <div class="card">
            <h3>📊 Learning Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Patterns", len(st.session_state.learned_patterns))
        with col2:
            total_cases = sum([pattern['count'] for pattern in st.session_state.learned_patterns.values()])
            st.metric("Total Cases Learned", total_cases)
        with col3:
            patterns_with_images = sum([1 for pattern in st.session_state.learned_patterns.values() if pattern.get('has_images')])
            st.metric("Patterns with Images", patterns_with_images)
        
        st.markdown("""
        <div class="card">
            <h3>🔍 Learned Patterns</h3>
        </div>
        """, unsafe_allow_html=True)
        for pattern_key, pattern_data in list(st.session_state.learned_patterns.items())[:10]:
            with st.expander(f"Pattern: {pattern_data['equipment_type']} (Seen {pattern_data['count']} times)"):
                st.write(f"**Symptoms:** {', '.join(pattern_data['symptoms']) if pattern_data['symptoms'] else 'None'}")
                st.write(f"**Environment:** {', '.join(pattern_data['environment']) if pattern_data['environment'] else 'Normal'}")
                st.write(f"**Common Issues:** {', '.join(pattern_data['common_issues'][:3])}")
                st.write(f"**Severity Distribution:** {pattern_data['severity_dist']}")
                if pattern_data.get('has_images'):
                    st.write("✅ **Uses image analysis**")
        
        st.markdown("""
        <div class="card">
            <h3>🏭 Equipment Insights</h3>
        </div>
        """, unsafe_allow_html=True)
        for equipment, insights in st.session_state.equipment_insights.items():
            with st.expander(f"{equipment} ({insights['total_cases']} cases)"):
                st.write(f"**First Case:** {insights['first_case'][:10]}")
                st.write(f"**Cases with Images:** {insights.get('cases_with_images', 0)}")
                if 'common_symptoms' in insights:
                    from collections import Counter
                    symptom_counts = Counter(insights['common_symptoms'])
                    st.write("**Most Common Symptoms:**")
                    for symptom, count in symptom_counts.most_common(5):
                        st.write(f"  - {symptom}: {count} times")

with tab4:
    st.markdown("""
    <div class="card">
        <h2>⚙️ Settings & Configuration</h2>
        <p style="color: #94a3b8;">Manage your application settings and data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>🔧 Application Settings</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Clear data option
    if st.button("🗑️ Clear All History", type="secondary"):
        if st.checkbox("I'm sure I want to delete all history and learned patterns"):
            st.session_state.diagnosis_history = []
            st.session_state.learned_patterns = {}
            st.session_state.equipment_insights = {}
            st.success("✅ All data cleared!")
    
    st.markdown("""
    <div class="card">
        <h3>📊 Export Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Export Case History", use_container_width=True):
            if st.session_state.diagnosis_history:
                import json
                history_json = json.dumps(st.session_state.diagnosis_history, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=history_json,
                    file_name="insightflow_case_history.json",
                    mime="application/json"
                )
            else:
                st.warning("No case history to export")
    

with col2:
        if st.button("🧠 Export Learned Patterns", use_container_width=True):
            if st.session_state.learned_patterns:
                patterns_json = json.dumps(st.session_state.learned_patterns, indent=2)
                st.download_button(
                    label="Download Patterns",
                    data=patterns_json,
                    file_name="insightflow_learned_patterns.json",
                    mime="application/json"
                )
            else:
                st.warning("No learned patterns to export")
    
    st.markdown("""
    <div class="card">
        <h3>ℹ️ About InsightFlow</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **InsightFlow - AI Maintenance Assistant**
    
    **Version 1.0**  
    Powered by Google Gemini AI
    
    **Features:**
    - 🤖 AI-powered maintenance diagnosis
    - 🖼️ Multi-modal image analysis  
    - 🧠 Continuous learning from cases
    - 📊 Historical case tracking
    - 🔧 Expert-level recommendations
    
    **Built with:** Streamlit & Google Generative AI
    """)

# Add some custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


