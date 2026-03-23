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

# --- Clinical CSS: Screen Fit ---
st.markdown("""
    <style>
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 5px solid #1a2a44; padding-bottom: 5px; font-size: 24px; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 8px; margin-bottom: 10px; font-size: 14px; }
    .stImage > img { border: 1px solid #ddd; border-radius: 4px; }
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
    st.subheader("🎯 Fine-Tune Alignment")
    # These sliders let you "nudge" the background chart left/right or up/down
    nudge_x = st.slider("Left/Right Nudge", 2.0, 5.0, 3.2, 0.05)
    nudge_y = st.slider("Up/Down Nudge", 18.5, 20.5, 19.4, 0.05)
    
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
    
    # FIGSIZE: (8, 5) fits the "Full Chart" comfortably on screen
    fig, ax = plt.subplots(figsize=(8, 5), dpi=110) 
    
    try:
        # --- DYNAMIC CALIBRATION ---
        # We use the sliders to define the image boundaries
        x_min, x_max = nudge_x, nudge_x + 17.0
        y_min, y_max = nudge_y, nudge_y + 9.2
        
        extent = [x_min, x_max, y_min, y_max]
        ax.imshow(img_array, extent=extent, aspect='auto', interpolation='lanczos', origin='upper')
        
        # DISPLAY LIMITS: Set wide enough to show all labels (Age 4-18 and AXL 20-28)
        ax.set_xlim(3.0, 19.0)
        ax.set_ylim(19.2, 28.8)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=70, edgecolors='white', linewidth=1, zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=70, edgecolors='white', linewidth=1, zorder=10)

        # Legend & Title
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='OS', markerfacecolor='#008000', markersize=6),
            Line2D([0], [0], marker='o', color='w', label='OD', markerfacecolor='#FF0000', markersize=6)
        ], loc='upper left', bbox_to_anchor=(0.1, 0.98), frameon=True, fontsize='xx-small')
        
        plt.title(f"AXL GROWTH: {name.upper()}", fontsize=12, fontweight='bold', pad=8)
        ax.axis('off')

        # Rendering to a buffer for Streamlit
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=140, bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        
        # DISPLAY: Center the image and force it to be clear
        _, col_mid, _ = st.columns([1, 6, 1])
        with col_mid:
            st.image(buf, use_container_width=True)

        if st.session_state.visits:
            st.download_button("📥 EXPORT REPORT", buf, f"AXL_{name}.png", "image/png")

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Image Missing: {img_file}")
