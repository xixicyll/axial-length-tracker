import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd
from matplotlib.lines import Line2D

# Wide layout and ultra-tight top padding
st.set_page_config(page_title="AXL Tracker", layout="wide")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    h1 {margin-top: -20px; font-size: 2rem !important;}
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: Data Entry ---
with st.sidebar:
    st.subheader("👤 Patient Info")
    name = st.text_input("Name/ID", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    notes = st.text_area("Clinical Notes", placeholder="Brief notes...", height=65)
    
    st.divider()
    
    st.subheader("➕ Add Visit")
    v_age = st.number_input("Age", 4.0, 18.0, 9.0, 0.1)
    c1, c2 = st.columns(2)
    v_left = c1.number_input("Left (mm)", 18.0, 32.0, 24.0)
    v_right = c2.number_input("Right (mm)", 18.0, 32.0, 24.0)
    
    if st.button("Add Data Point", type="primary", use_container_width=True):
        if 'visits' not in st.session_state: st.session_state.visits = []
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    if st.button("Undo Last", use_container_width=True):
        if st.session_state.get('visits'): st.session_state.visits.pop(); st.rerun()
    
    if st.button("Clear All", use_container_width=True):
        st.session_state.visits = []; st.rerun()

# --- Main Page: Restored Header ---
st.title("👁️ Axial Length History Tracker")
if 'visits' not in st.session_state: st.session_state.visits = []

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    # figsize=(15, 7.5) provides a wide-screen aspect ratio to prevent scrolling
    fig, ax = plt.subplots(figsize=(15, 7.5))
    img = mpimg.imread(img_file)
    
    # Image calibration & Shift Left (xlim up to 22)
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos') 
    ax.set_xlim(3.8, 22.0) 
    ax.set_ylim(19.5, 28.5)
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        left_vals = [v['Left'] for v in st.session_state.visits]
        right_vals = [v['Right'] for v in st.session_state.visits]
        ax.scatter(ages, left_vals, color='#008000', s=55, edgecolors='white', zorder=10)
        ax.scatter(ages, right_vals, color='#FF0000', s=55, edgecolors='white', zorder=10)

    # Professional Legend Position
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left eye', markerfacecolor='#008000', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Right eye', markerfacecolor='#FF0000', markersize=8)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.20, 0.96), 
              frameon=True, fontsize=10, facecolor='white', framealpha=0.9)

    plt.title(f"Patient Record: {name} ({gender})", fontsize=16, fontweight='bold', pad=15)
    
    if notes:
        # Keep notes short and at the very bottom of the chart
        plt.figtext(0.15, 0.05, f"Notes: {notes}", fontsize=10, style='italic', wrap=True)
    
    ax.axis('off')
    
    # use_container_width ensures it fills the screen without overflowing vertically
    st.pyplot(fig, use_container_width=True)
    
    # Compact Save button
    save_fn = f"AXL_{name}.png"
    plt.
