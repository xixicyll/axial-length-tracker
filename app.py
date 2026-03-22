import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd

st.set_page_config(page_title="Myopia Axial Tracker", layout="wide")

st.title("👁️ Axial Length History & Progression Tracker")

# --- Initialize Data Storage ---
if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- Sidebar: Patient Info & Visit Entry ---
with st.sidebar:
    st.header("1. Patient Information")
    name = st.text_input("Patient Name / ID", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    notes = st.text_area("Clinical Notes", "e.g., Started Ortho-K")
    
    st.divider()
    
    st.header("2. Add a Visit")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    col_os, col_od = st.columns(2)
    v_os = col_os.number_input("OS (mm)", 18.0, 32.0, 24.00)
    v_od = col_od.number_input("OD (mm)", 18.0, 32.0, 24.00)
    
    if st.button("➕ Add This Visit", type="primary"):
        st.session_state.visits.append({"Age": v_age, "OS": v_os, "OD": v_od})
        # Sort by age so the lines connect chronologically
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.rerun()

    if st.button("🗑️ Clear All Visits"):
        st.session_state.visits = []
        st.rerun()

# --- Calculations ---
growth_text = ""
if len(st.session_state.visits) >= 2:
    first, last = st.session_state.visits[0], st.session_state.visits[-1]
    years = last['Age'] - first['Age']
    if years > 0:
        os_rate = (last['OS'] - first['OS']) / years
        od_rate = (last['OD'] - first['OD']) / years
        growth_text = f"Progression Rate: OS {os_rate:.2f} mm/yr | OD {od_rate:.2f} mm/yr"

# --- Main Page: Plotting ---
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    fig, ax = plt.subplots(figsize=(12, 10))
    img = mpimg.imread(img_file)
    
    # Calibration Alignment
    ax.imshow(img, extent=[3.8, 18.2, 19.8, 28.2]) 
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        os_vals = [v['OS'] for v in st.session_state.visits]
        od_vals = [v['OD'] for v in st.session_state.visits]
        
        # Plot Lines
        ax.plot(ages, os_vals, color='green', linestyle='-', alpha=0.5, linewidth=2, zorder=5)
        ax.plot(ages, od_vals, color='red', linestyle='-', alpha=0.5, linewidth=2, zorder=5)
        
        # Plot Points
        ax.scatter(ages, os_vals, color='green', s=100, edgecolors='white', zorder=10)
        ax.scatter(ages, od_vals, color='red', s=100, edgecolors='white', zorder=10)

    # --- Simplified Legend (Color Only) ---
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Left Eye (OS)', markerfacecolor='blue', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Right Eye (OD)', markerfacecolor='red', markersize=10)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True)

    # Titles and Meta Data
    plt.title(f"Axial Length Progression: {name}", fontsize=18, fontweight='bold', pad=25)
    
    # Footer info (Notes + Growth Rate)
    footer_lines = []
    if growth_text: footer_lines.append(growth_text)
    if notes: footer_lines.append(f"Notes: {notes}")
    
    if footer_lines:
        plt.figtext(0.12, 0.03, "\n".join(footer_lines), fontsize=11, style='italic', wrap=True)
    
    ax.axis('off')
    st.pyplot(fig)
    
    # Download
    save_fn = f"AXL_Report_{name}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("📩 Download Professional Report", f, file_name=save_fn, mime="image/png")
else:
    st.error("Missing background chart images.")
