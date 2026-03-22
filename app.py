import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

st.set_page_config(page_title="Axial Length Tracker", layout="centered")

st.title("👁️ Axial Length Growth Tracker")
st.info("Input patient data on the left to plot on the growth chart.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Patient Data")
    name = st.text_input("Patient Name / ID", "Unnamed")
    gender = st.selectbox("Gender", ["Female", "Male"])
    age = st.slider("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    
    col1, col2 = st.columns(2)
    with col1:
        os_axl = st.number_input("Left (OS) mm", 18.0, 32.0, 23.50)
    with col2:
        od_axl = st.number_input("Right (OD) mm", 18.0, 32.0, 23.50)
    
    submit = st.button("Generate Report", type="primary")

# --- Plotting Logic ---
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    img = mpimg.imread(img_file)
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Map coordinates (Adjust 28 to match your specific chart's max Y-axis)
    ax.imshow(img, extent=[4, 18, 20, 28]) 
    
    # Add the patient dots
    ax.scatter(age, os_axl, color='#1f77b4', s=150, label=f'OS: {os_axl}mm', edgecolors='white', zorder=5)
    ax.scatter(age, od_axl, color='#d62728', s=150, label=f'OD: {od_axl}mm', edgecolors='white', zorder=5)
    
    ax.set_title(f"Axial Length Growth Chart: {name}", fontsize=14)
    ax.legend(loc='upper left', frameon=True)
    ax.axis('off')
    
    # Show plot
    st.pyplot(fig)
    
    # Download Button
    fn = f"AXL_{name}_{gender}.png"
    plt.savefig(fn, dpi=300, bbox_inches='tight')
    with open(fn, "rb") as img_file:
        st.download_button("📩 Download PNG for Records", img_file, file_name=fn, mime="image/png")
else:
    st.error(f"Missing file: {img_file}. Please ensure it is uploaded to the repository.")
