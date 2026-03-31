"""
📋 SCOUT HQ — Scouting Report Manager
Professional scouting report platform for football scouts.
Built by Francois 🦾
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date
import json

st.set_page_config(page_title="Scout HQ", page_icon="📋", layout="wide")

# ═══ THEME ═══
T = {"BG":"#0a1a0a","CARD":"#112211","BORDER":"rgba(34,197,94,0.2)","BORDER_H":"rgba(34,197,94,0.5)",
     "PRIMARY":"#22c55e","LIGHT":"#4ade80","TEXT":"#a8d4a8","TEXT_L":"#e0f0e0","DIM":"#4a7a4a","SURFACE":"#0f1f0f"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.stApp{{background:{T['BG']};font-family:'Inter',sans-serif}}
[data-testid="stSidebar"]{{background:{T['SURFACE']};border-right:1px solid {T['BORDER']}}}
.main-hdr{{font-size:2rem;font-weight:800;background:linear-gradient(135deg,{T['PRIMARY']},{T['LIGHT']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;padding:20px 0 5px}}
.sub-hdr{{color:{T['DIM']};font-size:0.85rem;text-align:center;letter-spacing:4px;text-transform:uppercase}}
.divider{{width:60px;height:2px;background:{T['PRIMARY']};margin:15px auto}}
.report-card{{background:{T['CARD']};border:1px solid {T['BORDER']};border-radius:12px;padding:18px;margin-bottom:12px;transition:all 0.2s}}
.report-card:hover{{border-color:{T['BORDER_H']};transform:translateY(-2px)}}
.p-name{{font-size:1.1rem;font-weight:700;color:{T['TEXT_L']}}}
.p-meta{{font-size:0.8rem;color:{T['DIM']};margin-top:4px}}
.p-stat{{display:inline-block;margin:4px 6px 4px 0;padding:3px 10px;background:{T['SURFACE']};border-radius:6px;font-size:0.78rem}}
.p-val{{color:{T['LIGHT']};font-weight:700}}.p-lbl{{color:{T['DIM']}}}
.section-title{{font-size:1.3rem;font-weight:700;color:{T['TEXT_L']};border-left:4px solid {T['PRIMARY']};padding-left:12px;margin:25px 0 12px}}
.metric-card{{background:{T['CARD']};border:1px solid {T['BORDER']};border-radius:12px;padding:16px;text-align:center}}
.metric-val{{font-size:1.8rem;font-weight:800;color:{T['LIGHT']}}}
.metric-lbl{{font-size:0.7rem;color:{T['DIM']};letter-spacing:2px;text-transform:uppercase;margin-top:4px}}
.tag-sign{{background:rgba(34,197,94,0.15);color:#22c55e;padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:600}}
.tag-watch{{background:rgba(234,179,8,0.15);color:#eab308;padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:600}}
.tag-reject{{background:rgba(239,68,68,0.15);color:#ef4444;padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:600}}
.footer{{text-align:center;padding:30px;font-size:0.7rem;color:{T['DIM']};letter-spacing:2px}}
.stTabs [data-baseweb="tab-list"]{{gap:6px}}
.stTabs [data-baseweb="tab"]{{background:{T['SURFACE']};border-radius:8px;color:{T['DIM']};border:1px solid {T['BORDER']};font-size:0.85rem}}
.stTabs [aria-selected="true"]{{background:rgba(34,197,94,0.15)!important;color:{T['LIGHT']}!important;border-color:{T['PRIMARY']}!important}}
</style>
""", unsafe_allow_html=True)

# ═══ DEMO DATA ═══
def get_demo_reports():
    return [
        {"player":"Florian Wirtz","team":"Bayer Leverkusen","pos":"MF","age":20,"nation":"🇩🇪","liga":"Bundesliga",
         "technik":9,"taktik":9,"physis":7,"mental":9,"potenzial":10,
         "strengths":"Ballkontrolle, Spielintelligenz, Dribbling, Passqualität",
         "weaknesses":"Körperliche Robustheit, Defensivarbeit",
         "fazit":"Generationstalent. Einer der besten jungen Spieler der Welt. Kann jede Mannschaft besser machen.",
         "empfehlung":"sign","scout":"Francois","datum":"2024-03-15"},
        {"player":"Jamal Musiala","team":"Bayern München","pos":"MF","age":21,"nation":"🇩🇪","liga":"Bundesliga",
         "technik":10,"taktik":8,"physis":7,"mental":8,"potenzial":10,
         "strengths":"Dribbling auf engstem Raum, Ballgefühl, Kreativität, Torabschluss",
         "weaknesses":"Physische Präsenz, Konstanz über 90 Min",
         "fazit":"Technisch der Beste seiner Generation. Vereint Dribbling und Torinstinkt auf höchstem Niveau.",
         "empfehlung":"sign","scout":"Francois","datum":"2024-03-10"},
        {"player":"Xavi Simons","team":"RB Leipzig","pos":"MF,FW","age":21,"nation":"🇳🇱","liga":"Bundesliga",
         "technik":8,"taktik":8,"physis":8,"mental":8,"potenzial":9,
         "strengths":"Tempo, Schusskraft, Progressive Carries, Vielseitigkeit",
         "weaknesses":"Entscheidungsfindung unter Druck, Defensivumschaltung",
         "fazit":"Hochveranlagter Offensivspieler. Kann auf mehreren Positionen spielen. Starker Torinstinkt.",
         "empfehlung":"sign","scout":"Nico","datum":"2024-02-28"},
        {"player":"Loïs Openda","team":"RB Leipzig","pos":"FW","age":24,"nation":"🇧🇪","liga":"Bundesliga",
         "technik":7,"taktik":7,"physis":9,"mental":7,"potenzial":8,
         "strengths":"Geschwindigkeit, Laufbereitschaft, Pressing, Tiefenläufe",
         "weaknesses":"Chancenverwertung, Kopfballspiel",
         "fazit":"Klassischer moderner Stürmer. Lebt von Tempo und Intensität. Braucht Räume.",
         "empfehlung":"watch","scout":"Francois","datum":"2024-03-01"},
        {"player":"Jonathan Burkardt","team":"Mainz 05","pos":"FW","age":23,"nation":"🇩🇪","liga":"Bundesliga",
         "technik":7,"taktik":7,"physis":8,"mental":8,"potenzial":8,
         "strengths":"Kopfballstärke, Abschluss, Führungsqualität, Einsatzbereitschaft",
         "weaknesses":"Tempo, Dribbling",
         "fazit":"Klassischer Stoßstürmer mit Torriecher. Kann eine Mannschaft tragen. DFB-Perspektive.",
         "empfehlung":"watch","scout":"Nico","datum":"2024-02-20"},
        {"player":"Alejandro Grimaldo","team":"Bayer Leverkusen","pos":"DF","age":28,"nation":"🇪🇸","liga":"Bundesliga",
         "technik":9,"taktik":8,"physis":7,"mental":8,"potenzial":8,
         "strengths":"Flanken, Freistöße, Offensivdrang, Passqualität aus der Tiefe",
         "weaknesses":"Defensiv-Zweikämpfe, Geschwindigkeit rückwärts",
         "fazit":"Einer der besten offensiven Außenverteidiger Europas. Unglaubliche Assist-Quote.",
         "empfehlung":"sign","scout":"Francois","datum":"2024-03-05"},
        {"player":"Tim Kleindienst","team":"Gladbach","pos":"FW","age":28,"nation":"🇩🇪","liga":"Bundesliga",
         "technik":6,"taktik":7,"physis":9,"mental":8,"potenzial":6,
         "strengths":"Kopfballstärke, Körperlichkeit, Einsatz, Strafrauminstinkt",
         "weaknesses":"Tempo, technische Finesse, Passspiel",
         "fazit":"Solider Bundesliga-Stürmer. Holt das Maximum aus seinen Fähigkeiten raus. Für Top-5 zu limitiert.",
         "empfehlung":"reject","scout":"Francois","datum":"2024-02-15"},
        {"player":"Piero Hincapié","team":"Bayer Leverkusen","pos":"DF","age":22,"nation":"🇪🇨","liga":"Bundesliga",
         "technik":7,"taktik":8,"physis":8,"mental":7,"potenzial":9,
         "strengths":"Spieleröffnung, Antizipation, Ruhe am Ball, Progressive Passes",
         "weaknesses":"Luftzweikämpfe, Aggressivität",
         "fazit":"Moderner Innenverteidiger mit exzellenter Spieleröffnung. Großes Entwicklungspotenzial.",
         "empfehlung":"sign","scout":"Nico","datum":"2024-03-12"},
        {"player":"Enzo Millot","team":"VfB Stuttgart","pos":"MF","age":22,"nation":"🇫🇷","liga":"Bundesliga",
         "technik":8,"taktik":7,"physis":7,"mental":7,"potenzial":8,
         "strengths":"Kreativität, Dribblings, Tor-Beteiligungen, Bewegung im Zwischenlinienraum",
         "weaknesses":"Defensivarbeit, Konstanz",
         "fazit":"Technisch starker Zehner. Passt ins Stuttgarter System. Hat sich enorm entwickelt.",
         "empfehlung":"watch","scout":"Francois","datum":"2024-03-08"},
        {"player":"Granit Xhaka","team":"Bayer Leverkusen","pos":"MF","age":31,"nation":"🇨🇭","liga":"Bundesliga",
         "technik":8,"taktik":9,"physis":7,"mental":10,"potenzial":7,
         "strengths":"Spielintelligenz, Passspiel, Führung, Spielkontrolle, Mentalität",
         "weaknesses":"Tempo, Wendigkeit",
         "fazit":"Der Herzschlag von Leverkusen. Macht alle um sich herum besser. Absolute Führungsfigur.",
         "empfehlung":"sign","scout":"Nico","datum":"2024-03-03"},
    ]

# ═══ SESSION STATE ═══
if "reports" not in st.session_state:
    st.session_state.reports = get_demo_reports()

def rec_tag(emp):
    m = {"sign":("🟢 Verpflichten","tag-sign"),"watch":("🟡 Beobachten","tag-watch"),"reject":("🔴 Absage","tag-reject")}
    label, cls = m.get(emp, ("❓","tag-watch"))
    return f'<span class="{cls}">{label}</span>'

def avg_rating(r):
    return round((r["technik"]+r["taktik"]+r["physis"]+r["mental"])/4, 1)

def radar_fig(r, color=T["PRIMARY"]):
    cats = ["Technik","Taktik","Physis","Mental","Potenzial"]
    vals = [r["technik"],r["taktik"],r["physis"],r["mental"],r["potenzial"]]
    vals += vals[:1]; cats += cats[:1]
    fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill="toself", line=dict(color=color,width=2),
                                     fillcolor=f"rgba(34,197,94,0.15)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,10],gridcolor="rgba(34,197,94,0.1)"),
                                  angularaxis=dict(gridcolor="rgba(34,197,94,0.1)")),
                      template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                      height=300,font=dict(color=T["TEXT"],size=11),showlegend=False,margin=dict(l=50,r=50,t=20,b=20))
    return fig

# ═══ HEADER ═══
st.markdown('<div class="main-hdr">📋 SCOUT HQ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-hdr">Scouting Report Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

tabs = st.tabs(["📋 Reports", "➕ Neuer Report", "👤 Spieler", "📊 Statistiken"])

# ═══ TAB 1: REPORTS ═══
with tabs[0]:
    st.markdown('<div class="section-title">📋 Scouting Reports</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: pos_f = st.selectbox("Position",["Alle","FW","MF","DF","GK"])
    with c2: emp_f = st.selectbox("Empfehlung",["Alle","sign","watch","reject"])
    with c3: scout_f = st.selectbox("Scout",["Alle"]+list(set(r["scout"] for r in st.session_state.reports)))
    with c4: sort_f = st.selectbox("Sortieren",["Datum","Bewertung","Alter","Name"])

    filtered = st.session_state.reports.copy()
    if pos_f != "Alle": filtered = [r for r in filtered if pos_f in r["pos"]]
    if emp_f != "Alle": filtered = [r for r in filtered if r["empfehlung"]==emp_f]
    if scout_f != "Alle": filtered = [r for r in filtered if r["scout"]==scout_f]
    if sort_f == "Bewertung": filtered.sort(key=lambda r: avg_rating(r), reverse=True)
    elif sort_f == "Alter": filtered.sort(key=lambda r: r["age"])
    elif sort_f == "Name": filtered.sort(key=lambda r: r["player"])
    else: filtered.sort(key=lambda r: r["datum"], reverse=True)

    st.markdown(f"**{len(filtered)} Reports**")
    for i in range(0, len(filtered), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(filtered): break
            r = filtered[idx]
            with col:
                avg = avg_rating(r)
                st.markdown(f'''
                <div class="report-card">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div class="p-name">{r["player"]}</div>
                        {rec_tag(r["empfehlung"])}
                    </div>
                    <div class="p-meta">{r["team"]} · {r["pos"]} · {r["age"]} Jahre · {r["nation"]} · {r["liga"]}</div>
                    <div style="margin-top:10px;">
                        <span class="p-stat"><span class="p-val">{r["technik"]}</span> <span class="p-lbl">Tech</span></span>
                        <span class="p-stat"><span class="p-val">{r["taktik"]}</span> <span class="p-lbl">Takt</span></span>
                        <span class="p-stat"><span class="p-val">{r["physis"]}</span> <span class="p-lbl">Phys</span></span>
                        <span class="p-stat"><span class="p-val">{r["mental"]}</span> <span class="p-lbl">Ment</span></span>
                        <span class="p-stat"><span class="p-val">{avg}</span> <span class="p-lbl">⌀</span></span>
                    </div>
                    <div style="margin-top:8px;font-size:0.82rem;color:{T['TEXT']};line-height:1.5;">{r["fazit"]}</div>
                    <div style="margin-top:6px;font-size:0.7rem;color:{T['DIM']};">Scout: {r["scout"]} · {r["datum"]}</div>
                </div>''', unsafe_allow_html=True)

# ═══ TAB 2: NEUER REPORT ═══
with tabs[1]:
    st.markdown('<div class="section-title">➕ Neuer Scouting Report</div>', unsafe_allow_html=True)
    with st.form("new_report"):
        c1,c2,c3 = st.columns(3)
        with c1: player = st.text_input("Spieler *")
        with c2: team = st.text_input("Verein *")
        with c3: pos = st.selectbox("Position *",["FW","MF","DF","GK","FW,MF","MF,DF"])
        c1,c2,c3 = st.columns(3)
        with c1: age = st.number_input("Alter",16,45,22)
        with c2: nation = st.text_input("Nation (Emoji)","🇩🇪")
        with c3: liga = st.text_input("Liga","Bundesliga")
        st.markdown("**Bewertungen (1-10)**")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: technik = st.slider("Technik",1,10,7)
        with c2: taktik = st.slider("Taktik",1,10,7)
        with c3: physis = st.slider("Physis",1,10,7)
        with c4: mental = st.slider("Mental",1,10,7)
        with c5: potenzial = st.slider("Potenzial",1,10,7)
        strengths = st.text_area("Stärken")
        weaknesses = st.text_area("Schwächen")
        fazit = st.text_area("Fazit / Gesamteindruck")
        empfehlung = st.selectbox("Empfehlung",["sign","watch","reject"],format_func=lambda x:{"sign":"🟢 Verpflichten","watch":"🟡 Weiter beobachten","reject":"🔴 Absage"}[x])
        scout = st.text_input("Scout-Name","Francois")
        submitted = st.form_submit_button("📝 Report speichern", use_container_width=True)
        if submitted and player and team:
            st.session_state.reports.append({"player":player,"team":team,"pos":pos,"age":age,"nation":nation,"liga":liga,
                "technik":technik,"taktik":taktik,"physis":physis,"mental":mental,"potenzial":potenzial,
                "strengths":strengths,"weaknesses":weaknesses,"fazit":fazit,"empfehlung":empfehlung,
                "scout":scout,"datum":date.today().isoformat()})
            st.success(f"✅ Report für {player} gespeichert!")
            st.rerun()

# ═══ TAB 3: SPIELER ═══
with tabs[2]:
    st.markdown('<div class="section-title">👤 Spieler-Übersicht</div>', unsafe_allow_html=True)
    players = {}
    for r in st.session_state.reports:
        if r["player"] not in players:
            players[r["player"]] = {"reports":[],"team":r["team"],"pos":r["pos"],"age":r["age"],"nation":r["nation"]}
        players[r["player"]]["reports"].append(r)

    selected = st.selectbox("Spieler", list(players.keys()))
    if selected:
        p = players[selected]
        reports = p["reports"]
        avg_t = round(sum(r["technik"] for r in reports)/len(reports),1)
        avg_k = round(sum(r["taktik"] for r in reports)/len(reports),1)
        avg_p = round(sum(r["physis"] for r in reports)/len(reports),1)
        avg_m = round(sum(r["mental"] for r in reports)/len(reports),1)
        avg_pot = round(sum(r["potenzial"] for r in reports)/len(reports),1)

        st.markdown(f'''
        <div style="padding:20px;background:{T['CARD']};border-radius:12px;border:1px solid {T['BORDER']};">
            <div style="font-size:1.5rem;font-weight:800;color:{T['TEXT_L']}">{selected}</div>
            <div style="color:{T['DIM']}">{p["team"]} · {p["pos"]} · {p["age"]} Jahre · {p["nation"]}</div>
            <div style="color:{T['DIM']};font-size:0.85rem;margin-top:4px;">{len(reports)} Report(s)</div>
        </div>''', unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            fig = radar_fig({"technik":avg_t,"taktik":avg_k,"physis":avg_p,"mental":avg_m,"potenzial":avg_pot})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            c1,c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_t}</div><div class="metric-lbl">Technik</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_p}</div><div class="metric-lbl">Physis</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_k}</div><div class="metric-lbl">Taktik</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_m}</div><div class="metric-lbl">Mental</div></div>', unsafe_allow_html=True)

# ═══ TAB 4: STATISTIKEN ═══
with tabs[3]:
    st.markdown('<div class="section-title">📊 Report-Statistiken</div>', unsafe_allow_html=True)
    reports = st.session_state.reports
    c1,c2,c3,c4 = st.columns(4)
    signs = len([r for r in reports if r["empfehlung"]=="sign"])
    watches = len([r for r in reports if r["empfehlung"]=="watch"])
    rejects = len([r for r in reports if r["empfehlung"]=="reject"])
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-val">{len(reports)}</div><div class="metric-lbl">Reports</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#22c55e">{signs}</div><div class="metric-lbl">Verpflichten</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#eab308">{watches}</div><div class="metric-lbl">Beobachten</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#ef4444">{rejects}</div><div class="metric-lbl">Absagen</div></div>', unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">🏆 Top bewertete Spieler</div>', unsafe_allow_html=True)
        top = sorted(reports, key=lambda r: avg_rating(r), reverse=True)[:5]
        for r in top:
            st.markdown(f'<div class="p-stat" style="margin:4px 0;display:block"><span class="p-val">{avg_rating(r)}</span> <span class="p-lbl">{r["player"]} ({r["team"]})</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-title">📝 Reports pro Scout</div>', unsafe_allow_html=True)
        scout_counts = {}
        for r in reports: scout_counts[r["scout"]] = scout_counts.get(r["scout"],0)+1
        for s,c in sorted(scout_counts.items(), key=lambda x:x[1], reverse=True):
            st.markdown(f'<div class="p-stat" style="margin:4px 0;display:block"><span class="p-val">{c}</span> <span class="p-lbl">{s}</span></div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer">SCOUT HQ © 2025 · PROFESSIONAL SCOUTING PLATFORM · BUILT BY FRANCOIS 🦾</div>', unsafe_allow_html=True)
