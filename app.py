import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import pandas as pd

# 1. Simple Header
st.title("👁️ Axial Length Tracker (Debug Mode)")

# 2. Initialize Data
if 'visits' not in st.session_state:
    st.session_state.visits = []

# 3. Simple Sidebar
with st.sidebar:
    st.header("Add Data")
    name = st.text_input("Name", "Patient")
    gender = st.selectbox("Gender", ["Female", "Male"])
    age = st.number_input("Age", 4.0, 18.0, 9.0)
    left = st.number_input("Left Eye", 18.0, 30.0, 24.0)
    right = st.number_input("Right Eye", 18.0, 30.0, 24.0)
    
    if st.button("Update"):
        st.session_state.visits.append({"Age": age, "Left": left, "Right": right})
        st.rerun()

# 4. Diagnostic Info (This will show even if the chart fails)
st.write("### Current Directory Files:")
st.write(os.listdir('.'))

st.write("### Measurement Data:")
st.write(st.session_state.visits)

# 5. Simple Plotting
img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    st.success(f"Found {img_file}! Attempting to draw...")
    
    fig, ax = plt.subplots()
    img = mpimg.imread(img_file)
    ax.imshow(img, extent=[4, 18, 20, 28], aspect='auto')
    
    if st.session_state.visits:
        df = pd.DataFrame(st.session_state.visits)
        ax.scatter(df['Age'], df['Left'], color='green', label='Left')
        ax.scatter(df['Age'], df['Right'], color='red', label='Right')
    
    st.pyplot(fig, width='stretch')
else:
    st.error(f"Cannot find {img_file}. Please check your GitHub file names.")
