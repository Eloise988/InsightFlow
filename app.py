import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import json

# Set up the page
st.set_page_config(
    page_title="InsightFlow - AI Maintenance Assistant",
    page_icon="🔧",
    layout="wide"
)

# Title and description
st.title("🔧 InsightFlow - AI Maintenance Assistant")
st.markdown("### *Multi-Modal Maintenance Diagnosis Powered by Google Gemini AI*")

# Sidebar for API key and features
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")
    if api_key:
        os.environ['GOOGLE_API_KEY'] = api_key
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")
    
    st.markdown("---")
    st.header("📊 Quick Stats")
    if 'diagnosis_history' in st.session_state:
        st.metric("Cases Processed", len(st.session_state.diagnosis_history))
    st.metric("AI Model", "Gemini 1.5 Pro")
    st.metric("Status", "🟢 Online")
    
    st.markdown("---")
    st.header("🎯 Features")
    st.markdown("• 🤖 AI-Powered Diagnosis")
    st.markdown("• 🔧 Repair Instructions") 
    st.markdown("• ⚠️ Safety Alerts")
    st.markdown("• 💰 Cost Estimation")
    st.markdown("• 📈 Maintenance History")

# Initialize session state
if 'diagnosis_history' not in st.session_state:
    st.session_state.diagnosis_history = []
if 'expert_mode' not in st.session_state:
    st.session_state.expert_mode = False

# Main application tabs
tab1, tab2, tab3 = st.tabs(["🔍 New Diagnosis", "📋 Case History", "⚙️ Advanced Settings"])

with tab1:
    st.header("🆕 New Maintenance Case")
    
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

    # Detailed issue description
    st.subheader("📝 Issue Description")
    
    issue_description = st.text_area(
        "Describe the issue in detail:",
        placeholder="• What symptoms are you observing?\n• Any unusual sounds, smells, or visual signs?\n• Error codes or warning messages?\n• When did the issue start?\n• Recent maintenance or changes?",
        height=150,
        help="Be as detailed as possible for accurate diagnosis"
    )

    # Additional context
    st.subheader("🔍 Additional Context")
    
    col4, col5 = st.columns(2)
    
    with col4:
        environment = st.multiselect(
            "Environmental Factors",
            ["High Temperature", "High Humidity", "Dusty Environment", "Vibration", "Corrosive Atmosphere", "None"]
        )
    
    with col5:
        symptoms = st.multiselect(
            "Observed Symptoms", 
            ["Unusual Noise", "Overheating", "Reduced Performance", "Leaks", "Error Codes", "Smell", "Visual Damage", "Intermittent Operation", "High Error Rate", "Network Issues"]
        )

    # Expert mode toggle
    st.session_state.expert_mode = st.checkbox("🔬 Expert Mode (Detailed Technical Analysis)")

    # Process diagnosis
    if st.button("🚀 Get AI Diagnosis", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Please enter your Google AI Studio API Key in the sidebar")
        elif not issue_description.strip():
            st.error("❌ Please describe the issue")
        else:
            with st.spinner("🔍 AI is analyzing the issue... This may take 20-30 seconds"):
                try:
                    # FIXED: Use correct model name
                    model = genai.GenerativeModel('gemini-1.5-pro-latest')
                    
                    # Enhanced prompt for better diagnosis
                    base_prompt = f"""
                    MAINTENANCE DIAGNOSIS REQUEST

                    EQUIPMENT: {equipment_type}
                    SEVERITY: {severity}
                    URGENCY: {urgency}
                    ENVIRONMENT: {', '.join(environment) if environment else 'Normal'}
                    SYMPTOMS: {', '.join(symptoms) if symptoms else 'Not specified'}

                    ISSUE DESCRIPTION:
                    {issue_description}

                    """
                    
                    if st.session_state.expert_mode:
                        prompt = base_prompt + """
                        As an expert maintenance engineer with 20+ years of experience, provide a COMPREHENSIVE technical analysis:

                        1. ROOT CAUSE ANALYSIS:
                           - Primary fault identification
                           - Contributing factors
                           - Failure mechanism

                        2. TECHNICAL DIAGNOSIS:
                           - Step-by-step verification procedure
                           - Required diagnostic tools
                           - Expected measurements/readings

                        3. REPAIR PROCEDURE:
                           - Detailed step-by-step instructions
                           - Required tools and equipment
                           - Replacement parts with specifications
                           - Technical specifications (torque values, tolerances, etc.)

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
                           - Monitoring parameters
                           - Early warning signs
                           - Spare parts recommendation

                        Format with clear technical headings and bullet points.
                        """
                    else:
                        prompt = base_prompt + """
                        As a maintenance expert, provide a clear and practical diagnosis:

                        1. LIKELY CAUSE: What's probably wrong
                        2. QUICK CHECKS: Simple things to verify first  
                        3. REPAIR STEPS: Step-by-step fix
                        4. TOOLS NEEDED: What you'll need
                        5. SAFETY FIRST: Important warnings
                        6. TIME & COST: Rough estimates
                        7. PREVENTION: How to avoid future issues

                        Use simple language and focus on actionable steps.
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
                        'expert_mode': st.session_state.expert_mode
                    }
                    st.session_state.diagnosis_history.append(case_data)
                    
                    # Display results
                    st.success("✅ Diagnosis Complete!")
                    st.balloons()
                    
                    # Results header with metrics
                    st.subheader("📊 Diagnosis Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Equipment", equipment_type)
                    with col2:
                        st.metric("Severity", severity, delta=None)
                    with col3:
                        st.metric("Urgency", urgency)
                    with col4:
                        st.metric("Case ID", f"#{case_data['id']}")
                    
                    # Detailed analysis
                    st.markdown("---")
                    st.subheader("🔬 Detailed Analysis & Recommendations")
                    st.markdown(response.text)
                    
                    # Quick actions
                    st.markdown("---")
                    st.subheader("🚀 Quick Actions")
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

with tab2:
    st.header("📋 Diagnosis History")
    
    if not st.session_state.diagnosis_history:
        st.info("📝 No diagnosis history yet. Complete your first diagnosis above!")
    else:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_equipment = st.multiselect(
                "Filter by Equipment",
                options=list(set([case['equipment_type'] for case in st.session_state.diagnosis_history])),
                default=[]
            )
        with col2:
            filter_severity = st.multiselect(
                "Filter by Severity", 
                options=["Low", "Medium", "High", "Critical"],
                default=[]
            )
        
        # Filter cases
        filtered_cases = st.session_state.diagnosis_history
        if filter_equipment:
            filtered_cases = [case for case in filtered_cases if case['equipment_type'] in filter_equipment]
        if filter_severity:
            filtered_cases = [case for case in filtered_cases if case['severity'] in filter_severity]
        
        # Display cases
        for case in reversed(filtered_cases):
            with st.expander(f"Case #{case['id']}: {case['equipment_type']} | {case['severity']} | {case['timestamp'][:16]}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**🕒 Time:** {case['timestamp'][:16]}")
                    st.write(f"**⚠️ Severity:** {case['severity']}")
                    st.write(f"**⏰ Urgency:** {case['urgency']}")
                with col2:
                    st.write(f"**🔧 Symptoms:** {', '.join(case['symptoms']) if case['symptoms'] else 'None'}")
                    st.write(f"**🌡️ Environment:** {', '.join(case['environment']) if case['environment'] else 'Normal'}")
                    st.write(f"**🔬 Mode:** {'Expert' if case['expert_mode'] else 'Standard'}")
                
                st.markdown("**📝 Issue Description:**")
                st.write(case['issue_description'])
                
                st.markdown("**🔍 Diagnosis:**")
                st.write(case['diagnosis'])
                
                # Case actions
                st.download_button(
                    label="📄 Export This Case",
                    data=case['diagnosis'],
                    file_name=f"insightflow_case_{case['id']}.txt",
                    mime="text/plain",
                    key=f"export_{case['id']}"
                )

with tab3:
    st.header("⚙️ Advanced Settings")
    
    st.subheader("🔧 Application Settings")
    
    st.checkbox("Enable detailed logging", value=False)
    st.checkbox("Show technical details", value=True)
    
    st.subheader("📈 Analytics")
    if st.session_state.diagnosis_history:
        st.write(f"Total cases processed: {len(st.session_state.diagnosis_history)}")
        
        # Basic analytics
        equipment_counts = {}
        severity_counts = {}
        
        for case in st.session_state.diagnosis_history:
            equipment_counts[case['equipment_type']] = equipment_counts.get(case['equipment_type'], 0) + 1
            severity_counts[case['severity']] = severity_counts.get(case['severity'], 0) + 1
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Equipment Distribution:**")
            for equip, count in equipment_counts.items():
                st.write(f"- {equip}: {count} cases")
        
        with col2:
            st.write("**Severity Distribution:**")
            for severity, count in severity_counts.items():
                st.write(f"- {severity}: {count} cases")
    
    st.subheader("🛠️ Maintenance")
    if st.button("Clear History", type="secondary"):
        st.session_state.diagnosis_history = []
        st.success("History cleared!")
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <h3>💡 Pro Tips for Best Results</h3>
    <p>• Be specific about symptoms and timing<br>
    • Include error codes and environmental conditions<br>
    • Use Expert Mode for complex technical issues<br>
    • Save important cases for future reference</p>
    <p><em>Built with Google Gemini AI • Streamlit • InsightFlow Technology</em></p>
</div>
""", unsafe_allow_html=True)
