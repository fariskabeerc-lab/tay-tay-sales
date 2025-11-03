import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales & Promotion Dashboard", layout="wide")
st.title("📊 Sales and Promotion Dashboard")

# ====== READ DATA ======
# Update these paths
sales_file = "tay tay jan to oct.Xlsx"          # Example: "C:/Users/admin/Desktop/sales_data.xlsx"
promo_file = "ANNIVERSARY OFFER LIST (1).xlsx"    # Example: "C:/Users/admin/Desktop/promo_data.xlsx"

# Read Excel files
sales_df = pd.read_excel(sales_file)
promo_df = pd.read_excel(promo_file)

# ====== MERGE DATA ======
# Merge using Barcode column
merged_df = pd.merge(
    sales_df,
    promo_df[['Barcode', 'Promo Disc%', 'Promo Price1', 'Promo Price Inc Tax1', 'Margin%']],
    on='Barcode',
    how='left',
    suffixes=('', '_promo')
)

# Create Promo Included column
merged_df["Promo Included"] = merged_df["Promo Disc%_promo"].apply(
    lambda x: "Yes" if pd.notnull(x) and x > 0 else "No"
)

# ====== REORDER COLUMNS ======
cols = ["Promo Included", "Barcode", "Item Name", "Unit", "CF", "Cost Price", "Selling", "Vat%", 
        "Selling Inc Vat", "Promo Disc%_promo", "Promo Price1_promo", "Promo Price Inc Tax1_promo", "Margin%_promo"]
merged_df = merged_df[[col for col in cols if col in merged_df.columns]]

# ====== COLOR STYLE ======
def highlight_promo(val):
    color = "#A7F3D0" if val == "Yes" else "#FEE2E2"
    return f"background-color: {color}"

# ====== DISPLAY ======
st.subheader("📈 Sales Data with Promotion Details")
st.dataframe(
    merged_df.style.applymap(highlight_promo, subset=["Promo Included"]),
    use_container_width=True
)

# ====== METRICS ======
total_items = len(merged_df)
promo_items = len(merged_df[merged_df["Promo Included"] == "Yes"])
non_promo_items = len(merged_df[merged_df["Promo Included"] == "No"])
avg_margin = round(merged_df["Margin%_promo"].mean(skipna=True), 2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Items", total_items)
col2.metric("Promo Items", promo_items)
col3.metric("Non-Promo Items", non_promo_items)
col4.metric("Avg Promo Margin (%)", avg_margin)
