import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales & Promotion Dashboard", layout="wide")
st.title("📊 Sales and Promotion Dashboard")

# ====== READ DATA ======
sales_file = "tay tay jan to oct.Xlsx"
promo_file = "ANNIVERSARY OFFER LIST (1).xlsx"

# Read Excel files
sales_df = pd.read_excel(sales_file)
promo_df = pd.read_excel(promo_file)

# ====== CLEAN COLUMN NAMES ======
sales_df.columns = sales_df.columns.str.strip().str.lower()
promo_df.columns = promo_df.columns.str.strip().str.lower()

# ====== DEBUG: Check column names ======
st.write("Sales columns:", sales_df.columns.tolist())
st.write("Promo columns:", promo_df.columns.tolist())

# ====== FIND PROMO COLUMNS DYNAMICALLY ======
possible_promo_cols = [
    'barcode', 'promo disc%', 'promo discount%', 'promo price1',
    'promo price inc tax1', 'promo price inc vat1', 'margin%'
]

# Select only columns that exist in promo file
promo_cols = [col for col in possible_promo_cols if col in promo_df.columns]

# ====== MERGE DATA ======
# Fix merge: sales_df has 'item code', promo_df has 'barcode'
merged_df = pd.merge(
    sales_df,
    promo_df[promo_cols],
    left_on='item code',
    right_on='barcode',
    how='left',
    suffixes=('', '_promo')
)

# ====== CREATE PROMO INCLUDED FLAG ======
merged_df["promo included"] = merged_df.apply(
    lambda row: "Yes" if any(pd.notnull(row[col]) for col in promo_cols if col != "barcode") else "No",
    axis=1
)

# ====== REORDER COLUMNS ======
preferred_order = [
    "promo included", "barcode", "item name", "unit", "cf", "cost price", "selling", 
    "vat%", "selling inc vat"
]
extra_cols = [col for col in merged_df.columns if col not in preferred_order]
merged_df = merged_df[[c for c in preferred_order if c in merged_df.columns] + extra_cols]

# ====== COLOR STYLE ======
def highlight_promo(val):
    color = "#A7F3D0" if val == "Yes" else "#FEE2E2"
    return f"background-color: {color}"

# ====== DISPLAY ======
st.subheader("📈 Sales Data with Promotion Details")
st.dataframe(
    merged_df.style.applymap(highlight_promo, subset=["promo included"]),
    use_container_width=True
)

# ====== METRICS ======
total_items = len(merged_df)
promo_items = len(merged_df[merged_df["promo included"] == "Yes"])
non_promo_items = total_items - promo_items

# Compute average margin if exists
margin_cols = [col for col in merged_df.columns if "margin" in col]
avg_margin = round(merged_df[margin_cols].mean(numeric_only=True).mean(), 2) if margin_cols else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Items", total_items)
col2.metric("Promo Items", promo_items)
col3.metric("Non-Promo Items", non_promo_items)
col4.metric("Avg Promo Margin (%)", avg_margin)
