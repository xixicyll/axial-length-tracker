import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd
from matplotlib.lines import Line2D

# 1. Wide layout and ultra-tight top padding
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")
st.markdown(""" <style> .block-container {padding-top: 1rem; padding-bottom: 0rem;} </style> """, unsafe_allow_html=True)

# Initialize visits
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 1. Compact Sidebar ---
with st.sidebar:
    st.caption("📋 Patient Profile")
    c_name, c_gen = st.columns([2, 1])
    name = c_name.text_input("ID", "Unnamed", label_visibility="collapsed")
    gender = c_gen.selectbox("Sex", ["Female", "Male"], label_visibility="collapsed")
    
    st.divider()
    
    st.caption("➕ Add Measurement")
    v_age = st.number_input("Age", 4.0, 18.0, 9.0, 0.1)
    # Put L and R on one line to save vertical space
    cl, cr = st.columns(2)
    v_left = cl.number_input("Left", 18.0, 32.0, 24.0, step=0.01)
    v_right = cr.number_input("Right", 18.0, 32.0, 24.0, step=0.01)
    
    if st.button("Add Data Point", type="primary", use_container_width=True):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    # Smaller buttons for utility
    c_undo, c_clear = st.columns(2)
    if c_undo.button("Undo", use_container_width=True):
        if st.session_state.visits: st.session_state.visits.pop(); st.rerun()
    if c_clear.button("Clear", use_container_width=True):
        st.session_state.visits = []; st.rerun()

# --- 2. Main Dashboard ---
st.title("👁️ Axial Length History Tracker")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    fig, ax = plt.subplots(figsize=(15, 8))
    img = mpimg.imread(img_file)
    
    # Calibration & extent
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos')
    ax.set_xlim(3.8, 20.0)
    ax.set_ylim(19.5, 28.5)
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        l_vals = [v['Left'] for v in st.session_state.visits]
        r_vals = [v['Right'] for v in st.session_state.visits]
        
        ax.plot(ages, l_vals, color='#008000', alpha=0.6, lw=2, zorder=5)
        ax.plot(ages, r_vals, color='#FF0000', alpha=0.6, lw=2, zorder=5)
        ax.scatter(ages, l_vals, color='#008000', s=70, edgecolors='white', zorder=10)
        ax.scatter(ages, r_vals, color='#FF0000', s=70, edgecolors='white', zorder=10)

    # (2) Legend moved down and inside (adjusted bbox_to_anchor)
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left Eye', markerfacecolor='#008000', markersize=9),
        Line2D([0], [0], marker='o', color='w', label='Right Eye', markerfacecolor='#FF0000', markersize=9)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.05, 0.90), 
              frameon=True, facecolor='white', framealpha=0.8, fontsize=11)

    # (3) Centered Title
    plt.title(f"Patient Record: {name} ({gender})", fontsize=18, fontweight='bold', pad=20, loc='center')
    
    ax.axis('off')
    st.pyplot(fig, use_container_width=True)

    # Clean Download button below chart
    save_fn = f"AXL_{name}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("💾 Download Report Image", f, file_name=save_fn)
else:
    st.error("Growth curve background images not found.")
