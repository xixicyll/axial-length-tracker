import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd
from matplotlib.lines import Line2D

# Wide layout and ultra-tight top padding
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")
st.markdown(""" <style> .block-container {padding-top: 1rem; padding-bottom: 0rem;} </style> """, unsafe_allow_html=True)

# Initialize visits
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 1. Compact Sidebar (Refined) ---
with st.sidebar:
    st.markdown("### 👤 Patient Profile")
    
    # Separate rows but using captions to save space
    st.caption("Patient Name/ID")
    name = st.text_input("Name", "Unnamed", label_visibility="collapsed")
    
    st.caption("Gender")
    gender = st.selectbox("Gender", ["Female", "Male"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("### ➕ Add Measurement")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    
    # L and R on one line for efficiency
    cl, cr = st.columns(2)
    v_left = cl.number_input("Left (mm)", 18.0, 32.0, 24.0, step=0.01)
    v_right = cr.number_input("Right (mm)", 18.0, 32.0, 24.0, step=0.01)
    
    if st.button("Add Data Point", type="primary", use_container_width=True):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    # Utilities
    c_undo, c_clear = st.columns(2)
    if c_undo.button("Undo Last", use_container_width=True):
        if st.session_state.visits: st.session_state.visits.pop(); st.rerun()
    if c_clear.button("Clear All", use_container_width=True):
        st.session_state.visits = []; st.rerun()

# --- 2. Main Dashboard ---
st.title("👁️ Axial Length History Tracker")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    # (3) Center Title: fig.suptitle or plt.title works, but plt.title centers on axes
    fig, ax = plt.subplots(figsize=(15, 8))
    img = mpimg.imread(img_file)
    
    # Image calibration
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos')
    ax.set_xlim(3.8, 20.0)
    ax.set_ylim(19.5, 28.5)
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        l_vals = [v['Left'] for v in st.session_state.visits]
        r_vals = [v['Right'] for v in st.session_state.visits]
        
        ax.plot(ages, l_vals, color='#008000', alpha=0.6, lw=2.5, zorder=5)
        ax.plot(ages, r_vals, color='#FF0000', alpha=0.6, lw=2.5, zorder=5)
        ax.scatter(ages, l_vals, color='#008000', s=80, edgecolors='white', zorder=10)
        ax.scatter(ages, r_vals, color='#FF0000', s=80, edgecolors='white', zorder=10)

    # (2) Legend: Shifted further right (x=0.18) to ensure it clears the Y-axis numbers
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left Eye', markerfacecolor='#008000', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Right Eye', markerfacecolor='#FF0000', markersize=10)
    ]
    # bbox_to_anchor=(x, y) -> increased x to 0.18
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.18, 0.90), 
              frameon=True, facecolor='white', framealpha=0.9, fontsize=12)

    # (3) Centered Title - padding increased for a cleaner look
    plt.title(f"Patient Record: {name} ({gender})", fontsize=20, fontweight='bold', pad=30)
    
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)

    # Save logic
    save_fn = f"AXL_{name}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("💾 Download Clinical Report", f, file_name=save_fn)
else:
    st.error(f"Growth curve image ({img_file}) not found in directory.")
