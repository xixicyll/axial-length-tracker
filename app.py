import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import numpy as np
import os
import io
from matplotlib.lines import Line2D
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# --- Clinical CSS ---
st.markdown("""
    <style>
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; padding-bottom: 5px; font-size: 24px; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 8px; margin-bottom: 10px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_fixed_bg(file_path):
    if os.path.exists(file_path):
        img = Image.open(file_path)
        img = ImageOps.exif_transpose(img)
        return np.array(img)
    return None

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 2. Sidebar ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Full Name", "Unnamed Patient")
    gender = st.selectbox("Biological Sex", ["Female", "Male"])
    
    st.divider()
    st.subheader("➕ New Entry")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    cl, cr = st.columns(2)
    v_left = cl.number_input("OS (mm)", 18.0, 32.0, 24.00, step=0.01)
    v_right = cr.number_input("OD (mm)", 18.0, 32.0, 24.00, step=0.01)
    
    if st.button("Update Record", type="primary", width='stretch'):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits.sort(key=lambda x: x['Age'])
        st.rerun()

    st.divider()
    st.subheader("🎯 Alignment Calibration")
    # Nudge moves the whole image
    nudge_x = st.slider("Left Margin Nudge", 1.0, 5.0, 2.5, 0.01)
    # Width stretches/shrinks the age lines
    width_x = st.slider("Age Grid Stretch", 15.0, 20.0, 17.5, 0.01)
    # Length calibration
    nudge_y = st.slider("Top Margin Nudge", 18.5, 20.5, 19.4, 0.01)
    
    if st.button("Undo Last Entry", width='stretch'):
        if st.session_state.visits: 
            st.session_state.visits.pop()
            st.rerun()

# --- 3. Main Display Area ---
st.title("AXIAL LENGTH CLINICAL HISTORY")

st.markdown(f"""<div class="patient-bar"><strong>Patient:</strong> {name.upper()} &nbsp; | &nbsp; 
<strong>Sex:</strong> {gender} &nbsp; | &nbsp; <strong>Date:</strong> {datetime.now().strftime("%d %b %Y")}</div>""", unsafe_allow_html=True)

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
img_array = load_fixed_bg(img_file)

if img_array is not None:
    plt.close('all')
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=110) 
    
    try:
        # --- CALIBRATION FORMULA ---
        # x_min/max defines where the image starts and ends in Age years
        x_min = nudge_x
        x_max = nudge_x + width_x
        
        # y_min/max defines the Axial Length mapping
        y_min = nudge_y
        y_max = nudge_y + 9.5 # Standard vertical span for 20-28mm + margins
        
        ax.imshow(img_array, extent=[x_min, x_max, y_min, y_max], aspect='auto', interpolation='lanczos', origin='upper')
        
        # Lock view to standard chart range
        ax.set_xlim(3.5, 18.5)
        ax.set_ylim(19.5, 28.5)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=80, edgecolors='white', linewidth=1.2, zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=80, edgecolors='white', linewidth=1.2, zorder=10)

        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='OS', markerfacecolor='#008000', markersize=7),
            Line2D([0], [0], marker='o', color='w', label='OD', markerfacecolor='#FF0000', markersize=7)
        ], loc='upper left', bbox_to_anchor=(0.1, 0.98), frameon=True, fontsize='xx-small')
        
        plt.title(f"AXL GROWTH: {name.upper()}", fontsize=14, fontweight='bold')
        ax.axis('off')

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=140, bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        
        _, col_mid, _ = st.columns([1, 8, 1])
        with col_mid:
            st.image(buf, use_container_width=True)

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Image Missing: {img_file}")
