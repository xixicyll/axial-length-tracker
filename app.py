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
    col_os, col_od = st.columns(2)
    v_os = col_os.number_input("Left eye (mm)", 18.0, 32.0, 24.00)
    v_od = col_od.number_input("Right eye (mm)", 18.0, 32.0, 24.00)
    
    if st.button("➕ Add This Visit", type="primary"):
        st.session_state.visits.append({"Age": v_age, "Left": v_os, "Right": v_od})
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
    
    # Calibration Alignment
    ax.imshow(img, extent=[3.8, 18.2, 19.8, 28.2]) 
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        left_vals = [v['Left'] for v in st.session_state.visits]
        right_vals = [v['Right'] for v in st.session_state.visits]
        
        # Plot Points (Small size = 60)
        ax.scatter(ages, left_vals, color='blue', s=60, edgecolors='white', linewidths=0.5, zorder=10)
        ax.scatter(ages, right_vals, color='red', s=60, edgecolors='white', linewidths=0.5, zorder=10)

    # --- Simplified Legend ---
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left eye', markerfacecolor='blue', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Right eye', markerfacecolor='red', markersize=8)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, fontsize=10)

    # Titles and Meta Data
    plt.title(f"Axial Length Progression: {name}", fontsize=18, fontweight='bold', pad=25)
    
    if notes:
        plt.figtext(0.12, 0.05, f"Notes: {notes}", fontsize=11, style='italic', wrap=True)
    
    ax.axis('off')
    st.pyplot(fig)
    
    # Download
    save_fn = f"AXL_Report_{name}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("📩 Download Professional Report", f, file_name=save_fn, mime="image/png")
else:
    st.error("Missing chart images in GitHub.")
