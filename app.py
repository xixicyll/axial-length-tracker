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
        right_vals = [v['Right'] for v in st.session_state.visits]
        
        # Plot Points
        # Left eye: Green (#008000), small size (60)
        # Right eye: Red (#FF0000), small size (60)
        ax.scatter(ages, left_vals, color='#008000', s=60, edgecolors='white', linewidths=0.5, zorder=10)
        ax.scatter(ages, right_vals, color='#FF0000', s=60, edgecolors='white', linewidths=0.5, zorder=10)

    # --- Updated Legend (Green/Red) ---
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left eye', markerfacecolor='#008000', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Right eye', markerfacecolor='#FF0000', markersize=8)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, fontsize=10, facecolor='white', framealpha=0.9)

    # Titles and Meta Data
    plt.title(f"Axial Length Progression: {name} ({gender})", fontsize=18, fontweight='bold', pad=25)
    
    if notes:
        plt.figtext(0.12, 0.05, f"Notes: {notes}", fontsize=11, style='italic', wrap=True)
    
    # Hide the extra axes (use the chart's printed grid instead)
    ax.axis('off')
    st.pyplot(fig)
    
    # Download
    save_fn = f"AXL_Report_{name}_{gender}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("📩 Download Professional Report (PNG)", f, file_name=save_fn, mime="image/png")
else:
    st.error(f"Image '{img_file}' not found in GitHub. Please verify the filenames match exactly.")
