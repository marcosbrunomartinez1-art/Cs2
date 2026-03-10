import streamlit as st
import sqlite3
import random
import pandas as pd
import requests

# 1. Configuración de jugadores (fuera del botón)
vitality = {"Zywoo": 94, "Apex": 88, "Ropz": 92, "Flamez": 90, "Mezii": 90}
furia = {"Fallen": 85, "Molodoy": 90, "Kscerato": 91, "Yekindar": 88, "Yuriih": 88}

def jugar_ronda(stats):
    v_vivos = list(vitality.keys())
    f_vivos = list(furia.keys())
    while v_vivos and f_vivos:
        at = random.choice(v_vivos + f_vivos)
        op = random.choice(f_vivos if at in vitality else v_vivos)
        s_at = vitality.get(at, furia.get(at))
        s_op = vitality.get(op, furia.get(op))
        if random.random() < (s_at / (s_at + s_op)):
            stats[at]["K"] += 1; stats[op]["D"] += 1
            if op in v_vivos: v_vivos.remove(op)
            else: f_vivos.remove(op)
        else:
            stats[op]["K"] += 1; stats[at]["D"] += 1
            if at in v_vivos: v_vivos.remove(at)
            else: f_vivos.remove(at)
    return "V" if not f_vivos else "F"

st.title("🏆 Simulador Profesional de CS2")

# 2. El botón de acción
if st.button("Simular Partido"):
    stats = {j: {"K": 0, "D": 0} for j in {**vitality, **furia}}
    m_v, m_f, fase = 0, 0, "reglamentaria"
    
    while True:
        res = jugar_ronda(stats)
        if res == "V": m_v += 1
        else: m_f += 1
        if fase == "reglamentaria":
            if m_v == 13 or m_f == 13: break
            if m_v == 12 and m_f == 12: fase = "overtime"
        elif fase == "overtime":
            if abs(m_v - m_f) >= 2 and (m_v > 12 or m_f > 12): break

    # Guardar en SQLite
    conn = sqlite3.connect('partidos_cs2.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS partidos (id INTEGER PRIMARY KEY, vital_score INTEGER, furia_score INTEGER, mvp TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS estadisticas (partido_id INTEGER, jugador TEXT, kills INTEGER, deaths INTEGER)')
    mvp = max(stats, key=lambda x: stats[x]['K'])
    c.execute("INSERT INTO partidos (vital_score, furia_score, mvp) VALUES (?, ?, ?)", (m_v, m_f, mvp))
    pid = c.lastrowid
    for j, s in stats.items():
        c.execute("INSERT INTO estadisticas VALUES (?, ?, ?, ?)", (pid, j, s['K'], s['D']))
    conn.commit(); conn.close()



    st.success(f"MARCADOR FINAL: Vitality {m_v} - {m_f} Furia | MVP: {mvp}")
    st.table(pd.DataFrame.from_dict(stats, orient='index'))

# 3. Botón de descarga (siempre visible)
try:
    with open("partidos_cs2.db", "rb") as file:
        st.download_button("Descargar historial", file, "historial_cs2.db")
except:
    st.info("Simula un partido para generar la base de datos.")


