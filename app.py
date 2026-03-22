import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import io
import pandas as pd
from matplotlib.lines import Line2D

# 1. Page Configuration
st.set_page_config(page_title="AXL Tracker Pro", layout="wide")

# CSS for tight layout
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 0rem;}
    h1 {margin-top: -10px; font-size: 2.2rem !important;}
    </style>
    """, unsafe_allow_html=True)

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 2. Sidebar: Patient Management ---
with st.sidebar:
    st.markdown("### 👤 Patient Profile")
    name = st.text_input("Name", "Unnamed", label_visibility="collapsed")
    gender = st.selectbox("Gender", ["Female", "Male"], label_visibility="collapsed")
    
    st.divider()
    st.markdown("### ➕ Add New Measurement")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    cl, cr = st.columns(2)
    v_left = cl.number_input("Left Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    v_right = cr.number_input("Right Eye (mm)", 18.0, 32.0, 24.00, step=0.01, format="%.2f")
    
    if st.button("Update Chart", type="primary", use_container_width=True):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    if st.button("Undo Last", use_container_width=True):
        if st.session_state.visits: 
            st.session_state.visits.pop()
            st.rerun()

# --- 3. Main Display Area ---
st.title("👁️ Axial Length History Tracker")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    # FAST PREVIEW: Lower DPI (80) for instant response
    fig, ax = plt.subplots(figsize=(12, 7), dpi=80) 
    img = mpimg.imread(img_file)
    
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='nearest') # 'nearest' is faster
    ax.set_xlim(3.8, 20.0)
    ax.set_ylim(19.5, 28.5)
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        l_vals = [v['Left'] for v in st.session_state.visits]
        r_vals = [v['Right'] for v in st.session_state.visits]
        ax.scatter(ages, l_vals, color='#008000', s=100, edgecolors='white', linewidth=1, zorder=10)
        ax.scatter(ages, r_vals, color='#FF0000', s=100, edgecolors='white', linewidth=1, zorder=10)

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left Eye (OS)', markerfacecolor='#008000', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Right Eye (OD)', markerfacecolor='#FF0000', markersize=8)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.18, 0.92), frameon=True, facecolor='white', framealpha=0.9)

    plt.title(f"Axial Length Growth Record: {name} ({gender})", fontsize=18, fontweight='bold', pad=10)
    ax.axis('off')
    
    # Display preview
    st.pyplot(fig, use_container_width=True, clear_figure=True)

    # --- 4. HIGH-RES GENERATION (Only on request) ---
    @st.fragment # Ensures this logic doesn't run unless needed
    def download_section():
        if st.button("Prepare High-Res Report 💾"):
            with st.spinner("Generating crisp image..."):
                # Re-create figure at high DPI only for the buffer
                fig_hr, ax_hr = plt.subplots(figsize=(15, 8.5), dpi=300)
                ax_hr.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos')
                if st.session_state.visits:
                    ax_hr.scatter(ages, l_vals, color='#008000', s=120, edgecolors='white', zorder=10)
                    ax_hr.scatter(ages, r_vals, color='#FF0000', s=120, edgecolors='white', zorder=10)
                
                ax_hr.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.18, 0.92), frameon=True)
                ax_hr.set_title(f"Axial Length Growth Record: {name} ({gender})", fontsize=22, fontweight='bold', pad=15)
                ax_hr.axis('off')
                
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                buf.seek(0)
                
                st.download_button(label="Click to Download PNG", data=buf, file_name=f"AXL_{name}.png", mime="image/png")

    download_section()

else:
    st.error(f"Missing background image: '{img_file}'")
