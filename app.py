import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import io
from matplotlib.lines import Line2D
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# --- RESTORED CLINICAL CSS ---
st.markdown("""
    <style>
    h1 {
        font-family: 'Times New Roman', serif;
        color: #1a2a44;
        border-bottom: 2px solid #1a2a44;
        padding-bottom: 10px;
    }
    .patient-bar {
        background-color: #f8f9fa;
        border-left: 5px solid #1a2a44;
        padding: 15px;
        margin-bottom: 20px;
        color: #333;
    }
    div.stButton > button[kind="primary"] {
        background-color: #1a2a44 !important;
        color: white !important;
        border: none !important;
    }
    div.stDownloadButton > button {
        background-color: #4682B4 !important;
        color: white !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_bg_image(file_path):
    if os.path.exists(file_path):
        return mpimg.imread(file_path)
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
st.title("👁️ Axial Length History Tracker")

# Restored Patient Info Bar
today = datetime.now().strftime("%d %b %Y")
st.markdown(f"""
    <div class="patient-bar">
        <strong>Patient:</strong> {name.upper()} &nbsp; | &nbsp; 
        <strong>Sex:</strong> {gender} &nbsp; | &nbsp; 
        <strong>Report Date:</strong> {today}
    </div>
    """, unsafe_allow_html=True)

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
img = load_bg_image(img_file)

if img is not None:
    plt.close('all')
    # Optimized figsize and DPI for speed-performance balance
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=90) 
    
    try:
        # 'nearest' interpolation for speed during real-time updates
        ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='nearest')
        ax.set_xlim(3.8, 20.0)
        ax.set_ylim(19.5, 28.5)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=130, edgecolors='white', linewidth=1.5, zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=130, edgecolors='white', linewidth=1.5, zorder=10)

        # Restored Formal Legend
        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left Eye (OS)', markerfacecolor='#008000', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Right Eye (OD)', markerfacecolor='#FF0000', markersize=10)
        ], loc='upper left', bbox_to_anchor=(0.18, 0.94), frameon=True, edgecolor='#1a2a44')
        
        # Restored Formal Chart Title
        plt.title(f"AXIAL LENGTH GROWTH CHART: {name.upper()}", 
                  fontsize=20, fontfamily='serif', fontweight='bold', color='#1a2a44', pad=15)
        ax.axis('off')

        # Buffer generation for the report
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=180, bbox_inches='tight')
        buf.seek(0)
        
        st.pyplot(fig, width='stretch', clear_figure=True)

        if st.session_state.visits:
            st.download_button(
                label="📥 EXPORT REPORT",
                data=buf,
                file_name=f"AXL_Report_{name.replace(' ', '_')}.png",
                mime="image/png",
                width='stretch'
            )

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Reference Image Missing: {img_file}")
