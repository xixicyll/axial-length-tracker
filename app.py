import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

st.set_page_config(page_title="Myopia Axial Tracker", layout="wide")

st.title("👁️ Axial Length Growth & Progression Tracker")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Patient Information")
    name = st.text_input("Patient Name / ID", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    notes = st.text_area("Clinical Notes", "e.g., Started 0.01% Atropine")
    
    st.divider()
    
    # Baseline Visit
    st.subheader("📍 Baseline Visit")
    age_1 = st.number_input("Age at Baseline", 4.0, 18.0, 8.0, 0.1)
    col_os1, col_od1 = st.columns(2)
    os_1 = col_os1.number_input("OS (mm) - Base", 18.0, 32.0, 23.50)
    od_1 = col_od1.number_input("OD (mm) - Base", 18.0, 32.0, 23.50)
    
    st.divider()
    
    # Follow-up Visit
    show_followup = st.checkbox("Add Follow-up Visit")
    if show_followup:
        st.subheader("📈 Follow-up Visit")
        age_2 = st.number_input("Age at Follow-up", 4.0, 18.0, 9.0, 0.1)
        col_os2, col_od2 = st.columns(2)
        os_2 = col_os2.number_input("OS (mm) - Follow", 18.0, 32.0, 24.00)
        od_2 = col_od2.number_input("OD (mm) - Follow", 18.0, 32.0, 24.00)

# --- Plotting Logic ---
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    img = mpimg.imread(img_file)
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # --- CALIBRATED ALIGNMENT ---
    # We use 3.8 to 18.2 (Age) and 19.8 to 28.2 (AXL) to 
    # compensate for the white borders in your .jfif files.
    ax.imshow(img, extent=[3.8, 18.2, 19.8, 28.2]) 
    
    # Plot Baseline Dots (Circles)
    ax.scatter(age_1, os_1, color='blue', s=120, marker='o', label='OS (Left) Baseline', edgecolors='white', linewidths=1.5, zorder=10)
    ax.scatter(age_1, od_1, color='red', s=120, marker='o', label='OD (Right) Baseline', edgecolors='white', linewidths=1.5, zorder=10)
    
    # Plot Follow-up (Crosses) and Trend Lines
    if show_followup:
        ax.scatter(age_2, os_2, color='blue', s=180, marker='X', label='OS Follow-up', edgecolors='white', linewidths=1, zorder=11)
        ax.scatter(age_2, od_2, color='red', s=180, marker='X', label='OD Follow-up', edgecolors='white', linewidths=1, zorder=11)
        
        # Dashed lines to visualize progression slope
        ax.plot([age_1, age_2], [os_1, os_2], color='blue', linestyle='--', alpha=0.7, linewidth=2, zorder=5)
        ax.plot([age_1, age_2], [od_1, od_2], color='red', linestyle='--', alpha=0.7, linewidth=2, zorder=5)

    # Titles and Notes
    plt.title(f"Axial Length Growth Chart: {name} ({gender})", fontsize=18, fontweight='bold', pad=25)
    plt.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, fontsize=11, facecolor='white', framealpha=0.9)
    
    # Add clinical notes and timestamps to the bottom
    if notes:
        plt.figtext(0.12, 0.05, f"Clinical Notes: {notes}", fontsize=12, style='italic', wrap=True, color='#333333')
    
    # Hide the plot axes (use the image's printed axes instead)
    ax.axis('off')
    
    # Display in App
    st.pyplot(fig)
    
    # Download Button
    save_fn = f"AXL_Report_{name}_{gender}.png"
    plt.savefig(save_fn, dpi=300, bbox_inches='tight')
    with open(save_fn, "rb") as f:
        st.download_button("📩 Download Professional Report (PNG)", f, file_name=save_fn, mime="image/png")
else:
    st.error(f"Image '{img_file}' not found. Please ensure the files are in your GitHub repo.")
