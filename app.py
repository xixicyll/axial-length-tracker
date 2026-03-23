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

# --- Clinical CSS: Compact View ---
st.markdown("""
    <style>
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; padding-bottom: 10px; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 12px; margin-bottom: 15px; color: #333; }
    div.stButton > button[kind="primary"] { background-color: #1a2a44 !important; color: white !important; }
    /* Limit chart width to stop it from being "too big" */
    .stPlotlyChart, .matplotlib-container { max-width: 750px; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_crop_image(file_path):
    if os.path.exists(file_path):
        img = Image.open(file_path)
        img = ImageOps.exif_transpose(img)
        
        # --- THE FIX: CROP TO ACTIVE GRID ---
        # We manually trim the white space so the '4' is at the very left edge
        # Adjust these percentages if the crop is too aggressive
        width, height = img.size
        # (left, top, right, bottom)
        # These values are calibrated to your specific screenshot layout
        left = width * 0.095   # Trims the Y-axis labels
        top = height * 0.08    # Trims the Top Title
        right = width * 0.95   # Trims the right margin
        bottom = height * 0.88 # Trims the Age labels at the bottom
        
        img_cropped = img.crop((left, top, right, bottom))
        return np.array(img_cropped)
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

    if st.button("Undo Last Entry", width='stretch'):
        if st.session_state.visits: 
            st.session_state.visits.pop()
            st.rerun()

# --- 3. Main Display Area ---
st.title("AXIAL LENGTH CLINICAL HISTORY")

st.markdown(f"""<div class="patient-bar"><strong>Patient:</strong> {name.upper()} &nbsp; | &nbsp; 
<strong>Sex:</strong> {gender} &nbsp; | &nbsp; <strong>Report Date:</strong> {datetime.now().strftime("%d %b %Y")}</div>""", unsafe_allow_html=True)

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
img_array = load_and_crop_image(img_file)

if img_array is not None:
    plt.close('all')
    # Compact figure size
    fig, ax = plt.subplots(figsize=(9, 6), dpi=100) 
    
    try:
        # --- ZERO-PADDING ALIGNMENT ---
        # Since the image is cropped to the grid, the extent is now EXACT.
        ax.imshow(img_array, extent=[4, 18, 20.0, 28.0], aspect='auto', interpolation='lanczos', origin='upper')
        
        # Match the viewing window exactly to the extent
        ax.set_xlim(4, 18)
        ax.set_ylim(20.0, 28.0)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=90, edgecolors='white', linewidth=1.2, zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=90, edgecolors='white', linewidth=1.2, zorder=10)

        # Legend & Title
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left OS', markerfacecolor='#008000', markersize=8),
            Line2D([0], [0], marker='o', color='w', label='Right OD', markerfacecolor='#FF0000', markersize=8)
        ], loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, edgecolor='#1a2a44', fontsize='x-small')
        
        plt.title(f"AXIAL LENGTH GROWTH CHART: {name.upper()}", 
                  fontsize=15, fontfamily='serif', fontweight='bold', color='#1a2a44', pad=10)
        
        ax.axis('off')

        # Buffer for Export
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        buf.seek(0)
        
        # UI Display
        _, col_mid, _ = st.columns([1, 8, 1])
        with col_mid:
            st.pyplot(fig, use_container_width=True)

        if st.session_state.visits:
            st.download_button("📥 EXPORT REPORT", buf, f"AXL_{name}.png", "image/png")

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Reference Image Missing: {img_file}")
