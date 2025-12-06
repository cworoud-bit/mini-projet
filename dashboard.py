import streamlit as st
import psutil
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Dashboard Surveillance Local", layout="wide")
st.title("🔧 Dashboard Surveillance Local Temps Réel")

# ----- Configuration -----
services = ["nginx"]  # فقط الخدمات الموجودة على جهازك
refresh_interval = 5  # secondes

# ----- Auto-refresh -----
# هذا يقوم بتحديث الصفحة كل 5 ثواني
st_autorefresh(interval=refresh_interval * 1000, limit=None, key="dashboard_refresh")

# ----- DataFrames pour historique -----
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "cpu", "ram", "disk"])

# ----- Fonctions -----
def check_service(service):
    try:
        res = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception as e:
        return str(e)

# ----- Collecte des metrics -----
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage("/").percent

new_row = pd.DataFrame([{"timestamp": datetime.now(), "cpu": cpu, "ram": ram, "disk": disk}])
st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)

# ----- Affichage Metrics -----
st.subheader("💻 Ressources Système")
col1, col2, col3 = st.columns(3)
col1.metric("CPU Usage", f"{cpu}%")
col2.metric("RAM Usage", f"{ram}%")
col3.metric("Disk Usage", f"{disk}%")

# ----- Graphiques historique -----
st.subheader("📈 Historique des ressources")
fig, ax = plt.subplots(figsize=(10,4))
ax.plot(st.session_state.history["timestamp"], st.session_state.history["cpu"], label="CPU")
ax.plot(st.session_state.history["timestamp"], st.session_state.history["ram"], label="RAM")
ax.plot(st.session_state.history["timestamp"], st.session_state.history["disk"], label="Disk")
ax.set_ylabel("%")
ax.set_xlabel("Temps")
ax.legend()
st.pyplot(fig)

# ----- Vérification services -----
st.subheader("🛠️ Services")
for s in services:
    status = check_service(s)
    st.write(f"{s}: {status}")
