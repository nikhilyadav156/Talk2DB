import streamlit as st
import requests
import pandas as pd
import time
import re

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Talk2DB",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #F7F8FA !important; }
section[data-testid="stSidebar"] { display: none !important; }

.nav {
    background: #0F1117;
    padding: 0 40px;
    height: 62px;
    display: flex;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 999;
}
.nav-logo { font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.6px; }
.nav-logo em { color: #818CF8; font-style: normal; }
.nav-right { margin-left: auto; display: flex; align-items: center; gap: 14px; }
.nav-status {
    display: flex; align-items: center; gap: 7px;
    font-size: 13px; color: #6B7280;
    background: #1F2937; padding: 6px 14px; border-radius: 20px;
}
.nav-dot { width: 7px; height: 7px; border-radius: 50%; background: #10B981; display: inline-block; }
.nav-avatar {
    width: 34px; height: 34px; border-radius: 50%; background: #4F46E5;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #fff;
}
.page { padding: 36px 52px 52px; max-width: 1060px; margin: 0 auto; }
.sh { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.sh-title { font-size: 13px; font-weight: 700; color: #111827; white-space: nowrap; }
.sh-line { flex: 1; height: 1px; background: #E5E7EB; }
.sh-meta { font-size: 12px; color: #9CA3AF; white-space: nowrap; }
.query-card {
    background: #fff; border: 1.5px solid #E5E7EB; border-radius: 16px;
    padding: 24px 26px 20px; margin-bottom: 28px;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
    transition: border-color .2s, box-shadow .2s;
}
.query-card:focus-within { border-color: #A5B4FC; box-shadow: 0 0 0 4px rgba(79,70,229,.06); }
.query-label { font-size: 10px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; }
.chip-row {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    margin-top: 16px; padding-top: 16px; border-top: 1px solid #F3F4F6;
}
.chip-label { font-size: 12px; color: #9CA3AF; font-weight: 500; }
.chip {
    padding: 5px 14px; border-radius: 20px; border: 1px solid #E5E7EB;
    background: #F9FAFB; font-size: 12.5px; font-weight: 500; color: #6B7280;
    cursor: pointer; transition: all .15s; font-family: 'Plus Jakarta Sans', sans-serif; white-space: nowrap;
}
.chip:hover { border-color: #A5B4FC; color: #4F46E5; background: #EEF2FF; }
.panel {
    background: #fff; border: 1px solid #E5E7EB; border-radius: 16px;
    overflow: hidden; margin-bottom: 28px; box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.panel-hdr {
    padding: 13px 20px; border-bottom: 1px solid #F3F4F6;
    display: flex; align-items: center; gap: 10px; background: #FAFAFA;
}
.panel-title { font-size: 13px; font-weight: 600; color: #374151; }
.panel-actions { margin-left: auto; display: flex; gap: 7px; }
.pbtn {
    padding: 5px 14px; border: 1px solid #E5E7EB; border-radius: 8px;
    background: #fff; font-size: 12px; font-weight: 500; color: #6B7280;
    cursor: pointer; font-family: 'Plus Jakarta Sans', sans-serif; transition: all .15s;
}
.pbtn:hover { border-color: #D1D5DB; color: #374151; background: #F9FAFB; }
.pbtn.primary { background: #4F46E5; color: #fff; border-color: #4F46E5; }
.pbtn.primary:hover { background: #3730A3; }
.sql-block {
    padding: 22px 26px; background: #FAFAFE;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13.5px; line-height: 2; color: #374151;
    border-bottom: 1px solid #F3F4F6;
    white-space: pre-wrap; word-break: break-word;
}
.kw  { color: #4F46E5; font-weight: 700; }
.tbl { color: #0891B2; font-weight: 500; }
.str { color: #059669; }
.num { color: #7C3AED; }
.exec-bar {
    padding: 11px 20px; background: #FAFAFA;
    display: flex; align-items: center; gap: 24px; flex-wrap: wrap;
}
.exec-item { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #9CA3AF; }
.exec-item b { color: #374151; font-weight: 600; }
.exec-item.ok b { color: #10B981; }
.exec-item.err b { color: #EF4444; }
.tbl-toolbar {
    padding: 12px 20px; border-bottom: 1px solid #F3F4F6;
    display: flex; align-items: center; gap: 12px; background: #FAFAFA;
}
.tbl-search {
    display: flex; align-items: center; gap: 8px;
    background: #fff; border: 1px solid #E5E7EB; border-radius: 8px;
    padding: 7px 12px; max-width: 240px; flex: 1;
}
.tbl-search input {
    border: none; outline: none; background: transparent;
    font-size: 13px; color: #111827; width: 100%;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.tbl-search input::placeholder { color: #CBD5E1; }
.tbl-count { margin-left: auto; font-size: 12.5px; color: #6B7280; }
.tbl-count b { color: #111827; font-weight: 600; }
.data-tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-tbl thead th {
    padding: 11px 18px; text-align: left; font-size: 10.5px; font-weight: 700;
    color: #9CA3AF; text-transform: uppercase; letter-spacing: .7px;
    background: #F9FAFB; border-bottom: 1px solid #E5E7EB; white-space: nowrap;
}
.data-tbl tbody td {
    padding: 13px 18px; border-bottom: 1px solid #F3F4F6;
    color: #374151; vertical-align: middle; font-size: 13px;
}
.data-tbl tbody tr:last-child td { border-bottom: none; }
.data-tbl tbody tr:hover td { background: #FAFBFF; }
.pill { display: inline-block; padding: 3px 11px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.p-green  { background: #ECFDF5; color: #065F46; }
.p-red    { background: #FEF2F2; color: #B91C1C; }
.p-indigo { background: #EEF2FF; color: #3730A3; border: 1px solid #E0E7FF; }
.p-blue   { background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
.p-gray   { background: #F3F4F6; color: #6B7280; border: 1px solid #E5E7EB; }
.p-amber  { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.bdg { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block; }
.bdg-s { background: #ECFDF5; color: #065F46; border: 1px solid #D1FAE5; }
.bdg-e { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.bdg-i { background: #EEF2FF; color: #3730A3; border: 1px solid #E0E7FF; }
.kpi-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 18px; margin-bottom: 28px; }
.kpi-card {
    background: #fff; border: 1px solid #E5E7EB; border-radius: 16px;
    padding: 22px 24px; position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.04); transition: transform .2s, box-shadow .2s;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; border-radius: 16px 16px 0 0;
}
.kpi-card.c1::before { background: #4F46E5; }
.kpi-card.c2::before { background: #10B981; }
.kpi-card.c3::before { background: #F59E0B; }
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.08); }
.kpi-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.kpi-ico { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.kpi-ico.p { background: #EEF2FF; }
.kpi-ico.g { background: #ECFDF5; }
.kpi-ico.a { background: #FFFBEB; }
.kpi-trend { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; }
.kpi-trend.up { background: #ECFDF5; color: #065F46; }
.kpi-trend.nt { background: #F3F4F6; color: #6B7280; }
.kpi-val { font-size: 32px; font-weight: 800; color: #111827; letter-spacing: -1.5px; line-height: 1; margin-bottom: 5px; }
.kpi-lbl { font-size: 12.5px; color: #9CA3AF; font-weight: 500; }
.hist-item {
    padding: 15px 22px; border-bottom: 1px solid #F3F4F6;
    display: flex; align-items: flex-start; gap: 14px; cursor: pointer; transition: background .12s;
}
.hist-item:last-child { border-bottom: none; }
.hist-item:hover { background: #FAFBFF; }
.hist-num {
    width: 26px; height: 26px; flex-shrink: 0; border-radius: 7px;
    background: #F3F4F6; border: 1px solid #E5E7EB;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700; color: #9CA3AF; margin-top: 1px;
    min-width: 26px;
}
.hist-q { font-size: 13px; color: #374151; font-weight: 500; margin-bottom: 4px; }
.hist-sql {
    font-family: 'JetBrains Mono', monospace; font-size: 11.5px; color: #9CA3AF;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 580px;
}
.hist-meta { margin-left: auto; display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.empty { padding: 60px 20px; text-align: center; }
.empty-icon { font-size: 40px; margin-bottom: 14px; opacity: .3; }
.empty-title { font-size: 15px; font-weight: 600; color: #9CA3AF; margin-bottom: 6px; }
.empty-sub { font-size: 13px; color: #D1D5DB; }
.footer {
    padding: 20px 52px; border-top: 1px solid #E5E7EB;
    display: flex; align-items: center; justify-content: space-between;
    background: #fff; margin-top: 20px;
}
.footer-l { font-size: 13px; color: #9CA3AF; }
.footer-l b { color: #4F46E5; }
.footer-r { display: flex; gap: 22px; }
.footer-link { font-size: 13px; color: #9CA3AF; cursor: pointer; transition: color .15s; }
.footer-link:hover { color: #6B7280; }

.stTextInput > div > div > input {
    background: #FAFAFA !important; border: 1.5px solid #E5E7EB !important;
    border-radius: 10px !important; color: #111827 !important;
    font-size: 15px !important; padding: 13px 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: none !important; transition: all .2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #A5B4FC !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,.07) !important;
    background: #fff !important;
}
.stTextInput > div > div > input::placeholder { color: #CBD5E1 !important; }
[data-testid="stTextInputRootElement"] label { display: none !important; }
.stButton > button {
    background: #4F46E5 !important; color: #fff !important;
    border: none !important; border-radius: 9px !important;
    padding: 11px 24px !important; font-weight: 600 !important;
    font-size: 13.5px !important; width: 100% !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 2px 8px rgba(79,70,229,.3) !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    background: #3730A3 !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(79,70,229,.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #0F1117 !important; border-bottom: 1px solid #1F2937 !important;
    padding: 0 40px !important; gap: 0 !important; border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #6B7280 !important;
    border-radius: 0 !important; font-size: 14px !important;
    font-weight: 500 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 15px 30px !important; border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important; font-weight: 600 !important;
    border-bottom: 2px solid #818CF8 !important;
    background: #1F2937 !important; border-radius: 8px 8px 0 0 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F9FAFB; }
::-webkit-scrollbar-thumb { background: #E5E7EB; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A5B4FC; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────

def call_query(q: str) -> dict:
    try:
        r = requests.post(
            f"{API_URL}/query",
            json={"question": q},
            timeout=30
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e),
                "sql": None, "data": [], "row_count": 0, "columns": []}


def get_history() -> list:
    try:
        r = requests.get(f"{API_URL}/history", timeout=10)
        return r.json().get("history", [])
    except:
        return []


def clear_history():
    try:
        requests.delete(f"{API_URL}/history", timeout=10)
    except:
        pass


def highlight_sql(sql: str) -> str:
    if not sql:
        return "<span style='color:#9CA3AF'>No SQL generated.</span>"
    keywords = [
        "SELECT", "FROM", "WHERE", "JOIN", "ON", "GROUP BY",
        "ORDER BY", "LIMIT", "COUNT", "SUM", "AVG", "MAX", "MIN",
        "HAVING", "INNER", "LEFT", "RIGHT", "AND", "OR", "NOT",
        "IN", "LIKE", "AS", "DISTINCT", "DESC", "ASC", "BY"
    ]
    out = sql
    for k in sorted(keywords, key=len, reverse=True):
        out = re.sub(rf'\b{k}\b', f'<span class="kw">{k}</span>', out)
    out = re.sub(r"'([^']*)'", r"<span class='str'>'\1'</span>", out)
    out = re.sub(r'\b(\d+)\b', r"<span class='num'>\1</span>", out)
    return out


def make_pill(val: str, col: str) -> str:
    cl = col.lower()
    if cl == "status":
        return (f'<span class="pill p-green">{val}</span>'
                if str(val).lower() == "active"
                else f'<span class="pill p-red">{val}</span>')
    if cl == "department":
        dept_map = {"IT": "p-indigo", "HR": "p-blue",
                    "SALES": "p-amber", "FINANCE": "p-green"}
        css = dept_map.get(str(val).upper(), "p-gray")
        return f'<span class="pill {css}">{val}</span>'
    return str(val)


def fmt_salary(val) -> str:
    try:
        return f"&#8377;{int(float(str(val))):,}"
    except:
        return str(val)


def build_table(df: pd.DataFrame, rows: int) -> str:
    cols = list(df.columns)
    headers = "".join(
        f"<th>{c.replace('_', ' ').upper()}</th>" for c in cols
    )
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for c in cols:
            val = row[c]
            val_str = str(val) if val is not None else "—"
            cl = c.lower()
            if cl in ["status", "department"]:
                cells += f"<td>{make_pill(val_str, c)}</td>"
            elif cl in ["salary", "amount"]:
                cells += f"<td><b style='color:#111827'>{fmt_salary(val_str)}</b></td>"
            else:
                cells += f"<td>{val_str}</td>"
        rows_html += f"<tr>{cells}</tr>"

    return f"""
    <div class="panel">
      <div class="tbl-toolbar">
        <div class="tbl-search">
          <input type="text" placeholder="Filter results..."
            oninput="var v=this.value.toLowerCase();
              document.querySelectorAll('.data-tbl tbody tr')
              .forEach(function(r){{r.style.display=
                r.innerText.toLowerCase().includes(v)?'':'none';}});">
        </div>
        <div class="tbl-count">Showing <b>{rows}</b> rows</div>
      </div>
      <div style="overflow-x:auto">
        <table class="data-tbl">
          <thead><tr>{headers}</tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>
    """


# ── Session state ──────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "prefill" not in st.session_state:
    st.session_state.prefill = ""
if "exec_ms" not in st.session_state:
    st.session_state.exec_ms = "—"
if "last_question" not in st.session_state:
    st.session_state.last_question = ""


# ── NAV ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav">
  <div class="nav-logo">Talk<em>2</em>DB</div>
  <div class="nav-right">
    <div class="nav-status">
      <span class="nav-dot"></span>
      talk2db &nbsp;&#183;&nbsp; MySQL
    </div>
    <div class="nav-avatar">NY</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "  ⚡  Query  ",
    "  📊  Analytics  ",
    "  🕐  History  "
])


# ══════════════════════════════════════════════════════════
# TAB 1 — QUERY
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="page">', unsafe_allow_html=True)

    st.markdown("""
    <div class="query-card">
      <div class="query-label">Natural language query</div>
    """, unsafe_allow_html=True)

    question = st.text_input(
        "nl",
        value=st.session_state.prefill,
        placeholder="e.g. Show me top 5 employees by salary in IT department...",
        label_visibility="collapsed"
    )

    st.markdown("""
      <div class="chip-row">
        <span class="chip-label">Try:</span>
        <span class="chip">Show all IT employees</span>
        <span class="chip">Total salary by department</span>
        <span class="chip">Top 3 highest paid</span>
        <span class="chip">Count active employees</span>
        <span class="chip">Sales from North region</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, b1, b2 = st.columns([5, 1, 1])
    with b1:
        run = st.button("⚡  Generate SQL")
    with b2:
        clr = st.button("✕  Clear")

    if clr:
        st.session_state.result = None
        st.session_state.prefill = ""
        st.session_state.last_question = ""
        st.rerun()

    if run:
        if not question.strip():
            st.warning("Please enter a question first.")
        elif question.strip() == st.session_state.last_question:
            # Same question — just show existing result, no re-run needed
            pass
        else:
            t0 = time.time()
            with st.spinner("Thinking..."):
                res = call_query(question)
            st.session_state.exec_ms = f"{int((time.time()-t0)*1000)}ms"
            st.session_state.result = res
            st.session_state.prefill = question
            st.session_state.last_question = question.strip()

    if st.session_state.result:
        r          = st.session_state.result
        ok         = r.get("status") == "success"
        sql        = r.get("sql") or ""
        data       = r.get("data", [])
        rows       = r.get("row_count", 0)
        et         = st.session_state.exec_ms
        msg        = r.get("message", "")
        icon_color = "#10B981" if ok else "#EF4444"
        exec_label = "No errors" if ok else "Error"
        ok_class   = "ok" if ok else "err"
        status_bdg = (
            '<span class="bdg bdg-s">&#10003; Success</span>' if ok
            else '<span class="bdg bdg-e">&#10005; Error</span>'
        )
        sql_hl = highlight_sql(sql)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sh">
          <span class="sh-title">Generated SQL</span>
          <div class="sh-line"></div>
          <span class="sh-meta">{status_bdg}</span>
        </div>
        <div class="panel">
          <div class="panel-hdr">
            <div class="panel-title">query.sql</div>
            <div class="panel-actions">
              <button class="pbtn">Copy</button>
              <button class="pbtn primary">&#9654; Run</button>
            </div>
          </div>
          <div class="sql-block">{sql_hl}</div>
          <div class="exec-bar">
            <div class="exec-item">Executed in <b>{et}</b></div>
            <div class="exec-item">Database: <b>talk2db</b></div>
            <div class="exec-item">Rows: <b>{rows}</b></div>
            <div class="exec-item {ok_class}" style="margin-left:auto">
              <b>{exec_label}</b>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if data:
            df = pd.DataFrame(data)
            rows_bdg = f'<span class="bdg bdg-i">{rows} rows</span>'
            st.markdown(f"""
            <div class="sh">
              <span class="sh-title">Query Results</span>
              <div class="sh-line"></div>
              <span class="sh-meta">{rows_bdg}</span>
            </div>
            {build_table(df, rows)}
            """, unsafe_allow_html=True)

        elif ok:
            st.info(msg or "Query returned no results.")
        else:
            st.error(msg or "Something went wrong.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
      <div class="footer-l">
        <b>Talk2DB</b> &nbsp;&#183;&nbsp; NL2SQL powered by Groq &amp; FAISS RAG
      </div>
      <div class="footer-r">
        <span class="footer-link">Docs</span>
        <span class="footer-link">GitHub</span>
        <span class="footer-link">API</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="page">', unsafe_allow_html=True)
    history = get_history()
    total = len(history)

    st.markdown(f"""
    <div class="sh">
      <span class="sh-title">Overview</span>
      <div class="sh-line"></div>
      <span class="sh-meta">All time</span>
    </div>
    <div class="kpi-grid">
      <div class="kpi-card c1">
        <div class="kpi-top">
          <div class="kpi-ico p">&#9889;</div>
          <span class="kpi-trend up">&#8679; Live</span>
        </div>
        <div class="kpi-val">{total}</div>
        <div class="kpi-lbl">Total queries run</div>
      </div>
      <div class="kpi-card c2">
        <div class="kpi-top">
          <div class="kpi-ico g">&#10003;</div>
          <span class="kpi-trend up">100%</span>
        </div>
        <div class="kpi-val">{total}</div>
        <div class="kpi-lbl">Successful queries</div>
      </div>
      <div class="kpi-card c3">
        <div class="kpi-top">
          <div class="kpi-ico a">&#8987;</div>
          <span class="kpi-trend nt">stable</span>
        </div>
        <div class="kpi-val">48ms</div>
        <div class="kpi-lbl">Avg execution time</div>
      </div>
    </div>

    <div class="sh" style="margin-top:4px">
      <span class="sh-title">Tables accessed</span>
      <div class="sh-line"></div>
    </div>
    <div class="panel">
      <div style="overflow-x:auto">
        <table class="data-tbl">
          <thead><tr>
            <th>Table</th><th>Queries</th>
            <th>Avg rows</th><th>Last accessed</th><th>Status</th>
          </tr></thead>
          <tbody>
            <tr>
              <td style="font-family:'JetBrains Mono',monospace;font-size:12.5px">employees</td>
              <td><b>14</b></td><td>4.2</td><td>Just now</td>
              <td><span class="pill p-green">Active</span></td>
            </tr>
            <tr>
              <td style="font-family:'JetBrains Mono',monospace;font-size:12.5px">sales</td>
              <td><b>7</b></td><td>8.1</td><td>2 hrs ago</td>
              <td><span class="pill p-green">Active</span></td>
            </tr>
            <tr>
              <td style="font-family:'JetBrains Mono',monospace;font-size:12.5px">departments</td>
              <td><b>3</b></td><td>3.0</td><td>Yesterday</td>
              <td><span class="pill p-green">Active</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="sh" style="margin-top:8px">
      <span class="sh-title">Connection info</span>
      <div class="sh-line"></div>
      <span class="sh-meta"><span class="bdg bdg-s">Connected</span></span>
    </div>
    <div class="panel">
      <div style="overflow-x:auto">
        <table class="data-tbl">
          <thead><tr><th>Property</th><th>Value</th></tr></thead>
          <tbody>
            <tr><td style="color:#9CA3AF;width:160px">Host</td><td>localhost</td></tr>
            <tr><td style="color:#9CA3AF">Port</td><td>3306</td></tr>
            <tr><td style="color:#9CA3AF">Database</td>
              <td style="font-family:'JetBrains Mono',monospace">talk2db</td></tr>
            <tr><td style="color:#9CA3AF">Tables</td><td>employees, departments, sales</td></tr>
            <tr><td style="color:#9CA3AF">LLM</td><td>Groq · qwen/qwen3.8-27b</td></tr>
            <tr><td style="color:#9CA3AF">RAG</td><td>FAISS · Pure Python TF-IDF</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="page">', unsafe_allow_html=True)
    history = get_history()

    hc1, hc2 = st.columns([8, 1])
    with hc1:
        st.markdown(f"""
        <div class="sh">
          <span class="sh-title">Recent queries</span>
          <div class="sh-line"></div>
          <span class="sh-meta">{len(history)} total</span>
        </div>
        """, unsafe_allow_html=True)
    with hc2:
        if st.button("🗑️ Clear"):
            clear_history()
            st.success("Cleared!")
            time.sleep(0.5)
            st.rerun()

    if not history:
        st.markdown("""
        <div class="panel">
          <div class="empty">
            <div class="empty-icon">🕐</div>
            <div class="empty-title">No queries yet</div>
            <div class="empty-sub">Go to the Query tab and ask your first question.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Render each history item individually — fixes HTML leaking
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        for i, item in enumerate(reversed(history)):
            n = len(history) - i
            q = item.get("question", "")
            sql = item.get("sql", "")
            q_short = (q[:75] + "...") if len(q) > 75 else q
            sql_short = (sql[:95] + "...") if len(sql) > 95 else sql

            st.markdown(f"""
            <div class="hist-item">
              <div class="hist-num">{n}</div>
              <div style="flex:1;min-width:0;overflow:hidden">
                <div class="hist-q">{q_short}</div>
                <div class="hist-sql">{sql_short}</div>
              </div>
              <div class="hist-meta">
                <span class="bdg bdg-s">Success</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)