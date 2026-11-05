import streamlit as st
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import tempfile

# Import project AI system
try:
    from ai_system import AgriculturalAISystem
    HAS_AI = True
except ImportError:
    HAS_AI = False

# Set page configuration
st.set_page_config(
    page_title="AgriWaste - AI Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load secrets if available
def get_config(key, default):
    try:
        return st.secrets[key]
    except:
        return default

WEATHER_KEY = get_config("WEATHER_API_KEY", None)
APP_EMAIL = get_config("CONTACT_EMAIL", "support@agriwaste.ai")
CONFIDENCE_THRESHOLD = get_config("MODEL_CONFIDENCE_THRESHOLD", 0.70)

# Custom CSS for premium look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.1rem;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #2ecc71;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        color: #7f8c8d;
        font-size: 1rem;
        text-transform: uppercase;
    }
    .result-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    .premium-header {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(#2ecc71, #27ae60);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Initialize AI System
@st.cache_resource
def get_ai_system():
    if HAS_AI:
        return AgriculturalAISystem()
    return None

ai_system = get_ai_system()

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 class='premium-header'>🌾 AgriWaste AI</h1>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/color/144/null/farming.png", width=100)
    st.markdown("---")
    
    st.info("AI-powered marketplace for transforming agricultural waste into value.")
    
    st.markdown("### 📊 Market Stats")
    st.metric("Total Waste Traded", "1.2k Tons", "+15%")
    st.metric("Carbon Credits Earned", "450 kg", "+8%")
    st.metric("Active Buyers", "124", "+12")
    
    st.markdown("---")
    st.markdown(f"Contact: {APP_EMAIL}")
    st.markdown("Created with ❤️ for SEM 5 AI Project")

# --- Header ---
st.markdown("<h1 class='premium-header'>Agricultural Waste Marketplace & AI Analyzer</h1>", unsafe_allow_html=True)
st.write("Leverage advanced CNN and Regression models to classify waste, predict prices, and connect with buyers.")

# --- Tabs ---
tab_analyzer, tab_market, tab_about = st.tabs(["🔍 AI Analyzer", "📈 Market Insights", "ℹ️ About Project"])

# --- TAB 1: AI ANALYZER ---
with tab_analyzer:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("### 📸 Upload Waste Image")
        uploaded_file = st.file_uploader("Choose an image of crop waste...", type=["jpg", "jpeg", "png", "jfif"])
        
        quantity = st.slider("Estimated Quantity (kg)", 100, 10000, 1000, step=100)
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            
            if st.button("🚀 Run AI Analysis", type="primary"):
                if ai_system:
                    with st.spinner("🧠 AI is analyzing the waste..."):
                        # Save temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = Path(tmp.name)
                        
                        try:
                            # Run analysis
                            analysis = ai_system.analyze_waste_complete(tmp_path, quantity_kg=quantity)
                            
                            # Clean up
                            os.unlink(tmp_path)
                            
                            st.session_state['last_analysis'] = analysis
                            st.success("Analysis Complete!")
                        except Exception as e:
                            st.error(f"Error during analysis: {e}")
                else:
                    st.error("AI System not loaded correctly.")

    with col2:
        if 'last_analysis' in st.session_state:
            analysis = st.session_state['last_analysis']
            
            if analysis['status'] == 'success':
                # Classification Result
                clf = analysis['classification']
                st.markdown(f"""
                <div class='result-card'>
                    <h3 style='margin-top:0'>🌾 Classification: <b>{clf['predicted_type']}</b></h3>
                    <p>Confidence: <b>{clf['confidence']:.1%}</b> ({clf['confidence_level']})</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quality Metrics
                qual = analysis['quality']
                st.markdown("### ✅ Quality Assessment")
                q_col1, q_col2, q_col3 = st.columns(3)
                q_col1.metric("Grade", qual['quality_grade'])
                q_col2.metric("Score", f"{qual['quality_score']:.1f}/100")
                q_col3.metric("Purity", f"{qual['purity_percent']:.0f}%")
                
                with st.expander("Detailed Quality Parameters"):
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = qual['moisture_percent'],
                        title = {'text': "Moisture (%)"},
                        gauge = {'axis': {'range': [None, 30]},
                                'bar': {'color': "#3498db"},
                                'steps' : [
                                    {'range': [0, 10], 'color': "lightgreen"},
                                    {'range': [10, 20], 'color': "yellow"},
                                    {'range': [20, 30], 'color': "red"}]}
                    ))
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.write(f"**Calorific Value:** {qual['calorific_value_mj_kg']:.2f} MJ/kg")
                    st.write(f"**Carbon Content:** {qual['carbon_content_percent']:.1f}%")

                # Price Prediction
                price = analysis['price']
                st.markdown(f"""
                <div class='result-card' style='border-top: 5px solid #f1c40f'>
                    <h3 style='margin-top:0'>💰 Market Valuation</h3>
                    <h2 style='color:#f39c12'>₹{price['total_value']:,.2f}</h2>
                    <p>Predicted Rate: <b>₹{price['predicted_price_per_kg']:.2f}/kg</b></p>
                    <p><small>Confidence: {price['confidence']:.1%}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Carbon Impact
                carbon = analysis['carbon_impact']
                st.markdown(f"""
                <div class='result-card' style='border-top: 5px solid #2ecc71'>
                    <h3 style='margin-top:0'>🌍 Environmental Impact</h3>
                    <p>CO₂ Offset: <b>{carbon['co2_avoided_kg']:.2f} kg</b></p>
                    <p>Tree Equivalent: <b>{carbon['trees_equivalent']:.1f} trees</b></p>
                    <p>Category: <span style='color:#27ae60; font-weight:bold'>{carbon['impact_category']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Buyer Recommendations
                st.markdown("### 🎯 Recommended Buyers")
                buyers = analysis['buyer_recommendations']
                for b in buyers[:3]:
                    with st.container():
                        st.markdown(f"""
                        <div style='background:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left:4px solid #2ecc71'>
                            <div style='display:flex; justify-content:space-between'>
                                <b>{b['name']}</b>
                                <span style='color:#27ae60'>Match: {b['match_score']:.1%}</span>
                            </div>
                            <small>{b['type']} | {b['location']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                if st.button("🛒 List on Marketplace"):
                    st.balloons()
                    st.success("Listing created successfully!")
            else:
                st.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")
        else:
            st.info("Upload an image and click 'Run AI Analysis' to see results.")

# --- TAB 2: MARKET INSIGHTS ---
with tab_market:
    st.markdown("### 📈 Market Trends")
    
    # Generate some dummy historical data
    dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
    data = pd.DataFrame({
        'Month': dates,
        'Rice Husk': np.random.normal(5300, 200, 12),
        'Wheat Straw': np.random.normal(4300, 150, 12),
        'Cotton Stalks': np.random.normal(5600, 300, 12)
    })
    
    fig_price = px.line(data, x='Month', y=['Rice Husk', 'Wheat Straw', 'Cotton Stalks'], 
                  title='Historical Price Trends (₹/Ton)',
                  labels={'value': 'Price (₹)', 'variable': 'Waste Type'},
                  template='plotly_white')
    st.plotly_chart(fig_price, use_container_width=True)
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        # Waste Distribution
        waste_dist = pd.DataFrame({
            'Type': ['Rice Husk', 'Wheat Straw', 'Sugarcane Bagasse', 'Cotton Stalks', 'Others'],
            'Volume': [35, 25, 20, 12, 8]
        })
        fig_pie = px.pie(waste_dist, values='Volume', names='Type', title='Market Volume Distribution (%)',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_m2:
        # Regional Stats
        regional_stats = pd.DataFrame({
            'State': ['Punjab', 'Haryana', 'UP', 'Maharashtra', 'Gujarat'],
            'Surplus': [1200, 950, 1500, 800, 600]
        })
        fig_bar = px.bar(regional_stats, x='State', y='Surplus', title='Regional Waste Surplus (Tons)',
                        color='Surplus', color_continuous_scale='Greens')
        st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: ABOUT ---
with tab_about:
    st.markdown("""
    ### 📖 Project Overview
    The **AgriWaste AI Marketplace** is a cutting-edge platform designed to solve the problem of agricultural waste burning and inefficient biomass utilization. 
    By leveraging Artificial Intelligence, we bridge the gap between farmers and industrial buyers.
    
    ### 🛠️ Technology Stack
    - **Deep Learning**: CNN (MobileNetV2) for crop waste classification.
    - **Machine Learning**: Regression models for price prediction and quality assessment.
    - **Frontend**: Streamlit for a fast, responsive, and interactive dashboard.
    - **Data Visualization**: Plotly for real-time market analytics.
    
    ### 🚀 Key Features
    1. **Instant Classification**: Identify waste type from a single photo.
    2. **Smart Pricing**: Get real-time market value based on moisture and purity.
    3. **Impact Tracking**: See your contribution to CO₂ reduction.
    4. **Market Matching**: Direct connection to verified biomass buyers.
    
    ### 👥 Team
    Developed as part of the AI Major Project (Semester 5).
    """)
    
    st.image("https://img.icons8.com/fluency/96/null/artificial-intelligence.png", width=50)
    st.caption("Version 1.0.0 | Built with Streamlit & TensorFlow")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #7f8c8d;'>© 2024 AgriWaste AI Marketplace. All rights reserved.</p>", unsafe_allow_html=True)
