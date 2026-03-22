import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import io
from matplotlib.lines import Line2D
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# Optimized CSS (Clinical Blue Palette)
st.markdown("""
    <style>
    h1 { font-family: 'Times New Roman', serif; color: #1a2a44; border-bottom: 2px solid #1a2a44; }
    .patient-bar { background-color: #f8f9fa; border-left: 5px solid #1a2a44; padding: 12px; margin-bottom: 15px; }
    div.stButton > button[kind="primary"] { background-color: #1a2a44 !important; color: white !important; }
    div.stDownloadButton > button { background-color: #4682B4 !important; color: white !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. CACHING: This is the #1 speed boost. We load the image into RAM once.
@st.cache_data
def get_bg_image(file_path):
    if os.path.exists(file_path):
        return mpimg.imread(file_path)
    return None

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 3. Sidebar: Fast Input ---
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

# --- 4. Main Display & Rendering Logic ---
st.title("AXIAL LENGTH CLINICAL HISTORY")

st.markdown(f"""<div class="patient-bar"><strong>Patient:</strong> {name.upper()} &nbsp; | &nbsp; 
<strong>Date:</strong> {datetime.now().strftime("%d %b %Y")}</div>""", unsafe_allow_html=True)

# 5. FRAGMENTED RENDERING: Only redraw the chart area
@st.fragment
def render_chart(gender, name):
    img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
    img = get_bg_image(img_file)
    
    if img is not None:
        # Optimization: Use lower DPI for the screen preview (Instant response)
        plt.close('all')
        fig, ax = plt.subplots(figsize=(12, 6.5), dpi=85) 
        
        ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='nearest') # 'nearest' is faster
        ax.set_xlim(3.8, 20.0)
        ax.set_ylim(19.5, 28.5)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            ax.scatter(ages, [v['Left'] for v in st.session_state.visits], color='#008000', s=100, edgecolors='white', zorder=10)
            ax.scatter(ages, [v['Right'] for v in st.session_state.visits], color='#FF0000', s=100, edgecolors='white', zorder=10)

        ax.legend(handles=[
            Line2D([0], [0], marker='o', color='w', label='Left OS', markerfacecolor='#008000', markersize=9),
            Line2D([0], [0], marker='o', color='w', label='Right OD', markerfacecolor='#FF0000', markersize=9)
        ], loc='upper left', bbox_to_anchor=(0.18, 0.94), frameon=True)
        
        plt.title(f"AXIAL LENGTH GROWTH: {name.upper()}", fontsize=16, fontfamily='serif', color='#1a2a44')
        ax.axis('off')

        # Display preview
        st.pyplot(fig, width='stretch', clear_figure=True)

        # Download Logic (Isolated so it doesn't slow down the preview)
        if st.session_state.visits:
            with st.expander("📝 Prepare Export"):
                if st.button("Finalize PNG"):
                    buf = io.BytesIO()
                    # Only now do we do the slow, high-quality 300 DPI render
                    fig.set_dpi(300) 
                    fig.savefig(buf, format="png", bbox_inches='tight')
                    st.download_button("📥 DOWNLOAD REPORT", buf, f"AXL_{name}.png", "image/png")
    else:
        st.error(f"Missing background image: {img_file}")

render_chart(gender, name)
