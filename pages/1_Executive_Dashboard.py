import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_business_strategy

# --- Page Config ---
st.set_page_config(page_title="Executive Dashboard | Analytics", page_icon="📊", layout="wide")

# --- Load Custom CSS (single call from root path, Streamlit always runs from root) ---
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css('styles.css')


# =====================================================================
# GUARD — require uploaded data
# =====================================================================
if 'data' not in st.session_state or st.session_state['data'] is None:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(56,139,253,0.1),rgba(88,166,255,0.05));
                border:1px solid rgba(56,139,253,0.25); border-radius:14px;
                padding:2rem; text-align:center; margin-top:3rem;">
        <div style="font-size:3rem; margin-bottom:0.7rem;">📂</div>
        <h3 style="color:#58a6ff !important; text-transform:none !important; font-size:1.3rem !important;">
            No Data Loaded
        </h3>
        <p style="color:#5a7499; font-size:0.95rem;">
            Please go to the <strong style="color:#c9d5e8;">Home page</strong> and
            upload your dataset in the sidebar first.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = st.session_state['data']
date_col = st.session_state.get('date_col')


# =====================================================================
# HEADER
# =====================================================================
st.markdown("""
<div style="padding: 1rem 0 0.5rem 0;">
    <h1 style="margin-bottom:0.3rem;">📊 Executive Dashboard</h1>
    <p style="color:#6b85a8; font-size:0.95rem;">
        Real-time basket analytics, trend intelligence, and AI-powered strategy.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()


# =====================================================================
# KPI CARDS
# =====================================================================
st.markdown("### 📈 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

# 1. Total Transactions
total_transactions = len(df)

# 2. Unique Customers
unique_customers = df['customer_id'].nunique() if 'customer_id' in df.columns else "N/A"

# 3. Retention Rate
retention_rate = None
if 'customer_id' in df.columns and 'basket_date' in df.columns:
    purchase_counts = df.groupby('customer_id')['basket_date'].nunique()
    repeat_customers = purchase_counts[purchase_counts > 1].count()
    total_customers = df['customer_id'].nunique()
    if total_customers > 0:
        retention_rate = (repeat_customers / total_customers) * 100

# 4. Average Basket Size
avg_basket = df['basket_count'].mean() if 'basket_count' in df.columns else None

with col1:
    st.metric(label="Total Transactions", value=f"{total_transactions:,}")
with col2:
    st.metric(label="Unique Customers", value=f"{unique_customers:,}" if isinstance(unique_customers, int) else unique_customers)
with col3:
    st.metric(label="Retention Rate", value=f"{retention_rate:.1f}%" if retention_rate is not None else "N/A")
with col4:
    st.metric(label="Avg Basket Size", value=f"{avg_basket:.2f}" if avg_basket is not None else "N/A")

st.divider()


# =====================================================================
# CHARTS — ROW 1
# =====================================================================
st.markdown("### 📉 Sales Trend & Day-of-Week Analysis")
col_chart1, col_chart2 = st.columns([3, 2])

with col_chart1:
    if 'basket_count' in df.columns and date_col:
        df_trend = df.groupby(date_col)['basket_count'].mean().reset_index()
        fig_trend = px.area(
            df_trend, x=date_col, y='basket_count',
            title="Average Basket Size Over Time",
            labels={'basket_count': 'Avg Basket Size', date_col: 'Date'}
        )
        fig_trend.update_traces(
            fill='tozeroy',
            line=dict(color='#58a6ff', width=2.5),
            fillcolor='rgba(88,166,255,0.12)'
        )
        fig_trend.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=14, color='#8ba3cc'),
            font=dict(color='#8ba3cc', size=11),
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(gridcolor='rgba(56,139,253,0.08)', zeroline=False),
            yaxis=dict(gridcolor='rgba(56,139,253,0.08)', zeroline=False),
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("ℹ️ Need `basket_count` column and a date column for this chart.")

with col_chart2:
    if date_col:
        df_days = df.copy()
        df_days['Day'] = pd.to_datetime(df_days[date_col]).dt.day_name()
        df_day_stats = df_days.groupby('Day').size().reset_index(name='Transactions')
        cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_day_stats['Day'] = pd.Categorical(df_day_stats['Day'], categories=cats, ordered=True)
        df_day_stats = df_day_stats.sort_values('Day')

        fig_days = px.bar(
            df_day_stats, x='Transactions', y='Day', orientation='h',
            title="Transactions By Day of Week",
            color='Transactions',
            color_continuous_scale=[[0, '#1f3a6e'], [0.5, '#388bfd'], [1, '#58a6ff']]
        )
        fig_days.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=14, color='#8ba3cc'),
            font=dict(color='#8ba3cc', size=11),
            margin=dict(l=10, r=10, t=40, b=10),
            coloraxis_showscale=False,
            yaxis=dict(gridcolor='rgba(56,139,253,0.05)'),
            xaxis=dict(gridcolor='rgba(56,139,253,0.08)'),
        )
        fig_days.update_traces(marker_line_width=0)
        st.plotly_chart(fig_days, use_container_width=True)
    else:
        st.info("ℹ️ Need a date column for Peak Shopping Days chart.")


# =====================================================================
# CHARTS — ROW 2 (Top Products + Customer Distribution)
# =====================================================================
st.divider()
st.markdown("### 🏆 Product & Customer Analytics")
col_p1, col_p2 = st.columns(2)

with col_p1:
    if 'product_id' in df.columns and 'basket_count' in df.columns:
        top_products = (
            df.groupby('product_id')['basket_count']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        top_products.columns = ['Product ID', 'Total Sales']
        fig_top = px.bar(
            top_products, x='Total Sales', y='Product ID', orientation='h',
            title="Top 10 Products by Sales Volume",
            color='Total Sales',
            color_continuous_scale=[[0, '#3a1f6e'], [0.5, '#a371f7'], [1, '#d2a8ff']]
        )
        fig_top.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=14, color='#8ba3cc'),
            font=dict(color='#8ba3cc', size=11),
            margin=dict(l=10, r=10, t=40, b=10),
            coloraxis_showscale=False,
            yaxis=dict(gridcolor='rgba(163,113,247,0.05)', categoryorder='total ascending'),
            xaxis=dict(gridcolor='rgba(163,113,247,0.08)'),
        )
        fig_top.update_traces(marker_line_width=0)
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("ℹ️ Need `product_id` and `basket_count` columns for product chart.")

with col_p2:
    if 'customer_id' in df.columns and 'basket_count' in df.columns:
        cust_totals = df.groupby('customer_id')['basket_count'].sum()
        fig_hist = px.histogram(
            cust_totals, x=cust_totals.values,
            title="Customer Spending Distribution",
            labels={'x': 'Total Basket Count', 'y': 'Number of Customers'},
            nbins=30,
            color_discrete_sequence=['#f78166']
        )
        fig_hist.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=14, color='#8ba3cc'),
            font=dict(color='#8ba3cc', size=11),
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False,
            xaxis=dict(gridcolor='rgba(247,129,102,0.08)', title_text='Total Basket Count'),
            yaxis=dict(gridcolor='rgba(247,129,102,0.08)', title_text='Customers'),
        )
        fig_hist.update_traces(marker_line_width=0)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("ℹ️ Need `customer_id` and `basket_count` columns for distribution chart.")


# =====================================================================
# AI STRATEGY ENGINE
# =====================================================================
st.divider()
st.markdown("### 🤖 AI Business Strategy Consultant")
st.markdown(
    "<p style='color:#5a7499; font-size:0.9rem; margin-bottom:1rem;'>"
    "Generate a CEO-level report with actionable growth strategies powered by Google Gemini.</p>",
    unsafe_allow_html=True
)

if st.button("✨ Generate Growth Strategy Report", use_container_width=False):
    with st.spinner("🧠 Gemini is analyzing your basket trends..."):
        try:
            insights = generate_business_strategy(df)
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(31,111,235,0.08),rgba(88,166,255,0.04));
                        border:1px solid rgba(56,139,253,0.2); border-radius:14px; padding:1.5rem 1.8rem;
                        margin-top:0.5rem;">
            """, unsafe_allow_html=True)
            st.markdown(insights)
            st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                label="⬇️ Download Strategy Report",
                data=insights,
                file_name="AI_Business_Strategy_Report.txt",
                mime="text/plain",
                use_container_width=False
            )
        except Exception as e:
            st.error(f"❌ Could not generate insights. Error: {e}")

st.divider()

# --- Footer ---
st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 0 0; color:#2d3f5a; font-size:0.8rem;">
    AI Business Analytics Hub · Executive Dashboard
</div>
""", unsafe_allow_html=True)
