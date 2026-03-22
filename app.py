import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd
from matplotlib.lines import Line2D

st.set_page_config(page_title="Myopia Axial Tracker", layout="wide")

st.title("👁️ Axial Length History Tracker")

# --- Initialize Data Storage ---
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- Sidebar: Patient Info & Visit Entry ---
with st.sidebar:
    st.header("1. Patient Information")
    name = st.text_input("Patient Name / ID", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    notes = st.text_area("Clinical Notes", "")
    
    st.divider()
    
    st.header("2. Add a Visit")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    col_left, col_right = st.columns(2)
    v_left = col_left.number_input("Left eye (mm)", 18.0, 32.0, 24.00)
    v_right = col_right.number_input("Right eye (mm)", 18.0, 32.0, 24.00)
    
    if st.button("➕ Add This Visit", type="primary"):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        # Sort by age so any past visits added later fall into place
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    col_del1, col_del2 = st.columns(2)
    if col_del1.button("🔙 Undo Last"):
        if st.session_state.visits:
            st.session_state.visits.pop()
            st.rerun()
            
    if col_del2.button("🗑️ Clear All"):
        st.session_state.visits = []
        st.rerun()

# --- Main Page: Plotting ---
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    fig, ax = plt.subplots(figsize=(12, 10))
    img = mpimg.imread(img_file)
    
    # Calibration Alignment (Adjust if dots don't line up perfectly)
    # [min_age, max_age, min_length, max_length]
    ax.imshow(img, extent=[3.8, 18.2, 19.8, 28.2]) 
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        left_vals = [v['Left'] for v in st.session_state.visits]
        right_vals = [v['Right']
