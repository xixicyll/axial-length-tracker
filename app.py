import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import os

st.set_page_config(page_title="AXL Clinical Tracker", layout="wide")

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- Sidebar ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Full Name", "Unnamed Patient")
    gender = st.selectbox("Biological Sex", ["Female", "Male"])
    st.divider()
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    v_left = st.number_input("OS (mm)", 18.0, 32.0, 24.00, 0.01)
    v_right = st.number_input("OD (mm)", 18.0, 32.0, 24.00, 0.01)
    
    if st.button("Update Record", type="primary", width="stretch"):
        st.session_state.visits.append({"Age": v_age, "OS": v_left, "OD": v_right})
        st.session_state.visits.sort(key=lambda x: x['Age'])
        st.rerun()

st.title("AXIAL LENGTH CLINICAL HISTORY")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    img = Image.open(img_file)
    fig = go.Figure()

    # --- THE ALIGNMENT FIX ---
    # We map the image edges precisely to the Age 4 and Age 18 lines.
    fig.add_layout_image(
        dict(
            source=img,
            xref="x", yref="y",
            x=3.6, y=28.5,        # Adjusted anchor to pull image left
            sizex=15.2, sizey=9.2, # Adjusted span to match Age 4-18
            sizing="stretch",
            opacity=1.0,
            layer="below"
        )
    )

    if st.session_state.visits:
        df = pd.DataFrame(st.session_state.visits)
        fig.add_trace(go.Scatter(
            x=df['Age'], y=df['OS'], name="OS (Left)", 
            mode='markers+lines', marker=dict(color='green', size=12, line=dict(width=2, color='white'))
        ))
        fig.add_trace(go.Scatter(
            x=df['Age'], y=df['OD'], name="OD (Right)", 
            mode='markers+lines', marker=dict(color='red', size=12, line=dict(width=2, color='white'))
        ))

    # --- THE VIEWPORT LOCK ---
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(
            title="Age (years)", 
            range=[4, 18],        # This removes the -7 to 29 empty space
            dtick=1, 
            showgrid=True, 
            gridcolor='lightgrey',
            fixedrange=True       # Prevents accidental zooming
        ),
        yaxis=dict(
            title="Axial Length (mm)", 
            range=[20, 28], 
            dtick=1, 
            showgrid=True, 
            gridcolor='lightgrey',
            fixedrange=True
        ),
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Image not found: {img_file}")

if st.button("Undo Last Entry"):
    if st.session_state.visits:
        st.session_state.visits.pop()
        st.rerun()
