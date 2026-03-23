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
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; padding-bottom: 10px; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 12px; margin-bottom: 15px; color: #333; }
    div.stButton > button[kind="primary"] { background-color: #1a2a44 !important; color: white !important; border: none !important; }
    div.stDownloadButton > button { background-color: #4682B4 !important; color: white !important; font-weight: 600 !important; }
    /* Limit the width of the chart container */
    .element-container img { max-width: 900px; margin: auto; }
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
    
    # --- CHART SIZE REDUCED ---
    # Changed from (15, 8.5) to (12, 7) to make it more compact
    fig, ax = plt.subplots(figsize=(12, 7), dpi=100) 
    
    try:
        # --- CALIBRATION SETTINGS ---
        # Adjust these slightly if the points don't hit the lines
        # Format: [Age_Start, Age_End, AXL_Bottom, AXL_Top]
        # Try changing 3.8 to 4.0 if points are too far left.
        x_min, x_max = 3.8, 18.2  
        y_min, y_max = 19.8, 28.2 
        
        extent = [x_min, x_max, y_min, y_max]
        
        ax.imshow(img_array, extent=extent, aspect='auto', interpolation='lanczos', origin='upper')
        
        # DISPLAY LIMITS: This is what you actually see
        ax.set_xlim(4, 18)
        ax.set_ylim(20.0, 28.0)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            l_vals = [v['Left'] for v in st.session_state.visits]
            r_vals = [v['Right'] for v in st.session_state.visits]
            
            ax.scatter(ages, l_vals, color='#008000', s=100, edgecolors='white', linewidth=1.2, zorder=10)
            ax.scatter(ages, r_vals, color='#FF0000', s=100, edgecolors='white', linewidth=1.2, zorder=10)

        # Legend & Formal Title
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left Eye (OS)', markerfacecolor='#008000', markersize=8),
            Line2D([0], [0], marker='o', color='w', label='Right Eye (OD)', markerfacecolor='#FF0000', markersize=8)
        ], loc='upper left', bbox_to_anchor=(0.15, 0.95), frameon=True, edgecolor='#1a2a44', fontsize='small')
        
        plt.title(f"AXIAL LENGTH GROWTH CHART: {name.upper()}", 
                  fontsize=16, fontfamily='serif', fontweight='bold', color='#1a2a44', pad=10)
        
        ax.axis('off')

        # Buffer for Export
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        buf.seek(0)
        
        # Center the chart in the UI
        _, col_mid, _ = st.columns([1, 6, 1])
        with col_mid:
            st.pyplot(fig, use_container_width=True)

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
