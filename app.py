import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="AXL Clinical Dashboard", layout="wide")

# --- Clinical Percentile Data (Simplified Example) ---
# In a real tool, these would be the exact values from the research papers
def get_percentile_data(age_range):
    # This represents the 50th percentile (average) growth curve
    return 21.5 + 0.8 * np.log(age_range - 2.5)

age_axis = np.linspace(4, 18, 100)
p50_curve = get_percentile_data(age_axis)
p95_curve = p50_curve + 1.2  # High risk
p5_curve = p50_curve - 1.0   # Low risk

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- Sidebar ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Name", "Unnamed Patient")
    st.divider()
    v_age = st.number_input("Age", 4.0, 18.0, 9.0, 0.1)
    v_os = st.number_input("OS (mm)", 18.0, 32.0, 24.00, 0.01)
    v_od = st.number_input("OD (mm)", 18.0, 32.0, 24.00, 0.01)
    
    if st.button("Add to Record", type="primary", width="stretch"):
        st.session_state.visits.append({"Age": v_age, "OS": v_os, "OD": v_od})
        st.rerun()

st.title("AXIAL LENGTH GROWTH ANALYSIS")

# --- The Digital Chart ---
fig = go.Figure()

# 1. Add Reference Percentiles (The "Background" but digital)
fig.add_trace(go.Scatter(x=age_axis, y=p95_curve, name="95th (High Risk)", 
                         line=dict(color='rgba(255,0,0,0.2)', width=1, dash='dash')))
fig.add_trace(go.Scatter(x=age_axis, y=p50_curve, name="50th (Average)", 
                         line=dict(color='rgba(0,0,0,0.3)', width=2)))
fig.add_trace(go.Scatter(x=age_axis, y=p5_curve, name="5th (Low Risk)", 
                         line=dict(color='rgba(0,0,255,0.2)', width=1, dash='dash')))

# 2. Add Patient Data
if st.session_state.visits:
    df = pd.DataFrame(st.session_state.visits)
    fig.add_trace(go.Scatter(x=df['Age'], y=df['OS'], name="OS (Left)", 
                             mode='markers+lines', marker=dict(color='green', size=12)))
    fig.add_trace(go.Scatter(x=df['Age'], y=df['OD'], name="OD (Right)", 
                             mode='markers+lines', marker=dict(color='red', size=12)))

fig.update_layout(
    template="plotly_white",
    xaxis=dict(title="Age (years)", range=[4, 18], dtick=1, showgrid=True),
    yaxis=dict(title="Axial Length (mm)", range=[20, 28], dtick=1, showgrid=True),
    height=600,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

if st.button("Undo Last"):
    if st.session_state.visits:
        st.session_state.visits.pop()
        st.rerun()
