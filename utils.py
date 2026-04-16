import pandas as pd
import numpy as np
import os
import re
import time
import streamlit as st

# -------------------------------------------------------------
# 1. Data Cleaning Agent ("Smart Cleaner")
# -------------------------------------------------------------
def smart_cleaner(df):
    """
    Auto-detects date columns, removes currency symbols, and handles missing values.
    Specifically validates basket_details files.
    """
    # 1. Convert Date (Handles multiple formats automatically)
    if 'basket_date' not in df.columns:
        for col in df.columns:
            if 'date' in col.lower() or 'day' in col.lower():
                df.rename(columns={col: 'basket_date'}, inplace=True)
                break
                
    if 'basket_date' in df.columns:
        df['basket_date'] = pd.to_datetime(df['basket_date'], errors='coerce')
        df = df.dropna(subset=['basket_date']) # Remove rows with invalid dates
        date_col = 'basket_date'
    else:
        date_col = None
    
    # 2. Convert IDs to strings (Prevents Plotly from treating them as numbers)
    for col in ['customer_id', 'product_id']:
        if col in df.columns:
            df[col] = df[col].astype(str)
            
    # 3. Clean Basket Counts
    if 'basket_count' in df.columns:
        df['basket_count'] = pd.to_numeric(df['basket_count'], errors='coerce').fillna(0)
        df = df[df['basket_count'] > 0]
        
    return df, date_col


# -------------------------------------------------------------
# Helper: resolve a secret from st.secrets or env vars
# -------------------------------------------------------------
def _get_secret(key: str) -> str | None:
    try:
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key) or None


# -------------------------------------------------------------
# 2. Insight Agent  (Groq primary → Gemini fallback)
# -------------------------------------------------------------
def generate_business_strategy(df):
    """
    Generates a CEO-level business strategy report.
    Uses Groq (LLaMA 3.3 70B) as primary — free with no daily hard-cap.
    Falls back to Gemini if no Groq key is configured.
    """

    # ── Build the prompt ──────────────────────────────────────
    total_sales  = df['basket_count'].sum()  if 'basket_count'  in df.columns else 0
    unique_cust  = df['customer_id'].nunique() if 'customer_id' in df.columns else 0
    avg_basket   = df['basket_count'].mean()  if 'basket_count'  in df.columns else 0
    top_5_products = {}
    if 'product_id' in df.columns and 'basket_count' in df.columns:
        top_5_products = (
            df.groupby('product_id')['basket_count']
            .sum().sort_values(ascending=False).head(5).to_dict()
        )

    prompt = f"""
    Act as a Senior Retail Business Consultant. I will give you a summary of my sales data.

    SUMMARY DATA:
    - Total Items Sold:            {total_sales:,}
    - Unique Customers:            {unique_cust:,}
    - Average Items per Basket:    {avg_basket:.2f}
    - Top 5 Best-Selling Products: {top_5_products}

    TASK — provide:
    1. A 'CEO Summary' (2 sentences).
    2. Three actionable growth strategies (cross-selling, loyalty programs, inventory shifts, etc.).
    3. One key 'Risk Factor' to watch out for.

    Format in clean Markdown with relevant emojis.
    """

    # ══════════════════════════════════════════════════════════
    # PRIMARY: Groq  (free tier, LLaMA 3.3 70B)
    # ══════════════════════════════════════════════════════════
    groq_key = _get_secret("GROQ_API_KEY")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            result = response.choices[0].message.content
            st.caption("🟢 Powered by **Groq · LLaMA 3.3 70B** (free tier)")
            return result

        except Exception as e:
            err_str = str(e)
            status   = getattr(e, 'status_code', None) or getattr(e, 'code', None)
            if status == 429:
                delay_match = re.search(r'(\d+(?:\.\d+)?)\s*s', err_str)
                wait = int(float(delay_match.group(1))) if delay_match else 60
                st.warning(f"⚠️ Groq rate limit hit — waiting {wait}s then retrying…")
                time.sleep(wait)
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=1024,
                    )
                    return response.choices[0].message.content
                except Exception:
                    pass  # fall through to Gemini
            else:
                # Non-quota error — fall through to Gemini
                st.warning(f"⚠️ Groq error ({status}) — trying Gemini fallback…")

    # ══════════════════════════════════════════════════════════
    # FALLBACK: Gemini  (google-genai SDK)
    # ══════════════════════════════════════════════════════════
    gemini_key = _get_secret("GEMINI_API_KEY")
    if not gemini_key:
        return (
            "⚠️ **No AI API key configured.**\n\n"
            "Add one of these to `.streamlit/secrets.toml`:\n"
            "- `GROQ_API_KEY` — free at [console.groq.com](https://console.groq.com) ✅ recommended\n"
            "- `GEMINI_API_KEY` — free at [aistudio.google.com](https://aistudio.google.com)"
        )

    from google import genai as google_genai
    client = google_genai.Client(api_key=gemini_key)
    gemini_models = ['gemini-2.0-flash', 'gemini-2.0-flash-lite']

    for model_name in gemini_models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name, contents=prompt
                )
                st.caption(f"🔵 Powered by **Google Gemini · {model_name}**")
                return response.text

            except Exception as e:
                status = getattr(e, 'code', None) or getattr(e, 'status_code', None)
                err_str = str(e)

                if status == 429:
                    if model_name == 'gemini-2.0-flash':
                        st.warning("⚠️ Gemini quota hit — trying lite model…")
                        break  # next model
                    delay_match = re.search(r'retry[^0-9]*(\d+)', err_str, re.IGNORECASE)
                    wait = int(delay_match.group(1)) if delay_match else 35
                    return (
                        "⚠️ **All AI quotas exhausted.**\n\n"
                        f"- ⏰ Retry in ~{wait}s or after midnight UTC (daily reset)\n"
                        "- ✅ **Recommended fix**: add a free [Groq API key](https://console.groq.com) "
                        "to `secrets.toml` — no quota limits on the free tier\n"
                        "- 💳 Or enable billing at [aistudio.google.com](https://aistudio.google.com)"
                    )
                elif status == 503:
                    if attempt < 2:
                        wait = (attempt + 1) * 2
                        st.warning(f"⏳ Gemini busy — retrying in {wait}s…")
                        time.sleep(wait)
                    else:
                        return "❌ Gemini is overloaded. Please try again in a few minutes."
                else:
                    return f"❌ Gemini error: {e}"

    return "❌ Could not generate insights. Please check your API keys and try again."

