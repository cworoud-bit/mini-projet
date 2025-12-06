import streamlit as st
import psutil
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --------------------------
# CONFIGURATION
# --------------------------
thresholds = {
    "cpu": 80,
    "ram": 80,
    "disk": 90
}

disk_clean_path = "/tmp"  # dossier à nettoyer si disque plein
services = ["nginx"]      # services monitorés (ssh/mysql si installés)

# --------------------------
# INIT SESSION STATE
# --------------------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["time", "cpu", "ram", "disk"])

if "incidents" not in st.session_state:
    st.session_state.incidents = pd.DataFrame(columns=["time", "service", "issue", "action"])

# --------------------------
# FONCTIONS
# --------------------------
def auto_clean_disk(threshold=90, path=disk_clean_path):
    usage = psutil.disk_usage("/").percent
    if usage >= threshold:
        st.warning(f"Disk usage {usage}% >= {threshold}%, cleaning {path}...")
        try:
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            st.info("[AUTO-CLEAN] Done")
        except Exception as e:
            st.error(f"[AUTO-CLEAN] Error: {e}")
        # Log incident
        st.session_state.incidents = pd.concat([st.session_state.incidents, pd.DataFrame([{
            "time": datetime.now(),
            "service": "Disk",
            "issue": f"Usage {usage}%",
            "action": f"Cleaned {path}"
        }])], ignore_index=True)

def colored_metric(label, value, threshold):
    color = "normal"
    if value >= threshold:
        color = "inverse"
    st.metric(label, f"{value}%", delta=None, delta_color=color)

# --------------------------
# MONITORING
# --------------------------
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage("/").percent

# Add to history
st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([{
    "time": datetime.now(),
    "cpu": cpu,
    "ram": ram,
    "disk": disk
}])], ignore_index=True)

# Check thresholds
if cpu >= thresholds["cpu"]:
    st.session_state.incidents = pd.concat([st.session_state.incidents, pd.DataFrame([{
        "time": datetime.now(),
        "service": "CPU",
        "issue": f"{cpu}%",
        "action": "Alert"
    }])], ignore_index=True)

if ram >= thresholds["ram"]:
    st.session_state.incidents = pd.concat([st.session_state.incidents, pd.DataFrame([{
        "time": datetime.now(),
        "service": "RAM",
        "issue": f"{ram}%",
        "action": "Alert"
    }])], ignore_index=True)

if disk >= thresholds["disk"]:
    auto_clean_disk(threshold=thresholds["disk"], path=disk_clean_path)

# --------------------------
# STREAMLIT DASHBOARD
# --------------------------
st.title("Dashboard Surveillance Proactive")

st.subheader("Resources Usage")
col1, col2, col3 = st.columns(3)
with col1:
    colored_metric("CPU Usage", cpu, thresholds["cpu"])
with col2:
    colored_metric("RAM Usage", ram, thresholds["ram"])
with col3:
    colored_metric("Disk Usage", disk, thresholds["disk"])

st.subheader("History")
st.line_chart(st.session_state.history.set_index("time"))

st.subheader("Incidents")
st.dataframe(st.session_state.incidents)

# --------------------------
# Pie Chart sûr
# --------------------------
st.subheader("Pie Chart of Incidents by Service")
if st.session_state.incidents.empty or st.session_state.incidents["service"].dropna().empty:
    st.info("Pas d'incidents pour le moment")
else:
    pie_data = st.session_state.incidents["service"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%")
    st.pyplot(fig)

# --------------------------
# AUTO REFRESH
# --------------------------
st_autorefresh(interval=5000, key="auto_refresh")  # 5000 ms = 5 secondes
