import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import io
from matplotlib.lines import Line2D

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# Clinical CSS (Simplified for speed)
st.markdown("""
    <style>
    h1 { font-family: serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; }
    div.stButton > button[kind="primary"] { background-color: #1a2a44 !important; color: white !important; }
    div.stDownloadButton > button { background-color: #4682B4 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CACHING: Keep image in RAM
@st.cache_data
def get_bg_image(file_path):
    if os.path.exists(file_path):
        return mpimg.imread(file_path)
    return None

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 3. Sidebar ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Full Name", "Unnamed Patient")
    gender = st.selectbox("Biological Sex", ["Female", "Male"])
    st.divider()
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    cl, cr = st.columns(2)
    v_left = cl.number_input("OS (mm)", 18.0, 32.0, 24.00, step=0.01)
    v_right = cr.number_input("OD (mm)", 18.0, 32.0, 24.00, step=0.01)
    
    if st.button("Update Record", type="primary", width='stretch'):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits.sort(key=lambda x: x['Age'])
        st.rerun()

# --- 4. Main Display ---
st.title("AXIAL LENGTH CLINICAL HISTORY")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
img = get_bg_image(img_file)

if img is not None:
    # SPEED OPTIMIZATION: Close all figures immediately
    plt.close('all')
    
    # Using a smaller figsize for the screen to speed up the rasterization
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=80) 
    
    try:
        # 'nearest' interpolation is the absolute fastest way to draw an image
        ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='nearest')
        ax.set_xlim(3.8, 20.0)
        ax.set_ylim(19.5, 28.5)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            # Batch plotting: Scatter is faster than Plot
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=80, edgecolors='white', zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=80, edgecolors='white', zorder=10)

        # Basic legend - heavy styling removed for speed
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left OS', markerfacecolor='#008000'),
            Line2D([0], [0], marker='o', color='w', label='Right OD', markerfacecolor='#FF0000')
        ], loc='upper left', bbox_to_anchor=(0.18, 0.94), frameon=True)
        
        plt.title(f"PATIENT: {name.upper()}", loc='left', fontsize=12, fontweight='bold')
        ax.axis('off')

        # Buffer for the download (Done once per rerun)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150) # Reduced DPI for faster buffer creation
        buf.seek(0)
        
        # Display
        st.pyplot(fig, width='stretch', clear_figure=True)

        if st.session_state.visits:
            st.download_button("📥 DOWNLOAD REPORT", buf, f"AXL_{name}.png", "image/png")

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Image Missing: {img_file}")
