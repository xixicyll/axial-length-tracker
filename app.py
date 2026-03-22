import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import io
import pandas as pd
from matplotlib.lines import Line2D

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# CSS for a professional, tight UI
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 0rem;}
    h1 {margin-top: -10px; font-size: 2.2rem !important;}
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 2. Sidebar: Patient Management ---
with st.sidebar:
    st.markdown("### 👤 Patient Profile")
    name = st.text_input("Name", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    
    st.divider()
    st.markdown("### ➕ Add New Measurement")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    
    cl, cr = st.columns(2)
    v_left = cl.number_input("Left Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    v_right = cr.number_input("Right Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    
    if st.button("Update Chart", type="primary", width='stretch'):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits.sort(key=lambda x: x['Age'])
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("Undo Last", width='stretch'):
        if st.session_state.visits: 
            st.session_state.visits.pop()
            st.rerun()
            
    if c2.button("Clear All", width='stretch'):
        st.session_state.visits = []
        st.rerun()

# --- 3. Main Display Area ---
st.title("👁️ Axial Length History Tracker")

# DIAGNOSTIC: Show data table even if chart fails
if st.session_state.visits:
    with st.expander("📋 View Measurement Log", expanded=False):
        st.table(pd.DataFrame(st.session_state.visits))

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

# Check if image exists and notify the user
if not os.path.exists(img_file):
    st.warning(f"⚠️ **File Not Found:** App is looking for `{img_file}`. Please ensure this file is in your GitHub root folder.")
    st.info("Files currently detected in directory: " + str(os.listdir('.')))
else:
    # Use a fresh figure for every run
    plt.close('all')
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=100) 
    
    try:
        img = mpimg.imread(img_file)
        ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos')
        ax.set_xlim(3.8, 20.0)
        ax.set_ylim(19.5, 28.5)
        
        if st.session_state.visits:
            ages = [v['Age'] for v in st.session_state.visits]
            l_vals = [v['Left'] for v in st.session_state.visits]
            r_vals = [v['Right'] for v in st.session_state.visits]
            
            ax.scatter(ages, l_vals, color='#008000', s=100, edgecolors='white', linewidth=1.2, zorder=10)
            ax.scatter(ages, r_vals, color='#FF0000', s=100, edgecolors='white', linewidth=1.2, zorder=10)

        # Legend & Title
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Left Eye (OS)', markerfacecolor='#008000', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Right Eye (OD)', markerfacecolor='#FF0000', markersize=10)
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.18, 0.92), 
                  frameon=True, facecolor='white', framealpha=0.9, fontsize=12)

        plt.title(f"Axial Length Growth Record: {name} ({gender})", fontsize=22, fontweight='bold', pad=10)
        ax.axis('off')
        
        # 2026 Syntax
        st.pyplot(fig, width='stretch', clear_figure=True)

        # Download Buffer
        if st.session_state.visits:
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=300, bbox_inches='tight', pad_inches=0.1)
            buf.seek(0)
            st.download_button(label="💾 Download PNG", data=buf, file_name=f"AXL_{name}.png", mime="image/png")
            
    except Exception as e:
        st.error(f"❌ **Plotting Error:** {e}")
    finally:
        plt.close(fig)
