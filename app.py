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

if os.path.exists(img_file):
    # Set high DPI (200) for crystal clear lines and text on-screen
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=200)
    img = mpimg.imread(img_file)
    
    # Image Calibration & Display
    # 'lanczos' interpolation ensures the background remains as sharp as possible
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos')
    
    # Define plot boundaries
    ax.set_xlim(3.8, 20.0)
    ax.set_ylim(19.5, 28.5)
    
    # Plot Patient Data
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        l_vals = [v['Left'] for v in st.session_state.visits]
        r_vals = [v['Right'] for v in st.session_state.visits]
        
        # Draw progression lines
        ax.plot(ages, l_vals, color='#008000', alpha=0.7, lw=2.5, zorder=5)
        ax.plot(ages, r_vals, color='#FF0000', alpha=0.7, lw=2.5, zorder=5)
        
        # Add high-visibility markers
        ax.scatter(ages, l_vals, color='#008000', s=90, edgecolors='white', linewidth=1.5, zorder=10)
        ax.scatter(ages, r_vals, color='#FF0000', s=90, edgecolors='white', linewidth=1.5, zorder=10)

    # Legend Configuration: Positioned right of the Y-axis numbers
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left Eye (OS)', markerfacecolor='#008000', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Right Eye (OD)', markerfacecolor='#FF0000', markersize=10)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.18, 0.92), 
              frameon=True, facecolor='white', framealpha=0.9, fontsize=12, shadow=True)

    # Title & Aesthetics
    plt.title(f"Axial Length Growth Record: {name} ({gender})", fontsize=22, fontweight='bold', pad=35)
    ax.axis('off')
    
    # Display the final sharpened plot
    st.pyplot(fig, use_container_width=True, clear_figure=True)

    # --- 4. Export Capabilities ---
    save_fn = f"AXL_Report_{name}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    
    with open(save_fn, "rb") as f:
        st.download_button(
            label="💾 Download High-Resolution Report",
            data=f,
            file_name=save_fn,
            mime="image/png",
            use_container_width=False
        )
else:
    st.error(f"Required background image '{img_file}' is missing from the server.")
    st.info("Please ensure your .jfif files are in the same folder as app.py.")
