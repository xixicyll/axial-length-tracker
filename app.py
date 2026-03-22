import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd
from matplotlib.lines import Line2D

# 1. Page Configuration for a Professional Dashboard
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# Ultra-tight top padding via CSS
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 0rem;}
    h1 {margin-top: -10px; font-size: 2.2rem !important;}
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State for Data Persistence
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 2. Compact Sidebar: Patient Management ---
with st.sidebar:
    st.markdown("### 👤 Patient Profile")
    
    # Separate rows for clarity, but using captions to save vertical space
    st.caption("Patient Name or ID")
    name = st.text_input("Name", "Unnamed", label_visibility="collapsed")
    
    st.caption("Biological Gender")
    gender = st.selectbox("Gender", ["Female", "Male"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("### ➕ Add New Visit")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    
    # Left and Right measurement on one row
    cl, cr = st.columns(2)
    v_left = cl.number_input("Left Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    v_right = cr.number_input("Right Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    
    if st.button("Update Chart", type="primary", use_container_width=True):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        # Keep data sorted by age for proper line plotting
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    # Utility buttons
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

# Determine which growth curve to load
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file
