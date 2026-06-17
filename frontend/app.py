"""
Talk2DB — Frontend
Ask questions in plain English. Get answers from your database.

Run with: streamlit run frontend/app.py
"""

import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import time

# ──────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Talk2DB",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "query"
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_question" not in st.session_state:
    st.session_state.last_question = None
if "exec_time" not in st.session_state:
    st.session_state.exec_time = None
if "history_cache" not in st.session_state:
    st.session_state.history_cache = None
if "query_input_value" not in st.session_state:
    st.session_state.query_input_value = ""
if "schema_open" not in st.session_state:
    st.session_state.schema_open = True

# ──────────────────────────────────────────────────────────────────────────
# STYLES
# ──────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --ink: #0B0E14;
    --ink-soft: #151926;
    --indigo: #4F46E5;
    --indigo-soft: #EEF0FE;
    --green: #16A34A;
    --green-soft: #ECFDF3;
    --red: #DC2626;
    --red-soft: #FEF2F2;
    --slate: #64748B;
    --slate-light: #94A3B8;
    --panel: #F7F8FC;
    --border: #E4E7EE;
    --border-soft: #EDEFF5;
}

html, body, [class*="css"]  {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: #FFFFFF;
}

#MainMenu, header, footer {visibility: hidden;}
.block-container {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}
div[data-testid="stAppViewContainer"] > .main {
    padding-top: 0 !important;
}

/* ============ TOP NAV ============ */
div.st-key-top_nav {
    background: var(--ink);
    padding: 16px 40px 18px 40px;
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    margin-right: calc(-50vw + 50%);
    margin-top: 0;
    margin-bottom: 22px;
    border-radius: 0;
}
div.st-key-top_nav div[data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important;
}
.t2db-wordmark {
    color: #FFFFFF;
    font-weight: 800;
    font-size: 26px;
    letter-spacing: -0.025em;
    padding-top: 3px;
}
div.st-key-top_nav .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #8B92A8 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 7px 14px !important;
    box-shadow: none !important;
}
div.st-key-top_nav .stButton > button:hover {
    color: #FFFFFF !important;
    background: rgba(255,255,255,0.06) !important;
}
.t2db-navbtn-active .stButton > button {
    background: rgba(255,255,255,0.1) !important;
    color: #FFFFFF !important;
}
.t2db-status {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    font-size: 12px;
    color: #8B92A8;
    font-family: 'JetBrains Mono', monospace;
    padding-top: 11px;
}
.t2db-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #34D399;
    box-shadow: 0 0 0 3px rgba(52,211,153,0.15);
}

/* ============ PAGE HEADER ============ */
.t2db-pagehead {
    padding: 28px 0 18px 0;
}
.t2db-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    font-weight: 600;
    color: var(--indigo);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.t2db-title {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em !important;
    margin: 0 !important;
    -webkit-text-fill-color: var(--ink) !important;
    opacity: 1 !important;
    line-height: 1.3 !important;
}
.t2db-sub {
    font-size: 14px;
    color: var(--slate);
    margin-top: 4px;
}

/* ============ EXEC BAR ============ */
.t2db-exec-container {
    background: var(--ink);
    border-radius: 12px;
    padding: 6px 10px;
}
div.st-key-exec_bar {
    background: var(--ink);
    border-radius: 12px;
    padding: 10px 10px 10px 16px;
    margin-bottom: 6px;
}
div.st-key-exec_bar div[data-testid="stTextInput"] input {
    padding-left: 0 !important;
}

div[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    color: #FFFFFF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14.5px !important;
    padding: 10px 4px !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #5B6478 !important;
}
div[data-testid="stTextInput"] > div {
    background: transparent !important;
    border: none !important;
}
div[data-testid="stTextInput"] > div > div {
    border: none !important;
}

.stButton > button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    letter-spacing: -0.01em;
    transition: all 0.15s ease;
}
.t2db-runbtn button {
    background: var(--indigo) !important;
    color: white !important;
    border: none !important;
    padding: 10px 22px !important;
}
.t2db-runbtn button:hover {
    background: #4338CA !important;
}
.t2db-ghostbtn button {
    background: transparent !important;
    color: var(--slate) !important;
    border: 1px solid var(--border) !important;
    padding: 9px 16px !important;
}
.t2db-ghostbtn button:hover {
    border-color: var(--slate-light) !important;
    color: var(--ink) !important;
}

/* ============ STATUS LINE ============ */
.t2db-statusline {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 4px 18px 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
}
.t2db-stat-ok { color: var(--green); font-weight: 600; }
.t2db-stat-err { color: var(--red); font-weight: 600; }
.t2db-stat-dim { color: var(--slate-light); }

/* ============ CHIP ROW (sample questions) ============ */
.t2db-chiprow {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 2px 0 26px 0;
}

/* ============ PANELS ============ */
.t2db-panel {
    background: var(--panel);
    border: 1px solid var(--border-soft);
    border-radius: 12px;
    padding: 20px;
}
.t2db-panel-title {
    font-size: 12px;
    font-weight: 700;
    color: var(--slate);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 7px;
}

/* ============ SCHEMA TREE ============ */
.t2db-schema-table {
    margin-bottom: 14px;
}
.t2db-schema-tname {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: var(--ink);
    background: var(--indigo-soft);
    display: inline-block;
    padding: 3px 9px;
    border-radius: 6px;
    margin-bottom: 7px;
}
.t2db-schema-col {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--slate);
    padding: 3px 0 3px 10px;
    border-left: 2px solid var(--border);
    margin-left: 4px;
}
.t2db-schema-col b { color: var(--ink); font-weight: 600; }

/* ============ SQL BLOCK ============ */
.t2db-sqlblock {
    background: var(--ink);
    border-radius: 10px;
    padding: 16px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #E2E4F1;
    overflow-x: auto;
    margin-bottom: 4px;
}
.t2db-sql-kw { color: #818CF8; font-weight: 700; }
.t2db-sql-str { color: #86EFAC; }
.t2db-sql-num { color: #FCA5A5; }
.t2db-sql-fn { color: #67E8F9; }

/* ============ RESULT TABLE ============ */
.t2db-table-wrap {
    border: 1px solid var(--border-soft);
    border-radius: 12px;
    overflow: hidden;
    margin-top: 4px;
}
.t2db-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.t2db-table thead th {
    background: var(--panel);
    color: var(--slate);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    text-align: left;
    padding: 11px 16px;
    border-bottom: 1px solid var(--border);
}
.t2db-table tbody td {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-soft);
    color: var(--ink);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
}
.t2db-table tbody tr:last-child td { border-bottom: none; }
.t2db-table tbody tr:hover { background: #FAFBFD; }

/* ============ PILLS ============ */
.t2db-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.t2db-pill-active { background: var(--green-soft); color: var(--green); }
.t2db-pill-resigned { background: var(--red-soft); color: var(--red); }
.t2db-pill-pending { background: #FEF9C3; color: #A16207; }
.t2db-pill-default { background: var(--indigo-soft); color: var(--indigo); }

/* ============ EMPTY STATE ============ */
.t2db-empty {
    text-align: center;
    padding: 70px 20px;
    color: var(--slate-light);
}
.t2db-empty-glyph {
    font-size: 30px;
    color: var(--border);
    margin-bottom: 14px;
}
.t2db-empty-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--slate);
    margin-bottom: 4px;
}
.t2db-empty-sub {
    font-size: 13px;
    color: var(--slate-light);
}

/* ============ METRIC CARDS ============ */
.t2db-metric {
    background: var(--panel);
    border: 1px solid var(--border-soft);
    border-radius: 12px;
    padding: 18px 20px;
}
.t2db-metric-label {
    font-size: 11.5px;
    font-weight: 700;
    color: var(--slate);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.t2db-metric-value {
    font-size: 26px;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: -0.02em;
}
.t2db-metric-delta {
    font-size: 12px;
    color: var(--green);
    font-weight: 600;
    margin-top: 4px;
}

/* ============ HISTORY ROW ============ */
.t2db-histrow {
    border: 1px solid var(--border-soft);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    background: #FFFFFF;
}
.t2db-histrow:hover { border-color: var(--slate-light); }
.t2db-hist-q {
    font-size: 14px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 6px;
}
.t2db-hist-meta {
    display: flex;
    gap: 14px;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--slate-light);
}

/* Divider */
.t2db-divider {
    height: 1px;
    background: var(--border-soft);
    margin: 24px 0;
}

/* Hide streamlit's default tab look entirely since we build our own nav */
div[data-testid="stHorizontalBlock"] { gap: 12px; }

/* Selectbox / general widget polish */
div[data-baseweb="select"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# API HELPERS
# ──────────────────────────────────────────────────────────────────────────

def run_query(question: str):
    try:
        t0 = time.time()
        resp = requests.post(f"{API_BASE}/query", json={"question": question}, timeout=60)
        elapsed = round((time.time() - t0) * 1000)
        if resp.status_code == 200:
            return resp.json(), elapsed, None
        else:
            return None, elapsed, f"Server returned {resp.status_code}"
    except requests.exceptions.ConnectionError:
        return None, None, "Can't reach the backend. Make sure FastAPI is running on port 8000."
    except requests.exceptions.Timeout:
        return None, None, "The query took too long to respond."
    except Exception as e:
        return None, None, str(e)


def fetch_history():
    try:
        resp = requests.get(f"{API_BASE}/history", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def clear_history():
    try:
        resp = requests.delete(f"{API_BASE}/history", timeout=10)
        return resp.status_code == 200
    except Exception:
        return False


def get_schema():
    """Static fallback schema shown in the rail. Replace with a live /schema
    endpoint call if you add one to main.py — kept static here so the UI
    renders even before the backend route exists."""
    return {
        "employees": ["id (PK)", "name", "department_id (FK)", "salary", "status"],
        "departments": ["id (PK)", "name", "manager"],
        "sales": ["id (PK)", "employee_id (FK)", "amount", "sale_date"],
    }


# ──────────────────────────────────────────────────────────────────────────
# SQL SYNTAX HIGHLIGHT (lightweight, no extra deps)
# ──────────────────────────────────────────────────────────────────────────

SQL_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "JOIN", "INNER", "LEFT", "RIGHT", "ON",
    "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "AS", "AND", "OR", "NOT",
    "IN", "BETWEEN", "LIKE", "IS", "NULL", "DESC", "ASC", "DISTINCT",
    "COUNT", "SUM", "AVG", "MAX", "MIN", "CASE", "WHEN", "THEN", "ELSE", "END"
]

def highlight_sql(sql: str) -> str:
    import re
    escaped = sql.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # strings
    escaped = re.sub(r"('[^']*')", r'<span class="t2db-sql-str">\1</span>', escaped)
    # numbers
    escaped = re.sub(r"(?<![\w])(\d+)(?![\w])", r'<span class="t2db-sql-num">\1</span>', escaped)
    # keywords
    for kw in sorted(SQL_KEYWORDS, key=len, reverse=True):
        escaped = re.sub(
            rf"(?<![\w]){kw}(?![\w])",
            f'<span class="t2db-sql-kw">{kw}</span>',
            escaped,
            flags=re.IGNORECASE,
        )
    return escaped


def status_pill(value: str) -> str:
    v = str(value).strip().lower()
    if v in ("active", "completed", "approved"):
        cls = "t2db-pill-active"
    elif v in ("resigned", "rejected", "failed", "inactive"):
        cls = "t2db-pill-resigned"
    elif v in ("pending", "in progress", "review"):
        cls = "t2db-pill-pending"
    else:
        return None
    return f'<span class="t2db-pill {cls}">{value}</span>'


def render_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    cols = list(df.columns)
    html = '<div class="t2db-table-wrap"><table class="t2db-table"><thead><tr>'
    for c in cols:
        html += f"<th>{c}</th>"
    html += "</tr></thead><tbody>"
    status_like_cols = {c for c in cols if c.lower() in ("status", "state")}
    for _, row in df.head(max_rows).iterrows():
        html += "<tr>"
        for c in cols:
            val = row[c]
            if c in status_like_cols:
                pill = status_pill(val)
                cell = pill if pill else str(val)
            else:
                cell = str(val)
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    return html


# ──────────────────────────────────────────────────────────────────────────
# TOP NAV
# ──────────────────────────────────────────────────────────────────────────

tabs = [("query", "Query"), ("analytics", "Analytics"), ("history", "History")]

with st.container(key="top_nav"):
    logo_col, nav_col, spacer_col = st.columns([0.26, 0.48, 0.26])
    with logo_col:
        st.markdown('<div class="t2db-wordmark">Talk2DB</div>', unsafe_allow_html=True)
    with nav_col:
        nav_btn_cols = st.columns(len(tabs))
        for i, (key, label) in enumerate(tabs):
            with nav_btn_cols[i]:
                is_active = st.session_state.active_tab == key
                btn_class = "t2db-navbtn-active" if is_active else "t2db-navbtn"
                st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
                if st.button(label, key=f"navbtn_{key}", use_container_width=True):
                    st.session_state.active_tab = key
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    with spacer_col:
        st.markdown('<div class="t2db-status"><div class="t2db-dot"></div>talk2db</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB: QUERY
# ──────────────────────────────────────────────────────────────────────────

if st.session_state.active_tab == "query":

    st.markdown("""
    <div class="t2db-pagehead">
        <div class="t2db-eyebrow">Query Console</div>
        <h1 class="t2db-title">Ask your database anything</h1>
        <div class="t2db-sub">Plain English in, SQL and results out — no query syntax required.</div>
    </div>
    """, unsafe_allow_html=True)

    rail_col, main_col = st.columns([0.27, 0.73], gap="medium")

    # ---- SCHEMA RAIL ----
    with rail_col:
        schema = get_schema()
        schema_html = '<div class="t2db-panel"><div class="t2db-panel-title">◆ Connected schema</div>'
        for table, cols in schema.items():
            schema_html += f'<div class="t2db-schema-table"><div class="t2db-schema-tname">{table}</div>'
            for c in cols:
                if "(" in c:
                    name, tag = c.split(" (", 1)
                    schema_html += f'<div class="t2db-schema-col"><b>{name}</b> · {tag.rstrip(")")}</div>'
                else:
                    schema_html += f'<div class="t2db-schema-col">{c}</div>'
            schema_html += '</div>'
        schema_html += '</div>'
        st.markdown(schema_html, unsafe_allow_html=True)

    # ---- MAIN QUERY AREA ----
    with main_col:
        with st.container(key="exec_bar"):
            input_col, btn_col = st.columns([0.85, 0.15])
            with input_col:
                question = st.text_input(
                    "question",
                    placeholder="❯ e.g. Which department has the highest average salary?",
                    label_visibility="collapsed",
                    value=st.session_state.query_input_value,
                    key="question_input",
                )
            with btn_col:
                st.markdown('<div class="t2db-runbtn">', unsafe_allow_html=True)
                run_clicked = st.button("Run  ↵", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Sample question chips
        samples = [
            "Top 5 highest paid employees",
            "Total sales by department",
            "Employees who resigned this year",
            "Average salary per department",
        ]
        chip_cols = st.columns(len(samples))
        for i, s in enumerate(samples):
            with chip_cols[i]:
                st.markdown('<div class="t2db-ghostbtn">', unsafe_allow_html=True)
                if st.button(s, key=f"chip_{i}", use_container_width=True):
                    st.session_state.query_input_value = s
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ---- EXECUTE ----
        if run_clicked and question.strip():
            with st.spinner(""):
                result, elapsed, error = run_query(question.strip())
            st.session_state.last_result = result
            st.session_state.last_question = question.strip()
            st.session_state.exec_time = elapsed
            st.session_state.last_error = error

        # ---- STATUS LINE ----
        if st.session_state.get("last_result") or st.session_state.get("last_error"):
            if st.session_state.get("last_error"):
                st.markdown(f"""
                <div class="t2db-statusline">
                    <span class="t2db-stat-err">● failed</span>
                    <span class="t2db-stat-dim">{st.session_state.last_error}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                result = st.session_state.last_result
                status = result.get("status", "success") if isinstance(result, dict) else "success"
                row_count = 0
                if isinstance(result, dict) and result.get("data") is not None:
                    try:
                        row_count = len(result["data"])
                    except Exception:
                        row_count = 0
                if status == "success" or status == "ok":
                    st.markdown(f"""
                    <div class="t2db-statusline">
                        <span class="t2db-stat-ok">● executed</span>
                        <span class="t2db-stat-dim">{row_count} rows returned</span>
                        <span class="t2db-stat-dim">{st.session_state.exec_time} ms</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    msg = result.get("message", "Could not execute query") if isinstance(result, dict) else "Could not execute query"
                    st.markdown(f"""
                    <div class="t2db-statusline">
                        <span class="t2db-stat-err">● blocked</span>
                        <span class="t2db-stat-dim">{msg}</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('<div class="t2db-divider"></div>', unsafe_allow_html=True)

        # ---- RESULTS AREA ----
        if st.session_state.get("last_result") and not st.session_state.get("last_error"):
            result = st.session_state.last_result
            sql = result.get("sql", "") if isinstance(result, dict) else ""

            if sql:
                st.markdown('<div class="t2db-panel-title">◆ Generated SQL</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="t2db-sqlblock">{highlight_sql(sql)}</div>', unsafe_allow_html=True)
                st.write("")

            data = result.get("data") if isinstance(result, dict) else None
            if data:
                try:
                    df = pd.DataFrame(data)
                    top_l, top_r = st.columns([0.5, 0.5])
                    with top_l:
                        st.markdown('<div class="t2db-panel-title">◆ Results</div>', unsafe_allow_html=True)
                    with top_r:
                        search = st.text_input(
                            "filter", placeholder="Filter results…",
                            label_visibility="collapsed", key="result_filter"
                        )
                    if search:
                        mask = df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
                        df_show = df[mask]
                    else:
                        df_show = df
                    st.markdown(render_table(df_show), unsafe_allow_html=True)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download CSV", csv,
                        file_name=f"talk2db_result_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                    )
                except Exception:
                    st.json(data)
            elif sql:
                st.markdown("""
                <div class="t2db-empty">
                    <div class="t2db-empty-glyph">∅</div>
                    <div class="t2db-empty-title">Query ran, but returned nothing</div>
                    <div class="t2db-empty-sub">Try widening your filters or rephrasing the question.</div>
                </div>
                """, unsafe_allow_html=True)

        elif not st.session_state.get("last_error"):
            st.markdown("""
            <div class="t2db-empty">
                <div class="t2db-empty-glyph">❯</div>
                <div class="t2db-empty-title">No query run yet</div>
                <div class="t2db-empty-sub">Type a question above or pick one of the samples to get started.</div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB: ANALYTICS
# ──────────────────────────────────────────────────────────────────────────

elif st.session_state.active_tab == "analytics":

    st.markdown("""
    <div class="t2db-pagehead">
        <div class="t2db-eyebrow">Usage</div>
        <h1 class="t2db-title">Analytics</h1>
        <div class="t2db-sub">A quick read on how the console is being used.</div>
    </div>
    """, unsafe_allow_html=True)

    history = fetch_history()
    entries = history.get("history", []) if isinstance(history, dict) else (history or [])

    total_queries = len(entries) if entries else 0
    success_count = sum(1 for e in entries if e.get("status", "success") in ("success", "ok")) if entries else 0
    success_rate = round((success_count / total_queries) * 100) if total_queries else 0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="t2db-metric">
            <div class="t2db-metric-label">Total Queries</div>
            <div class="t2db-metric-value">{total_queries}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="t2db-metric">
            <div class="t2db-metric-label">Success Rate</div>
            <div class="t2db-metric-value">{success_rate}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="t2db-metric">
            <div class="t2db-metric-label">Tables Indexed</div>
            <div class="t2db-metric-value">3</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    if entries:
        st.markdown('<div class="t2db-panel-title">◆ Most recent activity</div>', unsafe_allow_html=True)
        for e in entries[:5]:
            q = e.get("question", "—")
            ts = e.get("timestamp", "")
            st.markdown(f"""
            <div class="t2db-histrow">
                <div class="t2db-hist-q">{q}</div>
                <div class="t2db-hist-meta">{ts}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="t2db-empty">
            <div class="t2db-empty-glyph">▦</div>
            <div class="t2db-empty-title">No activity yet</div>
            <div class="t2db-empty-sub">Run a few queries from the Query tab and check back here.</div>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB: HISTORY
# ──────────────────────────────────────────────────────────────────────────

elif st.session_state.active_tab == "history":

    head_l, head_r = st.columns([0.7, 0.3])
    with head_l:
        st.markdown("""
        <div class="t2db-pagehead">
            <div class="t2db-eyebrow">Past Runs</div>
            <h1 class="t2db-title">Query History</h1>
            <div class="t2db-sub">Every question you've asked, and what came back.</div>
        </div>
        """, unsafe_allow_html=True)
    with head_r:
        st.write("")
        st.write("")
        st.markdown('<div class="t2db-ghostbtn">', unsafe_allow_html=True)
        if st.button("Clear all history", use_container_width=True):
            if clear_history():
                st.session_state.history_cache = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    history = fetch_history()
    entries = history.get("history", []) if isinstance(history, dict) else (history or [])

    if entries:
        for e in reversed(entries):
            q = e.get("question", "—")
            sql = e.get("sql", "")
            ts = e.get("timestamp", "")
            status = e.get("status", "success")
            badge = '<span class="t2db-stat-ok">● success</span>' if status in ("success", "ok") else '<span class="t2db-stat-err">● failed</span>'
            st.markdown(f"""
            <div class="t2db-histrow">
                <div class="t2db-hist-q">{q}</div>
                <div class="t2db-hist-meta">{badge}<span>{ts}</span></div>
            </div>
            """, unsafe_allow_html=True)
            if sql:
                with st.expander("View SQL", expanded=False):
                    st.markdown(f'<div class="t2db-sqlblock">{highlight_sql(sql)}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="t2db-empty">
            <div class="t2db-empty-glyph">◷</div>
            <div class="t2db-empty-title">History is empty</div>
            <div class="t2db-empty-sub">Queries you run will show up here automatically.</div>
        </div>
        """, unsafe_allow_html=True)