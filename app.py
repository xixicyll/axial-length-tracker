import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import os
from datetime import datetime

# 1. Setup
st.set_page_config(page_title="AXL Clinical Tracker", layout="wide")

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- Sidebar ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Name", "Unnamed Patient")
    gender = st.selectbox("Sex", ["Female", "Male"])
    st.divider()
    st.subheader("➕ Add Measurement")
    v_age = st.number_input("Age", 4.0, 18.0, 9.0, 0.1)
    v_left = st.number_input("OS (mm)", 18.0, 32.0, 24.00, 0.01)
    v_right = st.number_input("OD (mm)", 18.0, 32.0, 24.00, 0.01)
    
    if st.button("Update Chart", type="primary"):
        st.session_state.visits.append({"Age": v_age, "Left": v_left, "Right": v_right})
        st.rerun()

# --- Main Logic ---
st.title("AXIAL LENGTH GROWTH HISTORY")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    img = Image.open(img_file)
    
    # Create the Plotly Figure
    fig = go.Figure()

    # --- THE "BETTER WAY" ALIGNMENT ---
    # These numbers lock the image to the grid coordinates. 
    # Adjusting x0 from 4 to 3.4 pulls the "9" line under the 9.0 data point.
    fig.add_layout_image(
        dict(
            source=img,
            xref="x", yref="y",
            x=3.4, y=28.5, # Top-left anchor
            sizex=16.2, sizey=9.0, # Total span of the image
            sizing="stretch",
            opacity=1.0,
            layer="below"
        )
    )

    # Add Data Points
    if st.session_state.visits:
        ages = [v['Age'] for v in st.session_state.visits]
        fig.add_trace(go.Scatter(
            x=ages, y=[v['Left'] for v in st.session_state.visits],
            name="Left (OS)", mode='markers',
            marker=dict(color='green', size=12, line=dict(color='white', width=2))
        ))
        fig.add_trace(go.Scatter(
            x=ages, y=[v['Right'] for v in st.session_state.visits],
            name="Right (OD)", mode='markers',
            marker=dict(color='red', size=12, line=dict(color='white', width=2))
        ))

    # Clean up the layout
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(range=[4, 18], title="Age (years)", showgrid=False),
        yaxis=dict(range=[20, 28], title="Axial Length (mm)", showgrid=False),
        margin=dict(l=20, r=20, t=50, b=20),
        height=600,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)")
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Please ensure {img_file} is in the folder.")

if st.button("Clear Last Entry"):
    if st.session_state.visits:
        st.session_state.visits.pop()
        st.rerun()
