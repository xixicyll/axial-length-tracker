import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd
from matplotlib.lines import Line2D

st.set_page_config(page_title="Myopia Axial Tracker", layout="wide")

st.title("👁️ Axial Length History Tracker")

# --- Initialize Data Storage ---
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- Sidebar: Patient Info & Visit Entry ---
with st.sidebar:
    st.header("1. Patient Information")
    name = st.text_input("Patient Name / ID", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    notes = st.text_area("Clinical Notes", "")
    
    st.divider()
    
    st.header("2. Add a Visit")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    col_left, col_right = st.columns(2)
    v_left = col_left.number_input("Left eye (mm)", 18.0, 32.0, 24.00)
    v_right = col_right.number_input("Right eye (mm)", 18.0, 32.0, 24.00)
    
    if st.button("➕ Add This Visit", type="primary"):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    col_del1, col_del2 = st.columns(2)
    if col_del1.button("🔙 Undo Last"):
        if st.session_state.visits:
            st.session_state.visits.pop()
            st.rerun()
    if col_del2.button("🗑️ Clear All"):
        st.session_state.visits = []
        st.rerun()

# --- Main Page: Plotting ---
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    # Higher DPI for the figure to help with low-res backgrounds
    fig, ax = plt.subplots(figsize=(12, 10), dpi=100)
    img = mpimg.imread(img_file)
    
    # 1. THE "ZOOM OUT" ADJUSTMENT
    # We set the extent to match the actual grid: 4 to 18 years, 20 to 28 mm.
    # We then set the axis limits wider than the image to create "white space" 
    # which makes the low-res image look like a clean inset.
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto', interpolation='lanczos') 
    
    # Set limits slightly wider than the image to "Zoom Out"
    ax.set_xlim(3.5, 18.5)
    ax.set_ylim(19.5, 28.5)
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        left_vals = [v['Left'] for v in st.session_state.visits]
        right_vals = [v['Right'] for v in st.session_state.visits]
        
        # Plot Points
        ax.scatter(ages, left_vals, color='#008000', s=50, edgecolors='white', linewidths=0.5, zorder=10)
        ax.scatter(ages, right_vals, color='#FF0000', s=50, edgecolors='white', linewidths=0.5, zorder=10)

    # --- Re-positioned Legend ---
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left eye', markerfacecolor='#008000', markersize=7),
        Line2D([0], [0], marker='o', color='w', label='Right eye', markerfacecolor='#FF0000', markersize=7)
    ]
    
    # Placed in a safe "white space" corner
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.05, 0.98), 
              frameon=True, fontsize=9, facecolor='white', framealpha=0.8)

    plt.title(f"Axial Length Progression: {name} ({gender})", fontsize=16, fontweight='bold', pad=20)
    
    if notes:
        plt.figtext(0.12, 0.04, f"Notes: {notes}", fontsize=10, style='italic', wrap=True)
    
    # We keep the axis 'off' to hide the computer-generated scale 
    # and rely on the chart's own scale.
    ax.axis('off')
    st.pyplot(fig)
    
    # --- HIGH RES EXPORT ---
    save_fn = f"AXL_Report_{name}.png"
    # Exporting at 400 DPI helps the final PNG look professional
    plt.savefig(save_fn, dpi=400, bbox_inches='tight')
    
    with open(save_fn, "rb") as f:
        st.download_button("📩 Download High-Res Report", f, file_name=save_fn, mime="image/png")
else:
    st.error("Chart images not found.")
