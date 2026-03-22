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
    
    # Calibration Alignment (The actual grid is 4 to 18 years)
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos') 
    
    # 1. SHIFT CHART LEFT
    # By setting xlim to (3.8, 21), we add more space on the right (up to age 21)
    # This pushes the chart (which ends at 18) to the left.
    ax.set_xlim(3.8, 21.0)
    ax.set_ylim(19.5, 28.5)
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        left_vals = [v['Left'] for v in st.session_state.visits]
        right_vals = [v['Right'] for v in st.session_state.visits]
        
        # Plot Points
        ax.scatter(ages, left_vals, color='#008000', s=55, edgecolors='white', linewidths=0.5, zorder=10)
        ax.scatter(ages, right_vals, color='#FF0000', s=55, edgecolors='white', linewidths=0.5, zorder=10)

    # --- Legend Positioning ---
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left eye', markerfacecolor='#008000', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Right eye', markerfacecolor='#FF0000', markersize=8)
    ]
    
    # Placed slightly in from the left edge
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.05, 0.95), 
              frameon=True, fontsize=10, facecolor='white', framealpha=0.9)

    plt.title(f"Axial Length Progression: {name} ({gender})", fontsize=18, fontweight='bold', pad=25)
    
    if notes:
        plt.figtext(0.12, 0.05, f"Notes: {notes}", fontsize=11, style='italic', wrap=True)
    
    ax.axis('off')
    st.pyplot(fig)
    
    # High-Res Download
    save_fn = f"AXL_Report_{name}.png"
    plt.savefig(save_fn, dpi=400, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("📩 Download High-Resolution Report", f, file_name=save_fn, mime="image/png")
else:
    st.error("Chart images not found.")
