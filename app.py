import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image, ImageOps
import numpy as np
import os
import io
from matplotlib.lines import Line2D
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# --- Clinical Professional CSS ---
st.markdown("""
    <style>
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; padding-bottom: 10px; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 15px; margin-bottom: 20px; color: #333; }
    div.stButton > button[kind="primary"] { background-color: #1a2a44 !important; color: white !important; border: none !important; }
    div.stDownloadButton > button { 
        background-color: #4682B4 !important; 
        color: white !important; 
        font-weight: 600 !important; 
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. THE ROOT CAUSE FIX: Neutralizing Metadata
@st.cache_data
def load_fixed_bg(file_path):
    if os.path.exists(file_path):
        # Open with PIL to access metadata
        img = Image.open(file_path)
        # This line removes hidden "Rotate 90" or "Mirror" tags from your phone/scanner
        img = ImageOps.exif_transpose(img)
        # Convert to a format Matplotlib understands
        return np.array(img)
    return None

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 3. Sidebar ---
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

# --- 4. Main Display Area ---
st.title("AXIAL LENGTH CLINICAL HISTORY")

today = datetime.now().strftime("%d %b %Y")
st.markdown(f"""
    <div class="patient-bar">
        <strong>Patient:</strong> {name.upper()} &nbsp; | &nbsp; 
        <strong>Sex:</strong> {gender} &nbsp; | &nbsp; 
        <strong>Report Date:</strong> {today}
    </div>
    """, unsafe_allow_html=True)

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
img_array = load_fixed_bg(img_file)

if img_array is not None:
    plt.close('all')
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=100) 
    
    try:
        # Standard Grid: Age 4-18, AXL 20-28
        # We use a standard [left, right, bottom, top] extent
        extent = [4, 18, 20.0, 28.0]
        
        # Plotting with origin='upper' (default) because ImageOps already fixed the orientation
        ax.imshow(img_array, extent=extent, aspect='auto', interpolation='nearest', origin='upper')
        
        ax.set_xlim(4, 18)
        ax.set_ylim(20.0, 28.0)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            l_vals = [v['Left'] for v in st.session_state.visits]
            r_vals = [v['Right'] for v in st.session_state.visits]
            
            ax.scatter(ages, l_vals, color='#008000', s=140, edgecolors='white', linewidth=1.5, zorder=10)
            ax.scatter(ages, r_vals, color='#FF0000', s=140, edgecolors='white', linewidth=1.5, zorder=10)

        # Legend & Formal Title
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left Eye (OS)', markerfacecolor='#008000', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Right Eye (OD)', markerfacecolor='#FF0000', markersize=10)
        ], loc='upper left', bbox_to_anchor=(0.18, 0.94), frameon=True, edgecolor='#1a2a44')
        
        plt.title(f"AXIAL LENGTH GROWTH CHART: {name.upper()}", 
                  fontsize=20, fontfamily='serif', fontweight='bold', color='#1a2a44', pad=15)
        
        ax.axis('off')

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=180, bbox_inches='tight')
        buf.seek(0)
        
        st.pyplot(fig, width='stretch', clear_figure=True)

        if st.session_state.visits:
            st.download_button(
                label="📥 EXPORT CLINICAL GROWTH REPORT",
                data=buf,
                file_name=f"AXL_Report_{name.replace(' ', '_')}.png",
                mime="image/png"
            )

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Reference Image Missing: {img_file}")
