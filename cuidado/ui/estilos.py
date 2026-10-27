import streamlit as st

def aplicar_estilos():
    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            html, body, [class*="css"] {
                color: #31333F;
            }
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(180deg, #F6F7FB 0%, #EEF2FF 100%);
                color: #31333F;
            }
            [data-testid="stHeader"] {
                background: transparent;
            }
            .block-container {
                padding-top: 2.5rem;
                padding-bottom: 3rem;
            }
            .hero-panel {
                background: linear-gradient(135deg, #5B21B6 0%, #7C3AED 45%, #A855F7 100%);
                color: #FFFFFF;
                border-radius: 24px;
                padding: 1.2rem 1.4rem;
                box-shadow: 0 18px 42px rgba(91, 33, 182, 0.25);
                margin: 0.25rem 0 1.25rem 0;
            }
            .hero-panel h2 {
                color: #FFFFFF !important;
                margin: 0 0 0.25rem 0;
                font-size: 1.35rem;
            }
            .hero-panel p {
                color: rgba(255, 255, 255, 0.92) !important;
                margin: 0.2rem 0 0 0;
                line-height: 1.45;
            }
            .section-kicker {
                display: inline-block;
                padding: 0.25rem 0.65rem;
                border-radius: 999px;
                background: rgba(124, 58, 237, 0.10);
                color: #5B21B6;
                font-weight: 700;
                font-size: 0.78rem;
                letter-spacing: 0.02em;
                margin-bottom: 0.5rem;
            }
            .section-card {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(91, 33, 182, 0.10);
                border-radius: 20px;
                padding: 1rem 1.1rem;
                box-shadow: 0 10px 28px rgba(30, 41, 59, 0.06);
                margin: 0.25rem 0 1rem 0;
            }
            .structural-gaps {
                margin: 1.15rem 0 1.35rem 0;
            }
            .structural-gaps-intro {
                margin: 0 0 0.85rem 0;
                color: #475569 !important;
            }
            .structural-gap-card {
                min-height: 148px;
                background: linear-gradient(155deg, #FFFFFF 0%, #F8FAFF 100%);
                border: 1px solid rgba(91, 33, 182, 0.14);
                border-top: 4px solid var(--gap-accent);
                border-radius: 16px;
                padding: 0.9rem 0.85rem;
                box-shadow: 0 10px 24px rgba(30, 41, 59, 0.08);
            }
            .structural-gap-icon {
                font-size: 1.65rem;
                line-height: 1;
                margin-bottom: 0.45rem;
            }
            .structural-gap-card h3 {
                color: #31333F !important;
                font-size: 1rem;
                line-height: 1.2;
                margin: 0 0 0.45rem 0;
            }
            .structural-gap-card p {
                color: #475569 !important;
                font-size: 0.88rem;
                line-height: 1.35;
                margin: 0;
            }
            [data-testid="stAppViewContainer"] h1,
            [data-testid="stAppViewContainer"] h2,
            [data-testid="stAppViewContainer"] h3,
            [data-testid="stAppViewContainer"] p,
            [data-testid="stAppViewContainer"] label,
            [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
                color: #31333F;
            }
            [data-testid="stAppViewContainer"] p {
                line-height: 1.5;
            }
            [data-testid="stMetric"] {
                background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFF 100%);
                border: 1px solid rgba(91, 33, 182, 0.12);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: 0 12px 28px rgba(30, 41, 59, 0.10);
                position: relative;
                overflow: hidden;
            }
            [data-testid="stMetric"]::before {
                content: "";
                position: absolute;
                inset: 0 auto 0 0;
                width: 4px;
                background: linear-gradient(180deg, #8B5CF6 0%, #EC4899 100%);
            }
            [data-testid="stMetricLabel"],
            [data-testid="stMetricValue"],
            [data-testid="stMetricDelta"] {
                color: #31333F !important;
            }
            [data-baseweb="tab-list"] {
                background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(245,243,255,0.95));
                border-radius: 16px;
                padding: 0.35rem;
                border: 1px solid rgba(91, 33, 182, 0.10);
            }
            [data-baseweb="tab"] {
                color: #31333F !important;
                font-weight: 600;
            }
            [data-baseweb="tab"][aria-selected="true"] {
                color: #5B21B6 !important;
                background: rgba(91, 33, 182, 0.12);
                border-bottom-color: #5B21B6 !important;
            }
            [data-baseweb="tab"]:nth-child(1) {
                --tab-accent: #2563EB;
            }
            [data-baseweb="tab"]:nth-child(2) {
                --tab-accent: #DB2777;
            }
            [data-baseweb="tab"]:nth-child(3) {
                --tab-accent: #0F766E;
            }
            [data-baseweb="tab"]:hover {
                color: var(--tab-accent) !important;
                background: color-mix(in srgb, var(--tab-accent) 9%, white);
            }
            [data-baseweb="tab"][aria-selected="true"] {
                color: var(--tab-accent) !important;
                border-bottom-color: var(--tab-accent) !important;
            }
            .brand-mark {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                color: #5B21B6;
                font-size: 0.8rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.3rem;
            }
            .brand-mark span {
                display: inline-grid;
                place-items: center;
                width: 1.7rem;
                height: 1.7rem;
                border-radius: 0.6rem;
                background: linear-gradient(135deg, #7C3AED, #EC4899);
                color: #FFFFFF;
                box-shadow: 0 6px 14px rgba(124, 58, 237, 0.28);
            }
            .source-strip {
                background: #FFFBEB;
                border-left: 4px solid #F59E0B;
                border-radius: 10px;
                padding: 0.55rem 0.75rem;
            }
            .source-strip p {
                margin: 0;
                color: #713F12 !important;
                font-size: 0.82rem;
            }
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input,
            [data-testid="stTimeInput"] input,
            [data-testid="stSelectbox"] > div,
            [data-testid="stMultiSelect"] > div {
                background: #FFFFFF;
                color: #31333F;
            }
            [data-testid="stAlert"] {
                color: #31333F;
                border-radius: 14px;
            }
            [data-testid="stDataFrame"] {
                border-radius: 12px;
                overflow: hidden;
            }
            @media (max-width: 768px) {
                .block-container {
                    padding: 1rem 0.75rem 2rem;
                }
                [data-testid="stButton"] button {
                    min-height: 3.4rem;
                    width: 100%;
                    border-radius: 14px;
                    font-size: 1.05rem;
                    font-weight: 700;
                }
                .mobile-step {
                    border-left: 4px solid #8B5CF6;
                    background: rgba(255, 255, 255, 0.86);
                    border-radius: 0 14px 14px 0;
                    padding: 0.8rem 0.9rem;
                    margin: 0.6rem 0;
                }
                .mobile-kpi {
                    margin: 0.45rem 0;
                }
                [data-testid="stAppViewContainer"] h1 {
                    font-size: 1.65rem;
                    line-height: 1.2;
                }
                [data-testid="stAppViewContainer"] h2 {
                    font-size: 1.25rem;
                    line-height: 1.25;
                }
                [data-testid="stAppViewContainer"] h3 {
                    font-size: 1.05rem;
                    line-height: 1.3;
                }
                [data-testid="stAppViewContainer"] p,
                [data-testid="stAppViewContainer"] label,
                [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
                    font-size: 0.95rem;
                }
                [data-testid="stHorizontalBlock"] {
                    flex-direction: column;
                    gap: 0.6rem;
                }
                [data-testid="stMetric"] {
                    min-width: 100%;
                    padding: 0.8rem 0.9rem;
                }
                [data-testid="stMetricValue"] {
                    font-size: 1.25rem;
                }
                [data-testid="stMetricLabel"] {
                    font-size: 0.9rem;
                }
                [data-baseweb="tab-list"] {
                    overflow-x: auto;
                    white-space: nowrap;
                }
                [data-testid="stRadio"] > div {
                    flex-direction: column;
                    align-items: flex-start;
                }
                div[data-testid="stButton"] > button,
                button[kind="primary"],
                button[kind="secondary"] {
                    width: 100%;
                }
                [data-testid="stSelectbox"],
                [data-testid="stMultiSelect"],
                [data-testid="stTextInput"],
                [data-testid="stNumberInput"],
                [data-testid="stTimeInput"] {
                    width: 100%;
                }
                [data-testid="stCaptionContainer"] {
                    font-size: 0.82rem;
                    line-height: 1.35;
                }
                .hero-panel {
                    padding: 1rem 1rem;
                    border-radius: 20px;
                }
                .hero-panel h2 {
                    font-size: 1.15rem;
                }
                .brand-mark {
                    font-size: 0.72rem;
                }
                .source-strip {
                    padding: 0.5rem 0.65rem;
                }
                iframe,
                .stHtmlFrame,
                .element-container iframe {
                    max-width: 100%;
                }
                [data-testid="stDataFrame"] {
                    font-size: 0.84rem;
                }
                section.main iframe {
                    height: 390px !important;
                }
            }
            @media (min-width: 769px) {
                section.main iframe {
                    height: 560px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
