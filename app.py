import re
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

st.set_page_config(page_title="Company Intel", page_icon="🧠", layout="wide")

# ═══ THEME ═══
T = {
    "BG": "#07111f",
    "CARD": "#0d1b2a",
    "SURFACE": "#10243a",
    "BORDER": "rgba(96,165,250,0.16)",
    "BORDER_H": "rgba(96,165,250,0.45)",
    "PRIMARY": "#60a5fa",
    "ACCENT": "#22d3ee",
    "TEXT": "#dbeafe",
    "TEXT_DIM": "#8aa6c1",
    "SUCCESS": "#34d399",
    "WARN": "#fbbf24",
}

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.stApp {{ background: radial-gradient(circle at top right, rgba(34,211,238,0.08), transparent 20%), {T['BG']}; font-family:'Inter',sans-serif; }}
[data-testid="stSidebar"] {{ background:{T['SURFACE']}; border-right:1px solid {T['BORDER']}; }}
.block {{ background:{T['CARD']}; border:1px solid {T['BORDER']}; border-radius:18px; padding:20px; }}
.hero {{ padding:32px 0 18px; }}
.hero-title {{ font-size:3rem; font-weight:800; line-height:1; color:{T['TEXT']}; margin-bottom:10px; }}
.hero-title .accent {{ background:linear-gradient(135deg, {T['PRIMARY']}, {T['ACCENT']}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.hero-sub {{ color:{T['TEXT_DIM']}; font-size:1rem; max-width:840px; line-height:1.6; }}
.kpi {{ background:{T['CARD']}; border:1px solid {T['BORDER']}; border-radius:16px; padding:18px; height:100%; }}
.kpi-label {{ color:{T['TEXT_DIM']}; font-size:0.78rem; letter-spacing:1.4px; text-transform:uppercase; margin-bottom:10px; }}
.kpi-value {{ color:{T['TEXT']}; font-size:1.7rem; font-weight:800; }}
.section-title {{ color:{T['TEXT']}; font-size:1.2rem; font-weight:700; margin:8px 0 14px; }}
.muted {{ color:{T['TEXT_DIM']}; }}
.source-card {{ background:{T['SURFACE']}; border:1px solid {T['BORDER']}; border-radius:14px; padding:16px; margin-bottom:12px; }}
.source-title {{ color:{T['TEXT']}; font-size:1rem; font-weight:700; margin-bottom:6px; }}
.source-meta {{ color:{T['TEXT_DIM']}; font-size:0.82rem; margin-bottom:8px; }}
.summary-box {{ background:linear-gradient(180deg, rgba(96,165,250,0.12), rgba(34,211,238,0.04)); border:1px solid {T['BORDER_H']}; border-radius:18px; padding:20px; }}
.badge {{ display:inline-block; padding:5px 10px; border-radius:999px; font-size:0.78rem; font-weight:700; margin-right:8px; margin-bottom:8px; }}
.badge-ok {{ background:rgba(52,211,153,0.14); color:{T['SUCCESS']}; }}
.badge-warn {{ background:rgba(251,191,36,0.12); color:{T['WARN']}; }}
.footer {{ text-align:center; padding:30px 0 10px; color:{T['TEXT_DIM']}; font-size:0.8rem; }}
.stTextInput > div > div > input {{ background:{T['SURFACE']}; color:{T['TEXT']}; border-radius:12px; }}
</style>
""",
    unsafe_allow_html=True,
)


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def infer_domain(url: str) -> str:
    url = url.replace("https://", "").replace("http://", "")
    return url.split("/")[0]


@st.cache_data(show_spinner=False, ttl=1800)
def search_company(company: str, region: str, max_results: int = 8):
    query = f'{company} company latest news official website {region}'.strip()
    results = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append(
                {
                    "title": item.get("title", ""),
                    "href": item.get("href", ""),
                    "body": item.get("body", ""),
                }
            )
    return results


@st.cache_data(show_spinner=False, ttl=1800)
def fetch_page_excerpt(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = clean_text(soup.get_text(" "))
        if len(text) > 900:
            text = text[:900] + "…"
        return text
    except Exception:
        return ""



def build_brief(company: str, search_results):
    official_site = None
    linkedin = None
    wikipedia = None
    current_points = []
    source_rows = []

    for item in search_results:
        title = clean_text(item.get("title", ""))
        url = item.get("href", "")
        snippet = clean_text(item.get("body", ""))
        domain = infer_domain(url) if url else ""

        if not official_site and domain and company.lower().replace(" ", "") in domain.replace("-", "").replace(".", ""):
            official_site = url
        if not linkedin and "linkedin.com" in domain:
            linkedin = url
        if not wikipedia and "wikipedia.org" in domain:
            wikipedia = url

        excerpt = fetch_page_excerpt(url) if url else ""
        merged = clean_text(f"{snippet} {excerpt}")
        if merged:
            current_points.append(merged)

        source_rows.append(
            {
                "title": title or domain or "Quelle",
                "url": url,
                "domain": domain,
                "snippet": snippet,
                "excerpt": excerpt,
            }
        )

    facts = []
    if official_site:
        facts.append(("Offizielle Website", official_site))
    if linkedin:
        facts.append(("LinkedIn", linkedin))
    if wikipedia:
        facts.append(("Wikipedia", wikipedia))

    combined = " ".join(current_points)
    sentences = re.split(r"(?<=[.!?])\s+", combined)
    picked = []
    for s in sentences:
        s = clean_text(s)
        if not s:
            continue
        if company.lower() in s.lower() or len(picked) < 6:
            if s not in picked:
                picked.append(s)
        if len(picked) >= 6:
            break

    summary = picked[:4]
    watchouts = []
    for s in picked[4:]:
        if any(word in s.lower() for word in ["may", "could", "rumor", "report", "analyst", "possible", "expected"]):
            watchouts.append(s)

    return {
        "facts": facts,
        "summary": summary,
        "watchouts": watchouts,
        "sources": source_rows,
        "source_count": len(source_rows),
    }


st.markdown('<div class="hero">', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Company <span class="accent">Intel</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Gib ein Unternehmen ein und die App recherchiert aktuelle Web-Quellen, zieht Kernaussagen heraus und bereitet sie als kompaktes Briefing auf. Kein Bullshit, sondern ein sauberes MVP für schnelle Company Research.</div>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Recherche-Setup")
    company = st.text_input("Unternehmen", placeholder="z. B. Nvidia, Zalando, SAP")
    region = st.text_input("Region / Kontext", value="Germany")
    max_results = st.slider("Anzahl Quellen", 5, 12, 8)
    run = st.button("🔎 Recherche starten", use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown(
        "**MVP-Grenzen**\n- freie Websuche\n- keine Paywall-Umgehung\n- Qualität hängt von Quellenlage ab\n- ideal für schnellen First Brief, nicht für Due Diligence"
    )

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="kpi"><div class="kpi-label">Use Case</div><div class="kpi-value">Research MVP</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="kpi"><div class="kpi-label">Output</div><div class="kpi-value">Briefing + Quellen</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="kpi"><div class="kpi-label">Geeignet für</div><div class="kpi-value">Sales · VC · Recruiting</div></div>', unsafe_allow_html=True)

if run and company:
    with st.spinner(f"Recherchiere {company} ..."):
        try:
            results = search_company(company, region, max_results=max_results)
            brief = build_brief(company, results)
            st.session_state["brief"] = brief
            st.session_state["company"] = company
        except Exception as e:
            st.error(f"Recherche fehlgeschlagen: {e}")

brief = st.session_state.get("brief")
company_name = st.session_state.get("company")

if not brief:
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">So würde ich das Produkt positionieren</div>', unsafe_allow_html=True)
    st.markdown(
        "- **Einfach machbar als MVP:** Firmenname rein, Webquellen raus, Zusammenfassung anzeigen\n"
        "- **Professionell wirkend:** ja, absolut\n"
        "- **Schwierig wird es** bei Datenqualität, Dubletten, schwachen Quellen und rechtlicher/API-Skalierung\n"
        "- **Deshalb** ist diese erste Version bewusst ein sauberer Research-Assistent statt eine Wunderkugel"
    )
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Executive Brief — {company_name}</div>', unsafe_allow_html=True)

    if brief["source_count"] >= 6:
        st.markdown('<span class="badge badge-ok">Solide Quellenbasis</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-warn">Begrenzte Quellenbasis</span>', unsafe_allow_html=True)

    st.markdown('<span class="badge badge-ok">Aktuelle Web-Recherche</span>', unsafe_allow_html=True)
    st.markdown('<span class="badge badge-warn">Menschliche Prüfung empfohlen</span>', unsafe_allow_html=True)

    if brief["summary"]:
        for point in brief["summary"]:
            st.markdown(f"- {point}")
    else:
        st.markdown("- Für dieses Unternehmen konnte ich aus den freien Quellen noch keine saubere Kurz-Zusammenfassung ziehen.")
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="block">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Key Links</div>', unsafe_allow_html=True)
        if brief["facts"]:
            for label, url in brief["facts"]:
                st.markdown(f"- **{label}:** [{url}]({url})")
        else:
            st.markdown("- Keine klaren Primärlinks erkannt.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="block">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Watchouts</div>', unsafe_allow_html=True)
        if brief["watchouts"]:
            for item in brief["watchouts"]:
                st.markdown(f"- {item}")
        else:
            st.markdown("- Keine klaren Warnhinweise erkannt. Trotzdem Quellen prüfen.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Quellen</div>', unsafe_allow_html=True)
    for source in brief["sources"]:
        title = source["title"] or source["domain"] or "Quelle"
        url = source["url"]
        domain = source["domain"]
        snippet = source["snippet"]
        excerpt = source["excerpt"]
        st.markdown(
            f'''<div class="source-card">
<div class="source-title">{title}</div>
<div class="source-meta">{domain}</div>
<div class="muted">{snippet or excerpt or 'Keine Vorschau verfügbar.'}</div>
</div>''',
            unsafe_allow_html=True,
        )
        if url:
            st.markdown(f"[Quelle öffnen]({url})")

    source_df = pd.DataFrame(
        [{"Titel": s["title"], "Domain": s["domain"], "URL": s["url"]} for s in brief["sources"]]
    )
    with st.expander("Quellen als Tabelle"):
        st.dataframe(source_df, use_container_width=True, hide_index=True)

st.markdown('<div class="footer">COMPANY INTEL · MODERN COMPANY RESEARCH MVP · BUILT BY FRANCOIS 🦾</div>', unsafe_allow_html=True)
