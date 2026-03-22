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
    notes = st.text_area("Clinical Notes", "e.g., Started Ortho-K at age 9")
    
    st.divider()
    
    st.header("2. Add a Visit")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    col_os, col_od = st.columns(2)
    v_os = col_os.number_input("OS (mm)", 18.0, 32.0, 24.00)
    v_od = col_od.number_input("OD (mm)", 18.0, 32.0, 24.00)
    
    if st.button("➕ Add This Visit", type="primary"):
        # Store the visit and sort by age automatically
        st.session_state.visits.append({"Age": v_age, "OS": v_os, "OD": v_od})
        st.session_state.visits = sorted(st.session_state.visits, key=lambda x: x['Age'])
        st.success(f"Added visit for age {v_age}")

    if st.button("🗑️ Clear All Visits"):
        st.session_state.visits = []
        st.rerun()

# --- Main Page: Data Table & Plot ---
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    # Display the table of visits for the doctor to review
    if st.session_state.visits:
        with st.expander("View Visit Data Table"):
            df = pd.DataFrame(st.session_state.visits)
            st.table(df)

    # Plotting
    img = mpimg.imread(img_file)
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Calibration Alignment
    ax.imshow(img, extent=[3.8, 18.2, 19.8, 28.2]) 
    
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        os_vals = [v['OS'] for v in st.session_state.visits]
        od_vals = [v['OD'] for v in st.session_state.visits]
        
        # Plot lines connecting all visits
        ax.plot(ages, os_vals, color='blue', linestyle='--', alpha=0.6, linewidth=2, zorder=5)
        ax.plot(ages, od_vals, color='red', linestyle='--', alpha=0.6, linewidth=2, zorder=5)
        
        # Plot points (The latest visit is a star, previous ones are circles)
        ax.scatter(ages[:-1], os_vals[:-1], color='blue', s=100, marker='o', edgecolors='white', zorder=10, label='OS History')
        ax.scatter(ages[:-1], od_vals[:-1], color='red', s=100, marker='o', edgecolors='white', zorder=10, label='OD History')
        
        # Highlight current/latest visit
        ax.scatter(ages[-1], os_vals[-1], color='blue', s=250, marker='*', edgecolors='yellow', zorder=11, label='OS Latest')
        ax.scatter(ages[-1], od_vals[-1], color='red', s=250, marker='*', edgecolors='yellow', zorder=11, label='OD Latest')

    # Formatting
    plt.title(f"Axial Length Progression: {name} ({gender})", fontsize=18, fontweight='bold', pad=25)
    plt.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, fontsize=10)
    
    if notes:
        plt.figtext(0.12, 0.05, f"Clinical Notes: {notes}", fontsize=12, style='italic', wrap=True)
    
    ax.axis('off')
    st.pyplot(fig)
    
    # Download
    save_fn = f"AXL_Full_Report_{name}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("📩 Download Full History Report", f, file_name=save_fn, mime="image/png")
else:
    st.error("Chart images not found.")
