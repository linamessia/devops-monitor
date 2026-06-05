import time
import requests
import streamlit as st

import os
API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = "dev-secret"
HEADERS = {"X-API-Key": API_KEY}

st.set_page_config(page_title="DevOps Monitor", layout="wide")
st.title("DevOps Monitoring Dashboard")

tab1, tab2 = st.tabs(["Metrics", "🖧 Servers"])


#Tab 1 : Metrics
with tab1:
    @st.cache_data(ttl=2)
    def fetch_metrics():
        try:
            resp = requests.get(f"{API_URL}/metrics", timeout=3)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            st.warning(f"Erreur fetch_metrics : {e}")
            return None

    if "history" not in st.session_state:
        st.session_state.history = []

    placeholder = st.empty()

    with placeholder.container():
        metrics = fetch_metrics()
    if metrics is None:
        st.error("Impossible de contacter l'API — vérifie que uvicorn tourne sur le port 8000")
        time.sleep(2)
        st.rerun()
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("CPU %", f"{metrics['cpu_percent']} %")
        col2.metric("Memory %", f"{metrics['memory_percent']} %")
        col3.metric("Disk %", f"{metrics['disk_percent']} %")

        st.session_state.history.append({
            "cpu": metrics["cpu_percent"],
            "memory": metrics["memory_percent"],
        })
        if len(st.session_state.history) > 60:
            st.session_state.history = st.session_state.history[-60:]

        if len(st.session_state.history) > 1:
            st.subheader("CPU & Memory over time")
            st.line_chart(st.session_state.history)

    time.sleep(2)
    st.rerun()


# Tab 2 : Servers
with tab2:

    @st.cache_data(ttl=5)
    def fetch_servers():
        try:
            return requests.get(f"{API_URL}/servers", timeout=3).json()
        except Exception:
            return []

    def color_status(val):
        colors = {"UP": "background-color: #d4edda",
                  "DEGRADED": "background-color: #fff3cd",
                  "DOWN": "background-color: #f8d7da"}
        return colors.get(val, "")

    st.subheader("Serveurs enregistrés")
    servers = fetch_servers()
    if servers:
        import pandas as pd
        df = pd.DataFrame(servers)
        st.dataframe(df.style.applymap(color_status, subset=["status"]),
                     use_container_width=True)
    else:
        st.info("Aucun serveur enregistré.")

    st.subheader("Ajouter un serveur")
    with st.form("add_server"):
        name = st.text_input("Nom")
        host = st.text_input("Host")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8080)
        submitted = st.form_submit_button("Enregistrer")
        if submitted and name and host:
            resp = requests.post(
                f"{API_URL}/servers",
                json={"name": name, "host": host, "port": int(port)},
                headers=HEADERS,
                timeout=5,
            )
            if resp.status_code == 201:
                st.success(f"Serveur '{name}' ajouté !")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Erreur : {resp.text}")

    st.subheader(" Déclencher un health check")
    if servers:
        options = {f"{s['id']} — {s['name']}": s["id"] for s in servers}
        choice = st.selectbox("Choisir un serveur", list(options.keys()))
        if st.button("Lancer le check"):
            sid = options[choice]
            resp = requests.post(f"{API_URL}/servers/{sid}/check", timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                st.success(f"Status : **{result['status']}**")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Erreur : {resp.text}")