import streamlit as st
import psutil
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Dashboard Pro Surveillance", layout="wide")
st.title("🚨 Dashboard Pro Surveillance Local avec Logs et Alertes")

# ----- Configuration -----
services = ["nginx"]  # فقط الخدمات الموجودة على جهازك
refresh_interval = 5  # secondes
thresholds = {"cpu": 80, "ram": 80, "disk": 90}  # seuils

# ----- Auto-refresh -----
st_autorefresh(interval=refresh_interval * 1000, limit=None, key="dashboard_refresh")

# ----- DataFrames pour historique -----
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "cpu", "ram", "disk"])

if "incidents" not in st.session_state:
    st.session_state.incidents = pd.DataFrame(columns=["timestamp", "service", "status"])

# ----- Fonctions -----
def check_service(service):
    try:
        res = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        status = res.stdout.strip()
        return status
    except Exception as e:
        return str(e)

def colored_metric_text(label, value, threshold):
    color = "green" if value <= threshold else "red"
    st.markdown(f"<h4>{label}: <span style='color:{color}'>{value}%</span></h4>", unsafe_allow_html=True)

# ----- Collecte des metrics -----
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage("/").percent

new_row = pd.DataFrame([{"timestamp": datetime.now(), "cpu": cpu, "ram": ram, "disk": disk}])
st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)

# ----- Vérification services et logs -----
for s in services:
    status = check_service(s)
    if status != "active":
        new_incident = pd.DataFrame([{"timestamp": datetime.now(), "service": s, "status": status}])
        st.session_state.incidents = pd.concat([st.session_state.incidents, new_incident], ignore_index=True)

# ----- Affichage Metrics avec couleurs -----
st.subheader("💻 Ressources Système")
col1, col2, col3 = st.columns(3)
colored_metric_text("CPU Usage", cpu, thresholds["cpu"])
colored_metric_text("RAM Usage", ram, thresholds["ram"])
colored_metric_text("Disk Usage", disk, thresholds["disk"])

# ----- Graphiques historique -----
st.subheader("📈 Historique des ressources")
fig, ax = plt.subplots(figsize=(10,4))
ax.plot(st.session_state.history["timestamp"], st.session_state.history["cpu"], label="CPU", color='blue')
ax.plot(st.session_state.history["timestamp"], st.session_state.history["ram"], label="RAM", color='orange')
ax.plot(st.session_state.history["timestamp"], st.session_state.history["disk"], label="Disk", color='purple')
ax.set_ylabel("%")
ax.set_xlabel("Temps")
ax.legend()
st.pyplot(fig)

# ----- Pie chart incidents -----
st.subheader("📊 Répartition des incidents par service")
if not st.session_state.incidents.empty:
    count_service = st.session_state.incidents['service'].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(count_service, labels=count_service.index, autopct='%1.1f%%', colors=['red', 'blue', 'green'])
    st.pyplot(fig2)
else:
    st.write("Pas d'incidents pour l'instant.")

# ----- Affichage Logs -----
st.subheader("⚠️ Incidents enregistrés")
st.dataframe(st.session_state.incidents)
