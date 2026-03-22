import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import io
import pandas as pd
from matplotlib.lines import Line2D

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# Ultra-tight top padding via CSS to save screen real estate
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 0rem;}
    h1 {margin-top: -10px; font-size: 2.2rem !important;}
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 2. Sidebar: Patient Management ---
with st.sidebar:
    st.markdown("### 👤 Patient Profile")
    
    st.caption("Patient Name or ID")
    name = st.text_input("Name", "Unnamed", key="patient_name", label_visibility="collapsed")
    
    st.caption("Biological Gender")
    gender = st.selectbox("Gender", ["Female", "Male"], key="patient_gender", label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("### ➕ Add New Measurement")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    
    cl, cr = st.columns(2)
    v_left = cl.number_input("Left Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    v_right = cr.number_input("Right Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    
    if st.button("Update Chart", type="primary", use_container_width=True):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        # Sorting ensures dots appear in correct chronological order
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    c_undo, c_clear = st.columns(2)
    if c_undo.button("Undo Last", use_container_width=True):
        if st.session_state.visits: 
            st.session_state.visits.pop()
            st.rerun()
            
    if c_clear.button("Clear All", use_container_width=True):
        st.session_state.visits = []
        st.rerun()

# --- 3. Main Display Area ---
st.title("👁️ Axial Length History Tracker")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    # Create the figure with high DPI (200) for on-screen sharpness
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=200)
    img = mpimg.imread(img_file)
    
    # Image Calibration (Extent defines the coordinate system)
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos')
    ax.set_xlim(3.8, 20.0)
    ax.set_ylim(19.5, 28.5)
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        l_vals = [v['Left'] for v in st.session_state.visits]
        r_vals = [v['Right'] for v in st.session_state.visits]
        
        # Scatter dots only - white edge makes them pop against the background}' not found.")
