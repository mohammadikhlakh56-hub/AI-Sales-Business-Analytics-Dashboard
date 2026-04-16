import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Deep Dive Explorer | Analytics", page_icon="🔍", layout="wide")

# --- Load Custom CSS ---
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
    <h1 style="margin-bottom:0.3rem;">🔍 Deep Dive Explorer</h1>
    <p style="color:#6b85a8; font-size:0.95rem;">
        Filter, slice, and explore your dataset at the granular level. Export any view as a clean CSV.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()


# =====================================================================
# SUMMARY METRICS (quick recap)
# =====================================================================
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Rows", f"{len(df):,}")
m2.metric("Columns", f"{len(df.columns)}")
m3.metric(
    "Date Range",
    f"{df[date_col].min().strftime('%b %Y')} – {df[date_col].max().strftime('%b %Y')}"
    if date_col and pd.api.types.is_datetime64_any_dtype(df[date_col]) else "N/A"
)
m4.metric(
    "Unique Customers",
    f"{df['customer_id'].nunique():,}" if 'customer_id' in df.columns else "N/A"
)

st.divider()


# =====================================================================
# FILTERS — Sidebar-inside-page section
# =====================================================================
st.markdown("### 🎛️ Filter Controls")

filter_col1, filter_col2 = st.columns([2, 3])

categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
df_filtered = df.copy()

with filter_col1:
    if categorical_cols:
        chosen_col = st.selectbox("📌 Filter by column:", categorical_cols, key="filter_col_select")
        unique_vals = sorted(df[chosen_col].dropna().unique().tolist())
        selected_vals = st.multiselect(
            f"Select values for **{chosen_col}**:",
            options=unique_vals,
            default=[],
            key="filter_vals_select",
            placeholder="Select one or more values…"
        )
        if selected_vals:
            df_filtered = df_filtered[df_filtered[chosen_col].isin(selected_vals)]
    else:
        st.info("No categorical columns found to filter by.")

with filter_col2:
    # Date range filter (if date column exists)
    if date_col and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        date_range = st.date_input(
            "📅 Date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range_filter"
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered[date_col].dt.date >= start_date) &
                (df_filtered[date_col].dt.date <= end_date)
            ]
    else:
        st.info("ℹ️ No date column detected for date range filtering.")

# Filter summary badge
filtered_pct = (len(df_filtered) / len(df) * 100) if len(df) > 0 else 0
badge_color = "#3fb950" if filtered_pct == 100 else "#f0883e"
st.markdown(f"""
<div style="display:inline-block; background:rgba(22,30,50,0.6);
            border:1px solid rgba(56,139,253,0.2); border-radius:8px;
            padding:0.4rem 1rem; margin: 0.5rem 0 1rem 0; font-size:0.85rem;">
    Showing <strong style="color:{badge_color};">{len(df_filtered):,}</strong> of
    <strong style="color:#58a6ff;">{len(df):,}</strong> rows
    (<strong style="color:{badge_color};">{filtered_pct:.1f}%</strong>)
</div>
""", unsafe_allow_html=True)

st.divider()


# =====================================================================
# TABS — Data Table / Visual Breakdown / Schema
# =====================================================================
tab1, tab2, tab3 = st.tabs(["📋  Data Table", "📊  Visual Breakdown", "🗂️  Schema Info"])

# ---- TAB 1: Data Table ----
with tab1:
    st.markdown(f"<p style='color:#5a7499;font-size:0.85rem;'>Showing top 1,000 rows of filtered data.</p>",
                unsafe_allow_html=True)
    st.dataframe(
        df_filtered.head(1000).reset_index(drop=True),
        use_container_width=True,
        height=420
    )
    st.markdown("")

    col_dl1, col_dl2 = st.columns([1, 4])
    with col_dl1:
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️  Export as CSV",
            data=csv_data,
            file_name="filtered_data_export.csv",
            mime="text/csv",
            use_container_width=True
        )

# ---- TAB 2: Visual Breakdown ----
with tab2:
    if df_filtered.empty:
        st.warning("No data matches the current filters. Adjust the filters above.")
    else:
        viz_col1, viz_col2 = st.columns(2)

        with viz_col1:
            # Top Products bar chart
            if 'product_id' in df_filtered.columns and 'basket_count' in df_filtered.columns:
                top_prods = (
                    df_filtered.groupby('product_id')['basket_count']
                    .sum().sort_values(ascending=False).head(15).reset_index()
                )
                top_prods.columns = ['Product ID', 'Basket Count']
                fig_p = px.bar(
                    top_prods, x='Basket Count', y='Product ID', orientation='h',
                    title="Top 15 Products (Filtered View)",
                    color='Basket Count',
                    color_continuous_scale=[[0,'#1a3a6e'],[0.5,'#388bfd'],[1,'#58a6ff']]
                )
                fig_p.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False,
                    title_font=dict(size=13, color='#8ba3cc'),
                    font=dict(color='#8ba3cc', size=11),
                    margin=dict(l=5,r=5,t=40,b=5),
                    yaxis=dict(categoryorder='total ascending', gridcolor='rgba(56,139,253,0.06)'),
                    xaxis=dict(gridcolor='rgba(56,139,253,0.08)')
                )
                fig_p.update_traces(marker_line_width=0)
                st.plotly_chart(fig_p, use_container_width=True)
            else:
                st.info("Need `product_id` and `basket_count` columns.")

        with viz_col2:
            # Monthly volume (if date)
            if date_col and pd.api.types.is_datetime64_any_dtype(df_filtered[date_col]):
                df_monthly = df_filtered.copy()
                df_monthly['Month'] = df_monthly[date_col].dt.to_period('M').astype(str)
                monthly_counts = df_monthly.groupby('Month').size().reset_index(name='Transactions')

                fig_m = px.bar(
                    monthly_counts, x='Month', y='Transactions',
                    title="Monthly Transaction Volume (Filtered)",
                    color='Transactions',
                    color_continuous_scale=[[0,'#1a3a3a'],[0.5,'#0e8381'],[1,'#39d0d8']]
                )
                fig_m.update_layout(
                    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False,
                    title_font=dict(size=13, color='#8ba3cc'),
                    font=dict(color='#8ba3cc', size=11),
                    margin=dict(l=5,r=5,t=40,b=5),
                    xaxis=dict(tickangle=-45, gridcolor='rgba(57,208,216,0.06)'),
                    yaxis=dict(gridcolor='rgba(57,208,216,0.08)')
                )
                fig_m.update_traces(marker_line_width=0)
                st.plotly_chart(fig_m, use_container_width=True)
            else:
                st.info("Need a date column for monthly breakdown.")

        # Basket distribution histogram
        if 'basket_count' in df_filtered.columns:
            st.markdown("---")
            fig_hist = px.histogram(
                df_filtered, x='basket_count',
                title="Basket Size Distribution (Filtered)",
                nbins=40,
                color_discrete_sequence=['#a371f7'],
                labels={'basket_count': 'Basket Size'}
            )
            fig_hist.update_layout(
                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font=dict(size=13, color='#8ba3cc'),
                font=dict(color='#8ba3cc', size=11),
                margin=dict(l=5,r=5,t=40,b=5),
                showlegend=False,
                xaxis=dict(gridcolor='rgba(163,113,247,0.06)'),
                yaxis=dict(gridcolor='rgba(163,113,247,0.08)', title_text='Count')
            )
            fig_hist.update_traces(marker_line_width=0)
            st.plotly_chart(fig_hist, use_container_width=True)


# ---- TAB 3: Schema Info ----
with tab3:
    st.markdown("""
    <p style="color:#5a7499;font-size:0.88rem;margin-bottom:1rem;">
        Column-level metadata for the currently filtered dataset.
    </p>
    """, unsafe_allow_html=True)

    schema_rows = []
    for col in df_filtered.columns:
        col_series = df_filtered[col]
        null_count = col_series.isnull().sum()
        null_pct = (null_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        schema_rows.append({
            "Column": col,
            "Data Type": str(col_series.dtype),
            "Unique Values": col_series.nunique(),
            "Null Count": null_count,
            "Null %": f"{null_pct:.1f}%",
            "Sample Value": str(col_series.dropna().iloc[0]) if not col_series.dropna().empty else "—"
        })

    schema_df = pd.DataFrame(schema_rows)
    st.dataframe(schema_df, use_container_width=True, hide_index=True, height=400)

st.divider()
st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 0 0; color:#2d3f5a; font-size:0.8rem;">
    AI Business Analytics Hub · Deep Dive Explorer
</div>
""", unsafe_allow_html=True)
