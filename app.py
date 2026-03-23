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

# --- Clinical CSS: STRICT SIZE CONTROL ---
st.markdown("""
    <style>
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; padding-bottom: 10px; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 12px; margin-bottom: 15px; color: #333; }
    div.stButton > button[kind="primary"] { background-color: #1a2a44 !important; color: white !important; }
    
    /* This forces the chart to stay at a professional size */
    .stPlotlyChart, .matplotlib-container {
        max-width: 800px;
        margin: auto;
    }
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

    if st.button("Undo Last Entry", width='stretch'):
        if st.session_state.visits: 
            st.session_state.visits.pop()
            st.rerun()

# --- 3. Main Display Area ---
st.title("AXIAL LENGTH CLINICAL HISTORY")

st.markdown(f"""<div class="patient-bar"><strong>Patient:</strong> {name.upper()} &nbsp; | &nbsp; 
<strong>Sex:</strong> {gender} &nbsp; | &nbsp; <strong>Report Date:</strong> {datetime.now().strftime("%d %b %Y")}</div>""", unsafe_allow_html=True)

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
img_array = load_fixed_bg(img_file)

if img_array is not None:
    plt.close('all')
    
    # Smaller figsize to fix the "Too Big" problem
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=100) 
    
    try:
        # --- DEEP CALIBRATION ---
        # We are moving x_min significantly to the left (from 3.3 to 2.2) 
        # to compensate for the large white margin in your screenshot.
        x_min, x_max = 2.25, 19.35  
        y_min, y_max = 19.45, 28.55 
        
        extent = [x_min, x_max, y_min, y_max]
        
        ax.imshow(img_array, extent=extent, aspect='auto', interpolation='lanczos', origin='upper')
        
        # LOCK VISIBLE WINDOW: Standardize what the clinician sees
        ax.set_xlim(4, 18)
        ax.set_ylim(20.0, 28.0)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=100, edgecolors='white', linewidth=1.5, zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=100, edgecolors='white', linewidth=1.5, zorder=10)

        # Legend & Formal Title
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left OS', markerfacecolor='#008000', markersize=8),
            Line2D([0], [0], marker='o', color='w', label='Right OD', markerfacecolor='#FF0000', markersize=8)
        ], loc='upper left', bbox_to_anchor=(0.14, 0.96), frameon=True, edgecolor='#1a2a44', fontsize='small')
        
        plt.title(f"AXIAL LENGTH GROWTH CHART: {name.upper()}", 
                  fontsize=16, fontfamily='serif', fontweight='bold', color='#1a2a44', pad=10)
        
        ax.axis('off')

        # Buffer for Export
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        buf.seek(0)
        
        # Display with restricted container width
        _, col_mid, _ = st.columns([1, 8, 1])
        with col_mid:
            st.pyplot(fig, use_container_width=True)

        if st.session_state.visits:
            st.download_button("📥 EXPORT CLINICAL GROWTH REPORT", buf, f"AXL_{name}.png", "image/png")

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Reference Image Missing: {img_file}")
