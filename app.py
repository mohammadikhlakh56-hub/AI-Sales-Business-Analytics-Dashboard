import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from utils import smart_cleaner

# Load env variables (for GEMINI_API_KEY)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Business Hub | Sales Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Custom CSS ---
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css('styles.css')

# =====================================================
# SIDEBAR — Upload Panel
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1.2rem 0;">
        <div style="font-size:2.2rem; margin-bottom:0.3rem;">📦</div>
        <div style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:700;
                    color:#c9d5e8; letter-spacing:0.02em;">Data Upload Panel</div>
        <div style="font-size:0.75rem; color:#4d6080; margin-top:4px;">
            Supports CSV & Excel files
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your dataset here",
        type=["csv", "xlsx", "xls"],
        help="Upload a sales/basket CSV or Excel file to unlock all analytics features."
    )

    if uploaded_file is not None:
        try:
            filename = uploaded_file.name.lower()
            if filename.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {filename}")

            if df.empty:
                raise ValueError("The uploaded file is empty. Please upload a file with data.")

            with st.spinner("🔍 Running Smart Cleaner..."):
                df_clean, date_col = smart_cleaner(df)

            st.session_state['data'] = df_clean
            st.session_state['date_col'] = date_col

            # Show upload summary
            st.markdown("---")
            st.success(f"✅ **{uploaded_file.name}** loaded!")
            col_a, col_b = st.columns(2)
            col_a.metric("Rows", f"{len(df_clean):,}")
            col_b.metric("Columns", f"{len(df_clean.columns)}")
            st.markdown(
                "<div style='font-size:0.78rem;color:#4d8090;text-align:center;margin-top:6px;'>"
                "Navigate to the pages above ☝️</div>",
                unsafe_allow_html=True
            )

        except ValueError as ve:
            st.error(f"⚠️ **Validation Error:** {ve}")
            st.session_state['data'] = None
        except Exception as e:
            st.error(f"🛑 **Unexpected error:** {e}")
            st.session_state['data'] = None
    else:
        st.session_state.setdefault('data', None)
        st.markdown("""
        <div style="text-align:center; padding:1rem 0.5rem; border-radius:10px;
                    background:rgba(56,139,253,0.04); border:1px dashed rgba(56,139,253,0.2);">
            <div style="font-size:1.6rem;">📂</div>
            <div style="font-size:0.82rem; color:#4d6080; margin-top:6px;">
                No file uploaded yet
            </div>
        </div>
        """, unsafe_allow_html=True)


# =====================================================
# MAIN — Hero Section
# =====================================================
st.markdown("""
<div style="padding: 2rem 0 1rem 0;">
    <h1 style="margin-bottom:0.5rem;">🚀 AI Business Analytics Hub</h1>
    <p style="font-size:1.1rem; color:#6b85a8; max-width:700px; line-height:1.7; margin:0;">
        Upload your sales dataset and harness the power of AI-driven insights,
        interactive visualizations, and granular data exploration — all in one place.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- Status Banner ---
if st.session_state.get('data') is not None:
    df_loaded = st.session_state['data']
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(35,134,54,0.15),rgba(63,185,80,0.08));
                border:1px solid rgba(63,185,80,0.3); border-radius:14px; padding:1rem 1.4rem;
                display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;">
        <span style="font-size:1.8rem;">✅</span>
        <div>
            <div style="font-weight:700; color:#3fb950; font-size:1rem;">Dataset Active</div>
            <div style="font-size:0.85rem; color:#6b85a8;">
                {len(df_loaded):,} rows × {len(df_loaded.columns)} columns loaded — navigate to any page to explore!
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(56,139,253,0.1),rgba(88,166,255,0.05));
                border:1px solid rgba(56,139,253,0.25); border-radius:14px; padding:1rem 1.4rem;
                display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;">
        <span style="font-size:1.8rem;">👈</span>
        <div>
            <div style="font-weight:700; color:#58a6ff; font-size:1rem;">Get Started</div>
            <div style="font-size:0.85rem; color:#6b85a8;">
                Upload your CSV or Excel dataset in the sidebar to unlock all analytics features.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Feature Cards ---
st.markdown("### ✨ What You Can Do")
c1, c2, c3 = st.columns(3)

card_style = """
background:linear-gradient(135deg,rgba(22,30,50,0.7),rgba(14,20,38,0.9));
border:1px solid rgba(56,139,253,0.18); border-radius:16px;
padding:1.5rem 1.4rem; height:100%; transition:transform 0.2s ease;
"""

with c1:
    st.markdown(f"""
    <div style="{card_style}">
        <div style="font-size:2.2rem; margin-bottom:0.7rem;">📊</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:1.1rem;
                    color:#c9d5e8;margin-bottom:0.5rem;">Executive Dashboard</div>
        <div style="font-size:0.85rem;color:#5a7499;line-height:1.6;">
            View live KPI metrics, basket trend charts, day-of-week heatmaps,
            and generate an AI-powered strategy report with one click.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div style="{card_style}">
        <div style="font-size:2.2rem; margin-bottom:0.7rem;">🔍</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:1.1rem;
                    color:#c9d5e8;margin-bottom:0.5rem;">Deep Dive Explorer</div>
        <div style="font-size:0.85rem;color:#5a7499;line-height:1.6;">
            Slice and filter your dataset by any column, preview data instantly,
            explore product distributions, and export clean filtered CSVs.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div style="{card_style}">
        <div style="font-size:2.2rem; margin-bottom:0.7rem;">🤖</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:1.1rem;
                    color:#c9d5e8;margin-bottom:0.5rem;">AI Strategy Engine</div>
        <div style="font-size:0.85rem;color:#5a7499;line-height:1.6;">
            Powered by Google Gemini — get a CEO summary, growth strategies,
            and risk factors tailored to your actual data in seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- How-To Steps ---
st.markdown("### 🗺️ How It Works")
s1, s2, s3 = st.columns(3)

step_style_num = "font-family:'Outfit',sans-serif;font-size:2rem;font-weight:800;color:#1f6feb;"
step_style_title = "font-weight:700;color:#c9d5e8;font-size:0.95rem;margin:0.4rem 0 0.3rem 0;"
step_style_desc = "font-size:0.82rem;color:#5a7499;line-height:1.55;"

with s1:
    st.markdown(f"""
    <div style="{card_style} text-align:center;">
        <div style="{step_style_num}">01</div>
        <div style="{step_style_title}">Upload Your Data</div>
        <div style="{step_style_desc}">Drop any CSV or Excel sales file in the sidebar. We auto-detect date columns and clean the data.</div>
    </div>""", unsafe_allow_html=True)

with s2:
    st.markdown(f"""
    <div style="{card_style} text-align:center;">
        <div style="{step_style_num}">02</div>
        <div style="{step_style_title}">Explore Dashboards</div>
        <div style="{step_style_desc}">Navigate to Executive Dashboard for visual KPIs or Deep Dive for granular data exploration.</div>
    </div>""", unsafe_allow_html=True)

with s3:
    st.markdown(f"""
    <div style="{card_style} text-align:center;">
        <div style="{step_style_num}">03</div>
        <div style="{step_style_title}">Generate AI Insights</div>
        <div style="{step_style_desc}">Click "Generate Growth Strategy" to get actionable AI recommendations and download the report.</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# --- Footer ---
st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem 0; color:#2d3f5a; font-size:0.8rem;">
    Built with ❤️ using Streamlit · Powered by Google Gemini AI · 
    <span style="color:#1f6feb;">Sales & Business Analytics Dashboard</span>
</div>
""", unsafe_allow_html=True)
