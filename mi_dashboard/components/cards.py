import streamlit as st

from config.style import COLORS

_BG_TINT = {
    COLORS["accent"]: COLORS["cyan_light"],
    COLORS["success"]: COLORS["green_light"],
    COLORS["warning"]: COLORS["orange_light"],
    COLORS["danger"]: COLORS["red_light"],
    COLORS["purple"]: COLORS["purple_light"],
    COLORS["info"]: COLORS["blue_light"],
    COLORS["primary"]: COLORS["blue_light"],
}


def kpi_card(
    label: str,
    value: str,
    delta: str = "",
    help_text: str = "",
    color: str = COLORS["accent"],
    icon: str = "",
    delay: float = 0.0,
) -> None:
    """Render a premium KPI card with glassmorphism, hover lift, and trend badges."""
    delta_html = ""
    if delta:
        is_positive = delta.startswith("+") or delta.startswith("▲")
        arrow = "▲" if is_positive else "▼"
        delta_color = COLORS["success"] if is_positive else COLORS["danger"]
        delta_bg = COLORS["green_light"] if is_positive else COLORS["red_light"]
        delta_html = f"""<div class="kpi-trend-badge" style="color:{delta_color};background:{delta_bg};"><span style="font-size:0.6rem;">{arrow}</span> {delta}</div>"""

    help_html = ""
    if help_text:
        help_html = f"""<div class="kpi-sub">{help_text}</div>"""

    bg_tint = _BG_TINT.get(color, COLORS["blue_light"])

    icon_html = ""
    if icon:
        icon_html = f"""<div class="kpi-icon-box" style="background:{bg_tint};box-shadow:0 0 16px {bg_tint};">{icon}</div>"""

    html_content = f"""<div class="kpi-premium" style="animation-delay:{delay}s;border-top-color:{color};" onmouseover="this.style.borderColor='{color}40';this.style.boxShadow='0 8px 32px rgba(0,0,0,0.2),0 0 24px {color}15';this.style.borderTopColor='{color}'" onmouseout="this.style.borderColor='';this.style.boxShadow='';this.style.borderTopColor='{color}'"><div class="kpi-glow" style="background:radial-gradient(circle,{color}08 0%,transparent 70%);"></div><div style="display:flex;align-items:flex-start;gap:0.8rem;">{icon_html}<div style="flex:1;min-width:0;"><div class="kpi-label-text">{label}</div><div class="kpi-value-text">{value}</div>{delta_html}{help_html}</div></div></div>"""
    st.markdown(html_content, unsafe_allow_html=True)
