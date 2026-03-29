import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="AXL Clinical Tracker", layout="wide")

if 'visits' not in st.session_state:
    st.session_state.visits = []

# --- 2. DATA TABLES ---
MALE_DATA = {
    "Age": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    "3":   [21.26, 21.49, 21.71, 21.91, 22.09, 22.27, 22.42, 22.56, 22.68, 22.78, 22.86, 22.91, 22.94, 22.95, 22.92],
    "5":   [21.41, 21.64, 21.86, 22.07, 22.26, 22.44, 22.60, 22.75, 22.88, 22.99, 23.08, 23.15, 23.20, 23.23, 23.22],
    "10":  [21.63, 21.87, 22.10, 22.32, 22.53, 22.72, 22.89, 23.05, 23.20, 23.33, 23.44, 23.53, 23.60, 23.66, 23.69],
    "25":  [21.99, 22.26, 22.51, 22.75, 22.98, 23.19, 23.40, 23.58, 23.76, 23.92, 24.06, 24.19, 24.31, 24.41, 24.50],
    "50":  [22.39, 22.69, 22.97, 23.25, 23.51, 23.76, 23.99, 24.22, 24.43, 24.62, 24.81, 24.98, 25.13, 25.28, 25.41],
    "75":  [22.78, 23.12, 23.45, 23.76, 24.07, 24.36, 24.64, 24.90, 25.15, 25.39, 25.61, 25.82, 26.01, 26.18, 26.35],
    "90":  [23.13, 23.51, 23.88, 24.24, 24.60, 24.93, 25.26, 25.57, 25.86, 26.14, 26.39, 26.63, 26.84, 27.04, 27.21],
    "95":  [23.33, 23.74, 24.15, 24.54, 24.92, 25.30, 25.65, 25.99, 26.31, 26.61, 26.89, 27.14, 27.36, 27.56, 27.74]
}

FEMALE_DATA = {
    "Age": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    "3":   [20.74, 20.96, 21.17, 21.37, 21.56, 21.73, 21.89, 22.04, 22.18, 22.29, 22.40, 22.48, 22.55, 22.59, 22.61],
    "5":   [20.87, 21.11, 21.33, 21.53, 21.73, 21.92, 22.09, 22.25, 22.39, 22.53, 22.64, 22.74, 22.82, 22.89, 22.93],
    "10":  [21.08, 21.33, 21.56, 21.79, 22.00, 22.21, 22.40, 22.57, 22.73, 22.88, 23.02, 23.14, 23.24, 23.33, 23.41],
    "25":  [21.41, 21.69, 21.96, 22.22, 22.46, 22.70, 22.92, 23.12, 23.31, 23.49, 23.66, 23.81, 23.95, 24.08, 24.19],
    "50":  [21.78, 22.10, 22.41, 22.70, 22.98, 23.25, 23.51, 23.75, 23.97, 24.19, 24.39, 24.57, 24.75, 24.91, 25.05],
    "75":  [22.14, 22.50, 22.85, 23.19, 23.51, 23.82, 24.11, 24.39, 24.65, 24.90, 25.13, 25.34, 25.54, 25.73, 25.89],
    "90":  [22.46, 22.87, 23.26, 23.63, 23.99, 24.34, 24.67, 24.98, 25.28, 25.55, 25.81, 26.05, 26.27, 26.46, 26.64],
    "95":  [22.66, 23.08, 23.50, 23.90, 24.28, 24.65, 25.01, 25.34, 25.66, 25.95, 26.22, 26.47, 26.70, 26.90, 27.08]
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("👤 Patient Profile")
    name = st.text_input("Name", "Unnamed Patient")
    gender = st.selectbox("Biological Sex", ["Female", "Male"])
    st.divider()
    v_age = st.number_input("Age (Years)", 4.0, 18.0, 9.0, 0.1)
    v_os = st.number_input("OS (mm)", 18.0, 32.0, 24.00, 0.01)
    v_od = st.number_input("OD (mm)", 18.0, 32.0, 24.00, 0.01)
    
    if st.button("Update Record", type="primary", use_container_width=True):
        st.session_state.visits.append({"Age": v_age, "OS": v_os, "OD": v_od})
        st.session_state.visits.sort(key=lambda x: x['Age'])
        st.rerun()

# --- 4. PLOT CONSTRUCTION ---
st.title(f"AXIAL LENGTH GROWTH CHART: {name.upper()}")

data_source = FEMALE_DATA if gender == "Female" else MALE_DATA
fig = go.Figure()

MARKER_MAP = {
    "3":  {"symbol": "circle", "dash": "solid"},
    "5":  {"symbol": "triangle-up", "dash": "solid"},
    "10": {"symbol": "square-open", "dash": "solid"},
    "25": {"symbol": "square", "dash": "solid"},
    "50": {"symbol": None, "dash": "dash"}, 
    "75": {"symbol": "triangle-up-open", "dash": "solid"},
    "90": {"symbol": "x", "dash": "solid"},
    "95": {"symbol": "diamond-open", "dash": "solid"}
}

# Percentile Lines: Decoupling Legend Width from Chart Width
for p in ["3", "5", "10", "25", "50", "75", "90", "95"]:
    style = MARKER_MAP[p]
    is_median = (p == "50")
    
    # Trace for the CHART (No Legend)
    fig.add_trace(go.Scatter(
        x=data_source["Age"], y=data_source[p],
        mode='lines+markers' if style["symbol"] else 'lines',
        marker=dict(symbol=style["symbol"], size=7, color="black"),
        line=dict(color="black" if is_median else "#777777", width=1.5, dash=style["dash"]),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Trace for the LEGEND ONLY (No Data)
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        name=p,
        mode='lines+markers' if style["symbol"] else 'lines',
        marker=dict(symbol=style["symbol"], size=8, color="black"),
        line=dict(color="black", width=0.5, dash=style["dash"]), # Hairline width for legend
        showlegend=True
    ))

# Patient Measurements
if st.session_state.visits:
    df = pd.DataFrame(st.session_state.visits)
    fig.add_trace(go.Scatter(x=df['Age'], y=df['OS'], mode='markers+lines', 
                             marker=dict(color='green', size=11), line=dict(width=2.5), showlegend=False))
    fig.add_trace(go.Scatter(x=df['Age'], y=df['OD'], mode='markers+lines', 
                             marker=dict(color='red', size=11), line=dict(width=2.5), showlegend=False))

# --- 5. BORDER & HORIZONTAL LEGEND ---
fig.update_layout(
    template="plotly_white",
    xaxis=dict(
        title="<b>Age (years)</b>", range=[4, 18], dtick=1, 
        showgrid=True, gridcolor='lightgrey',
        showline=True, linewidth=2, linecolor='black', mirror=True # Boxed Border
    ),
    yaxis=dict(
        title=f"<b>Axial length (mm) - {gender}s</b>", range=[20, 28], dtick=1, 
        showgrid=True, gridcolor='lightgrey',
        showline=True, linewidth=2, linecolor='black', mirror=True # Boxed Border
    ),
    height=800,
    legend=dict(
        orientation="h",
        yanchor="top", y=-0.12, 
        xanchor="center", x=0.5,
        font=dict(size=13),
        itemsizing='constant'
    ),
    annotations=[
        dict(
            xref="paper", yref="paper", x=0.02, y=0.98,
            text="<span style='color:green'>●</span> OS<br><span style='color:red'>●</span> OD",
            font=dict(size=14, family="Arial Black"),
            showarrow=False, align="left", bgcolor="white", bordercolor="black", borderwidth=1
        )
    ],
    margin=dict(l=80, r=40, t=40, b=120)
)

st.plotly_chart(fig, use_container_width=True)

if st.button("Undo Last Entry"):
    if st.session_state.visits:
        st.session_state.visits.pop()
        st.rerun()
