import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import os

# 1. Dashboard Configuration
st.set_page_config(page_title="AXL Clinical Tracker", layout="wide")

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- Sidebar ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Full Name", "Unnamed Patient")
    gender = st.selectbox("Biological Sex", ["Female", "Male"])
    st.divider()
    st.subheader("➕ New Entry")
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    cl, cr = st.columns(2)
    v_left = cl.number_input("OS (mm)", 18.0, 32.0, 24.00, 0.01)
    v_right = cr.number_input("OD (mm)", 18.0, 32.0, 24.00, 0.01)
    
    if st.button("Update Clinical Record", type="primary", width="stretch"):
        st.session_state.visits.append({
            "Age": v_age, "OS (Left)": v_left, "OD (Right)": v_right
        })
        st.session_state.visits.sort(key=lambda x: x['Age'])
        st.rerun()

# --- Main Layout ---
st.title("AXIAL LENGTH GROWTH HISTORY")

img_file = "AXL female.jfif" if gender == "Female" else "AXL male.jfif"

if os.path.exists(img_file):
    img = Image.open(img_file)
    
    fig = go.Figure()

    # --- NO-DISTORTION ALIGNMENT ---
    # We map the image to a slightly wider range to show the labels properly
    fig.add_layout_image(
        dict(
            source=img,
            xref="x", yref="y",
            x=3.15, y=28.8, # Precise anchor based on your 9:52 PM screenshot
            sizex=16.8, sizey=9.8,
            sizing="contain", # PREVENTS DISTORTION
            opacity=0.8,
            layer="below"
        )
    )

    # Add Data Points with high-contrast clinical colors
    if st.session_state.visits:
        df = pd.DataFrame(st.session_state.visits)
        fig.add_trace(go.Scatter(
            x=df['Age'], y=df['OS (Left)'],
            name="Left Eye (OS)", mode='markers+lines',
            marker=dict(color='#008000', size=14, symbol='circle', line=dict(color='white', width=2)),
            line=dict(color='#008000', width=1, dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=df['Age'], y=df['OD (Right)'],
            name="Right Eye (OD)", mode='markers+lines',
            marker=dict(color='#FF0000', size=14, symbol='x', line=dict(color='white', width=2)),
            line=dict(color='#FF0000', width=1, dash='dot')
        ))

    # Professional Axis Setup
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(
            title="Age (years)", range=[3.8, 18.2], 
            dtick=1, showgrid=True, gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title="Axial Length (mm)", range=[19.8, 28.2], 
            dtick=1, showgrid=True, gridcolor='rgba(0,0,0,0.1)'
        ),
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Patient Data Table ---
    if st.session_state.visits:
        st.subheader("📊 Measurement Log")
        st.table(pd.DataFrame(st.session_state.visits))
        
        if st.button("Clear Last Entry"):
            st.session_state.visits.pop()
            st.rerun()
else:
    st.error(f"Image not found: {img_file}. Please check the filename.")
