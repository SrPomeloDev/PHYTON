COLORS = {
    # â”€â”€ Core brand â”€â”€
    "primary": "#6366F1",        # Indigo vibrante
    "secondary": "#8B5CF6",      # PÃºrpura
    "accent": "#06B6D4",         # Cyan
    "success": "#10B981",        # Emerald
    "warning": "#F59E0B",        # Amber
    "danger": "#EF4444",         # Red
    "info": "#3B82F6",           # Blue
    "purple": "#A855F7",         # Purple bright

    # â”€â”€ Backgrounds â”€â”€
    "bg_page": "#0B0F19",
    "bg_card": "rgba(255,255,255,0.04)",
    "bg_card_solid": "#111827",
    "bg_card_hover": "rgba(255,255,255,0.07)",
    "bg_surface": "#111827",

    # â”€â”€ Text â”€â”€
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",

    # â”€â”€ Borders â”€â”€
    "border": "rgba(255,255,255,0.08)",
    "border_hover": "rgba(255,255,255,0.15)",
    "border_accent": "rgba(99,102,241,0.4)",

    # â”€â”€ Tints (for KPI backgrounds) â”€â”€
    "blue_light": "rgba(99,102,241,0.12)",
    "green_light": "rgba(16,185,129,0.12)",
    "orange_light": "rgba(245,158,11,0.12)",
    "red_light": "rgba(239,68,68,0.12)",
    "cyan_light": "rgba(6,182,212,0.12)",
    "purple_light": "rgba(168,85,247,0.12)",

    # â”€â”€ Sidebar â”€â”€
    "sidebar_bg": "#070B14",
    "sidebar_text": "#CBD5E1",

    # â”€â”€ Header â”€â”€
    "header_gradient_start": "#0B0F19",
    "header_gradient_end": "#1E1B4B",

    # â”€â”€ New premium accent â”€â”€
    "primary_light": "#818CF8",
    "accent_hover": "#0891B2",
    "success_hover": "#059669",
    "warning_hover": "#D97706",
    "danger_hover": "#DC2626",
    "shadow_sm": "0 1px 3px rgba(0,0,0,0.3)",
    "shadow_md": "0 4px 12px rgba(0,0,0,0.4)",
    "shadow_lg": "0 8px 30px rgba(0,0,0,0.5)",
}

CHART_COLORS = [
    "#6366F1",  # Indigo
    "#06B6D4",  # Cyan
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#EF4444",  # Red
    "#A855F7",  # Purple
    "#3B82F6",  # Blue
    "#EC4899",  # Pink
    "#14B8A6",  # Teal
    "#F97316",  # Orange
]

# Assign a fixed color to each segment so the donut always uses the same palette.
# Edit the hex values below to change colors — no need to touch the chart code.
SEGMENT_COLORS = {
    "Retail":            "#6366F1",  # Indigo
    "Cliente Frecuente": "#06B6D4",  # Cyan
    "Mayorista":         "#10B981",  # Emerald
    "Corporativo":       "#F59E0B",  # Amber
    "Nuevo":             "#A855F7",  # Purple
}

FONT_FAMILY = "'Plus Jakarta Sans', Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

PLOTLY_TEMPLATE = "plotly_dark"

import streamlit as st
import streamlit.components.v1 as components

def apply_theme():
    """Inject global CSS and the mouse follower JS script."""
    st.markdown(inject_css(), unsafe_allow_html=True)
    components.html("""
<script>
    (function() {
        var win = window.parent;
        var doc = win.document;
        
        if (win.__mouseFollowerRAF) {
            cancelAnimationFrame(win.__mouseFollowerRAF);
            win.__mouseFollowerRAF = null;
        }
        
        var old = doc.getElementById('mc-aura');
        if (old) old.remove();
        
        // ── CONFIG ──────────────────────────────────
        var AURA_SIZE     = 140;   // px (diameter)
        var FOLLOW_SPEED  = 0.18;  // 0-1: higher = snappier
        // ────────────────────────────────────────────
        
        var aura = doc.createElement('div');
        aura.id = 'mc-aura';
        aura.style.cssText = 'position:fixed;width:' + AURA_SIZE + 'px;height:' + AURA_SIZE + 'px;border-radius:50%;background:radial-gradient(circle, rgba(99,102,241,0.10) 0%, rgba(168,85,247,0.03) 50%, transparent 70%);pointer-events:none;z-index:99999;transform:translate(-50%,-50%);will-change:transform;';
        doc.body.appendChild(aura);
        
        doc.body.style.cursor = '';
        
        var mx = window.innerWidth / 2;
        var my = window.innerHeight / 2;
        var ax = mx, ay = my;
        var half = AURA_SIZE / 2;
        
        doc.onmousemove = function(e) {
            mx = e.clientX;
            my = e.clientY;
        };
        
        function update() {
            ax += (mx - ax) * FOLLOW_SPEED;
            ay += (my - ay) * FOLLOW_SPEED;
            aura.style.transform = 'translate3d(' + (ax - half) + 'px, ' + (ay - half) + 'px, 0)';
            win.__mouseFollowerRAF = requestAnimationFrame(update);
        }
        win.__mouseFollowerRAF = requestAnimationFrame(update);
    })();
</script>
    """, height=0, width=0)

def inject_css() -> str:
    c = COLORS
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

        /* â”€â”€ Design Tokens â”€â”€ */
        :root {{
            --font: {FONT_FAMILY};
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.35);
            --shadow-md: 0 4px 14px rgba(0,0,0,0.40);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.45);
            --shadow-xl: 0 20px 60px rgba(0,0,0,0.50);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        /* â”€â”€ Keyframe Animations â”€â”€ */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(16px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulse-glow {{
            0%, 100% {{ box-shadow: 0 0 8px rgba(99,102,241,0.15); }}
            50% {{ box-shadow: 0 0 20px rgba(99,102,241,0.35); }}
        }}
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        @keyframes breathe {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}

        /* â”€â”€ Global â”€â”€ */
        html, body, [class*="css"] {{
            font-family: var(--font);
        }}
        .stApp {{
            background-color: {c['bg_page']} !important;
            background-image: 
                radial-gradient(rgba(255,255,255, 0.1) 1px, transparent 1px),
                radial-gradient(circle at 50% 0%, rgba(30,27,75,0.4) 0%, transparent 60%) !important;
            background-size: 32px 32px, 100% 100% !important;
            background-attachment: fixed !important;
        }}

        /* â”€â”€ Scrollbar â”€â”€ */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.02); }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,0.18); }}

        /* â”€â”€ Main Container â”€â”€ */
        .main .block-container {{
            padding-top: 0.8rem !important;
            padding-bottom: 2rem !important;
            max-width: 1440px;
        }}

        /* â”€â”€ Hide Streamlit chrome â”€â”€ */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{
            background: transparent !important; border-bottom: none !important;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           PAGE HEADER
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .page-header {{
            display: flex; align-items: center; gap: 0.85rem;
            margin-bottom: 1.2rem; padding-bottom: 1rem;
            border-bottom: 1px solid {c['border']};
        }}
        .page-header-icon {{
            width: 44px; height: 44px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.25rem; flex-shrink: 0;
            box-shadow: 0 4px 20px rgba(99,102,241,0.2);
        }}
        .page-header-title {{
            font-size: 1.5rem; font-weight: 800;
            color: {c['text_primary']}; letter-spacing: -0.5px; line-height: 1.2;
        }}
        .page-header-subtitle {{
            color: {c['text_muted']}; font-size: 0.82rem; margin-top: 0.15rem;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           SECTION TITLES & DIVIDER
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .section-title {{
            font-size: 1.1rem; font-weight: 800;
            color: {c['text_primary']}; margin: 1.5rem 0 0.5rem 0;
            letter-spacing: -0.3px; display: flex; align-items: center; gap: 0.5rem;
        }}
        .section-subtitle {{
            font-size: 0.78rem; color: {c['text_muted']}; margin-bottom: 0.8rem;
        }}
        .section-divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), rgba(6,182,212,0.2), transparent);
            margin: 1.5rem 0; border: none;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           BUTTONS â€” Premium
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .stButton button {{
            border-radius: 10px; font-weight: 600; font-size: 0.82rem;
            border: 1px solid {c['border']};
            background: rgba(255,255,255,0.04);
            color: {c['text_primary']};
            transition: all var(--transition);
            letter-spacing: 0.3px;
            backdrop-filter: blur(4px);
        }}
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md), 0 0 24px rgba(99,102,241,0.12);
            border-color: {c['primary']};
            background: rgba(99,102,241,0.12);
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           CHART PANELS â€” Glassmorphism
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        div[data-testid="stPlotlyChart"] {{
            background: rgba(255,255,255,0.025);
            border: 1px solid {c['border']};
            border-radius: var(--radius-lg);
            padding: 0.5rem 0.75rem 0.25rem 0.75rem;
            margin-bottom: 0.75rem;
            overflow: hidden;
            transition: all var(--transition);
        }}
        div[data-testid="stPlotlyChart"]:hover {{
            border-color: rgba(99,102,241,0.25);
            box-shadow: var(--shadow-lg);
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           KPI CARDS â€” Premium / Glassmorphism
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .kpi-premium {{
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {c['border']};
            border-radius: var(--radius-lg);
            padding: 1rem 1.2rem;
            margin-bottom: 0.6rem;
            position: relative;
            overflow: hidden;
            transition: all var(--transition);
            animation: fadeInUp 0.5s ease-out both;
        }}
        .kpi-premium::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            opacity: 0;
            transition: all var(--transition);
        }}
        .kpi-premium:hover {{
            border-color: rgba(99,102,241,0.25);
            box-shadow: var(--shadow-lg);
            transform: translateY(-3px);
        }}
        .kpi-premium:hover::before {{
            opacity: 1;
        }}
        .kpi-premium .kpi-glow {{
            position: absolute;
            top: -50%; right: -20%;
            width: 120px; height: 120px;
            border-radius: 50%;
            pointer-events: none;
            transition: all var(--transition);
        }}
        .kpi-premium:hover .kpi-glow {{
            transform: scale(1.3);
        }}
        .kpi-premium .kpi-icon-box {{
            width: 38px; height: 38px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem; flex-shrink: 0;
        }}
        .kpi-premium .kpi-label-text {{
            color: {c['text_muted']};
            font-size: 0.65rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.8px;
            margin-bottom: 0.2rem;
        }}
        .kpi-premium .kpi-value-text {{
            color: {c['text_primary']};
            font-size: 1.7rem; font-weight: 800; line-height: 1.1;
            font-variant-numeric: tabular-nums; letter-spacing: -0.5px;
        }}
        .kpi-premium .kpi-trend-badge {{
            display: inline-flex; align-items: center; gap: 0.2rem;
            font-size: 0.7rem; font-weight: 700;
            padding: 0.15rem 0.5rem; border-radius: 20px;
            margin-top: 0.2rem;
        }}
        .kpi-premium .kpi-sub {{
            color: {c['text_muted']}; font-size: 0.65rem; margin-top: 0.2rem; font-weight: 400;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           DATAFRAMES
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {c['border']};
            border-radius: 14px; overflow: hidden;
            box-shadow: var(--shadow-sm);
            font-size: 0.82rem;
            background: {c['bg_card_solid']};
        }}
        div[data-testid="stDataFrame"] thead tr th {{
            background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.1)) !important;
            font-weight: 700 !important; font-size: 0.72rem !important;
            text-transform: uppercase !important; letter-spacing: 0.6px !important;
            color: {c['text_primary']} !important;
            padding: 0.65rem 0.8rem !important;
            border-bottom: 1px solid {c['border']} !important;
        }}
        div[data-testid="stDataFrame"] tbody tr td {{
            padding: 0.5rem 0.8rem !important;
            border-bottom: 1px solid {c['border']};
            color: {c['text_secondary']};
            background: transparent;
        }}
        div[data-testid="stDataFrame"] tbody tr:nth-child(even) td {{
            background: rgba(255,255,255,0.015);
        }}
        div[data-testid="stDataFrame"] tbody tr:hover td {{
            background: rgba(99,102,241,0.06) !important;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           SELECT / MULTISELECT
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .stMultiSelect div[data-baseweb="select"] > div,
        .stSelectbox div[data-baseweb="select"] > div {{
            border-radius: 10px; border-color: {c['border']};
            background: rgba(255,255,255,0.04);
            min-height: 38px; color: {c['text_primary']};
            transition: all var(--transition);
        }}
        .stMultiSelect div[data-baseweb="select"] > div:hover,
        .stMultiSelect div[data-baseweb="select"] > div:focus-within,
        .stSelectbox div[data-baseweb="select"] > div:hover {{
            border-color: {c['primary']};
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           TABS
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem; border-bottom: 1px solid {c['border']};
            background: transparent;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-weight: 500; font-size: 0.85rem; color: {c['text_muted']};
            border-radius: 8px 8px 0 0; padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: {c['text_primary']}; background: rgba(255,255,255,0.04);
        }}
        .stTabs [aria-selected="true"] {{
            color: {c['primary']} !important;
            border-bottom: 2px solid {c['primary']} !important;
            background: rgba(99,102,241,0.08) !important;
            font-weight: 600 !important;
        }}
        .stTabs [data-baseweb="tab-panel"] {{
            background: rgba(255,255,255,0.015);
            border: 1px solid {c['border']};
            border-top: none;
            border-radius: 0 0 12px 12px;
            padding: 1rem 0.8rem;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           PROGRESS ROWS
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .progress-row {{
            background: rgba(255,255,255,0.03);
            border: 1px solid {c['border']};
            border-radius: 12px; padding: 0.85rem 1rem;
            margin-bottom: 0.5rem;
            display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
        }}
        .progress-label {{
            min-width: 100px; font-weight: 700; color: {c['text_primary']}; font-size: 0.85rem;
        }}
        .progress-track {{
            flex: 1; min-width: 120px;
            background: rgba(255,255,255,0.04); border-radius: 8px; height: 10px; overflow: hidden;
        }}
        .progress-fill {{
            height: 100%; border-radius: 8px; transition: width 0.8s ease;
        }}
        .progress-pct {{
            min-width: 56px; text-align: right; font-weight: 800; font-size: 0.9rem;
        }}
        .progress-detail {{
            min-width: 140px; text-align: right; color: {c['text_muted']}; font-size: 0.72rem;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           ALERTS / EXPANDERS / SPINNER / CAPTIONS
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        div[data-testid="stAlert"] {{
            border-radius: 12px !important; border: 1px solid {c['border']} !important;
            background: rgba(255,255,255,0.03) !important; font-size: 0.85rem !important;
        }}
        div[data-testid="stAlert"] [data-testid="stAlertContainer"] {{
            padding: 0.75rem 1rem !important;
        }}
        div[data-testid="stExpander"] {{
            background: rgba(255,255,255,0.02);
            border: 1px solid {c['border']}; border-radius: 14px; overflow: hidden;
        }}
        div[data-testid="stExpander"] summary {{
            font-weight: 600 !important; color: {c['text_secondary']} !important; font-size: 0.85rem !important;
        }}
        div[data-testid="stSpinner"] > div {{
            border-top-color: {c['primary']} !important;
        }}
        .stCaption, small {{
            color: {c['text_muted']} !important; font-size: 0.75rem !important;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           DOWNLOAD BUTTON
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .stDownloadButton button {{
            border-radius: 10px !important; font-weight: 600 !important;
            background: rgba(99,102,241,0.12) !important;
            border: 1px solid rgba(99,102,241,0.3) !important;
            color: {c['text_primary']} !important;
            transition: all var(--transition) !important;
        }}
        .stDownloadButton button:hover {{
            background: rgba(99,102,241,0.25) !important;
            border-color: {c['primary']} !important;
            transform: translateY(-1px) !important;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           SIDEBAR â€” Premium
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {c['sidebar_bg']} 0%, #0A0E1A 100%) !important;
            border-right: 1px solid rgba(99,102,241,0.12);
        }}
        section[data-testid="stSidebar"] > div {{
            background: transparent !important;
        }}
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {{
            color: {c['sidebar_text']} !important;
        }}
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background-color: rgba(255,255,255,0.06);
            border-color: rgba(255,255,255,0.1); color: white;
            border-radius: 10px; transition: all var(--transition);
        }}
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
            border-color: {c['primary']}; background-color: rgba(255,255,255,0.08);
        }}
        section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {{
            background: linear-gradient(135deg, {c['primary']}, {c['secondary']});
            color: white; border-radius: 6px; border: none;
        }}
        section[data-testid="stSidebar"] .stPageLink a {{
            font-size: 0.8rem !important; font-weight: 500 !important;
            padding: 0.35rem 0.7rem !important; border-radius: 8px !important;
            transition: all var(--transition) !important;
            color: rgba(255,255,255,0.5) !important;
            border: none !important; background: transparent !important;
            margin-bottom: 0.15rem !important; box-shadow: none !important;
        }}
        section[data-testid="stSidebar"] .stPageLink a:hover {{
            background: rgba(255,255,255,0.06) !important;
            color: white !important; text-decoration: none !important;
        }}

        .sidebar-brand {{
            text-align: center; padding: 0.3rem 0 0.6rem 0;
        }}
        .sidebar-brand-logo {{
            width: 46px; height: 46px;
            background: linear-gradient(135deg, {c['primary']}, {c['accent']});
            border-radius: 14px;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 1.4rem;
            box-shadow: 0 4px 20px rgba(99,102,241,0.4);
            margin-bottom: 0.4rem;
        }}
        .sidebar-brand-name {{
            font-weight: 800; font-size: 0.9rem; color: white; letter-spacing: -0.2px;
        }}
        .sidebar-brand-tag {{
            font-size: 0.58rem; color: rgba(255,255,255,0.3); letter-spacing: 0.5px;
        }}
        .nav-section {{
            color: rgba(255,255,255,0.25);
            font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 2px; padding: 0.5rem 0.5rem 0.2rem 0.5rem;
        }}
        .filter-section {{
            color: rgba(255,255,255,0.35);
            font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 1.2px; margin-top: 0.6rem; margin-bottom: 0.25rem;
            padding: 0.25rem 0.4rem;
            background: rgba(255,255,255,0.025);
            border-radius: 6px;
            display: flex; align-items: center; gap: 0.4rem;
        }}
        .filter-label {{
            color: rgba(255,255,255,0.5);
            font-size: 0.65rem; font-weight: 600; margin-bottom: 0.1rem; letter-spacing: 0.3px;
        }}

        /* Sidebar filter toggle buttons (âœ“ âœ•) */
        section[data-testid="stSidebar"] div[data-testid="column"] .stButton button {{
            padding: 0 !important; min-width: 24px !important; height: 24px !important;
            line-height: 24px !important; font-size: 0.6rem !important;
            border-radius: 6px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            background: rgba(255,255,255,0.04) !important;
            color: rgba(255,255,255,0.5) !important; font-weight: 400 !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="column"] .stButton button:hover {{
            background: rgba(99,102,241,0.2) !important;
            border-color: rgba(99,102,241,0.4) !important; color: white !important;
            transform: none !important; box-shadow: none !important;
        }}

        /* Sidebar reset button */
        section[data-testid="stSidebar"] .stButton:last-child button {{
            padding: 0.4rem 0.8rem !important; height: auto !important;
            font-size: 0.75rem !important;
            background: rgba(99,102,241,0.1) !important;
            border-color: rgba(99,102,241,0.25) !important;
            border-radius: 8px !important;
            color: rgba(255,255,255,0.8) !important; width: 100% !important;
        }}
        section[data-testid="stSidebar"] .stButton:last-child button:hover {{
            background: rgba(99,102,241,0.25) !important;
            border-color: rgba(99,102,241,0.5) !important; color: white !important;
        }}

        /* Sidebar multiselect compact */
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            min-height: 30px !important; font-size: 0.75rem !important;
        }}
        section[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {{
            font-size: 0.65rem !important; padding: 0 0.4rem !important; height: 20px !important;
        }}

        .filter-badge {{
            display: inline-block;
            background: rgba(99,102,241,0.2);
            color: {c['primary_light']};
            font-size: 0.6rem; font-weight: 700;
            padding: 0.15rem 0.5rem; border-radius: 20px;
            margin-left: 0.4rem; letter-spacing: 0.3px;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           DRILL-DOWN BADGE â€” Pill Premium
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .drill-badge {{
            display: inline-flex; align-items: center; gap: 0.5rem;
            padding: 0.4rem 0.8rem 0.4rem 1rem;
            background: rgba(99,102,241,0.1);
            border: 1px solid rgba(99,102,241,0.3);
            border-radius: 50px;
            font-size: 0.82rem; font-weight: 600;
            color: {c['primary_light']};
            margin-bottom: 0.8rem;
            backdrop-filter: blur(8px);
            transition: all var(--transition);
        }}
        .drill-badge:hover {{
            border-color: rgba(99,102,241,0.5);
            box-shadow: 0 0 20px rgba(99,102,241,0.1);
        }}
        .drill-badge .drill-label {{
            font-weight: 400; color: {c['text_secondary']};
        }}
        .drill-badge .drill-clear {{
            cursor: pointer; font-size: 1rem; line-height: 1;
            padding: 0 4px; transition: all var(--transition);
            opacity: 0.6;
        }}
        .drill-badge .drill-clear:hover {{
            color: {c['danger']}; opacity: 1; transform: scale(1.2);
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           STAT CHIPS
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .stat-chip {{
            background: rgba(59,130,246,0.1);
            border: 1px solid rgba(59,130,246,0.2);
            border-radius: 10px; padding: 0.5rem 0.9rem;
            display: inline-flex; align-items: center; gap: 0.5rem;
        }}
        .stat-chip-value {{
            color: {c['text_primary']}; font-size: 0.85rem; font-weight: 700;
        }}
        .stat-chip-label {{
            color: {c['text_muted']}; font-weight: 400;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           ROWS (for drill buttons under charts)
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        .drill-row {{
            display: flex; flex-wrap: wrap; gap: 0.4rem;
            margin: -0.3rem 0 0.5rem 0;
        }}
        .drill-btn {{
            font-size: 0.7rem !important; font-weight: 600 !important;
            padding: 0.15rem 0.6rem !important;
            border-radius: 50px !important;
            background: transparent !important;
            border: 1px solid {c['border']} !important;
            color: rgba(255,255,255,0.5) !important;
            transition: all var(--transition) !important;
            min-height: 28px !important;
            line-height: 1 !important;
        }}
        .drill-btn:hover {{
            background: rgba(99,102,241,0.1) !important;
            border-color: {c['primary']} !important;
            color: {c['primary_light']} !important;
        }}

        /* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
           RESPONSIVE
           â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding-left: 1rem !important; padding-right: 1rem !important;
            }}
            .progress-row {{
                flex-direction: column; align-items: stretch; gap: 0.5rem;
            }}
            .progress-detail {{ text-align: left; }}
        }}
    </style>
    """
