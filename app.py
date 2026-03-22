import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import io
from matplotlib.lines import Line2D

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# 2. CACHING: Instant background loading
@st.cache_data
def load_bg_image(file_path):
    if os.path.exists(file_path):
        return mpimg.imread(file_path)
    return None

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 2. Sidebar: Patient Management ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Name", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    
    st.divider()
    st.subheader("➕ Add New Measurement")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    
    cl, cr = st.columns(2)
    v_left = cl.number_input("Left (mm)", 18.0, 32.0, 24.00, step=0.01)
    v_right = cr.number_input("Right (mm)", 18.0, 32.0, 24.00, step=0.01)
    
    if st.button("Update Chart", type="primary", width='stretch'):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits.sort(key=lambda x: x['Age'])
        st.rerun()

    if st.button("Undo Last", width='stretch'):
        if st.session_state.visits: 
            st.session_state.visits.pop()
            st.rerun()

# --- 3. Main Display Area ---
st.title("👁️ Axial Length History Tracker")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"
img = load_bg_image(img_file)

if img is not None:
    plt.close('all')
    # Use a consistent figure size for both screen and save
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=100)
    
    try:
        ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos')
        ax.set_xlim(3.8, 20.0)
        ax.set_ylim(19.5, 28.5)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            l_vals = [v['Left'] for v in st.session_state.visits]
            r_vals = [v['Right'] for v in st.session_state.visits]
            
            ax.scatter(ages, l_vals, color='#008000', s=120, edgecolors='white', linewidth=1.5, zorder=10)
            ax.scatter(ages, r_vals, color='#FF0000', s=120, edgecolors='white', linewidth=1.5, zorder=10)

        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Left OS', markerfacecolor='#008000', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Right OD', markerfacecolor='#FF0000', markersize=10)
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.18, 0.92), frameon=True)
        plt.title(f"Axial Length Growth Record: {name} ({gender})", fontsize=22, fontweight='bold', pad=10)
        ax.axis('off')

        # --- CRITICAL FIX: Save to buffer BEFORE displaying with st.pyplot ---
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=200, bbox_inches='tight')
        buf.seek(0)
        
        # Now display to the web app
        st.pyplot(fig, width='stretch', clear_figure=True)

        if st.session_state.visits:
            st.download_button(
                label="💾 Download Report (.png)",
                data=buf,
                file_name=f"AXL_Report_{name}.png",
                mime="image/png",
                width='stretch'
            )

    finally:
        plt.close(fig)
else:
    st.error(f"⚠️ Missing {img_file}")
