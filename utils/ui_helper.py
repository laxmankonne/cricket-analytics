"""
UI Helper Utility Module
Handles custom CSS injection, sidebar brand rendering, and common header cards.
"""

import os
import streamlit as st

def apply_app_styles():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_sidebar_header():
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 20px 0; text-align: left;">
            <div style="font-size: 1.4rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">
                🏏 <span style="color: #16A34A;">CRIC</span><span style="color: #38BDF8;">ANALYTICS</span>
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 4px;">
                Advanced Cricket Data Analytics Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

def render_page_header(title, subtitle, badge_text="OFFICIAL CRICKET DATASET"):
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div class="cricket-header-badge">
                <span>⚡</span> {badge_text}
            </div>
            <h1 style="font-size: 2.25rem; font-weight: 800; color: #F8FAFC; margin: 0 0 8px 0; letter-spacing: -0.025em;">
                {title}
            </h1>
            <p style="font-size: 1.05rem; color: #94A3B8; margin: 0; max-width: 800px; line-height: 1.5;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

