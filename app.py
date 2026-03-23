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

# --- Clinical CSS: Compact & Centered ---
st.markdown("""
    <style>
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; padding-bottom: 10px; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 12px; margin-bottom: 15px; color: #333; }
    div.stButton > button[kind="primary"] { background-color: #1a2a44 !important; color: white !important; }
    
    /* Strict control over the chart display size */
    .matplotlib-container {
        max-width: 850px;
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
    
    # FIGSIZE: Balanced for clinical readability without being overwhelming
    fig, ax = plt.subplots(figsize=(11, 7), dpi=100) 
    
    try:
        # --- THE ALIGNMENT CALIBRATION ---
        # Adjusting x_min to 2.5 and x_max to 19.5 ensures Age 9 lands 
        # exactly on the 9th vertical line by compensating for image margins.
        x_min, x_max = 2.5, 19.5  
        y_min, y_max = 19.5, 28.5 
        
        extent = [x_min, x_max, y_min, y_max]
        
        # We use 'upper' to keep the labels readable
        ax.imshow(img_array, extent=extent, aspect='auto', interpolation='lanczos', origin='upper')
        
        # DISPLAY LIMITS: We 'crop' the view visually but keep the full image data
        ax.set_xlim(3.5, 18.5) # Shows a bit of the 4 and 18 labels
        ax.set_ylim(19.5, 28.5) # Shows the full 20 to 28 range
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=110, edgecolors='white', linewidth=1.5, zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=110, edgecolors='white', linewidth=1.5, zorder=10)

        # Legend & Title
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left OS', markerfacecolor='#008000', markersize=9),
            Line2D([0], [0], marker='o', color='w', label='Right OD', markerfacecolor='#FF0000', markersize=9)
        ], loc='upper left', bbox_to_anchor=(0.14, 0.96), frameon=True, edgecolor='#1a2a44', fontsize='small')
        
        plt.title(f"AXIAL LENGTH GROWTH CHART: {name.upper()}", 
                  fontsize=18, fontfamily='serif', fontweight='bold', color='#1a2a44', pad=15)
        
        ax.axis('off')

        # Buffer & Layout Rendering
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=160, bbox_inches='tight')
        buf.seek(0)
        
        _, col_mid, _ = st.columns([0.5, 9, 0.5])
        with col_mid:
            st.pyplot(fig, use_container_width=True)

        if st.session_state.visits:
            st.download_button("📥 EXPORT CLINICAL GROWTH REPORT", buf, f"AXL_{name}.png", "image/png")

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Reference Image Missing: {img_file}")
