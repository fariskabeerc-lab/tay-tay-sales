import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales Dashboard with Promotions", layout="wide")
st.title("📊 Full Sales Dashboard with Promotional Data")

# ===========================================================
# --- Load Sales and Promotion Data from Local Folder ---
# ===========================================================

# Replace with your actual file paths or names
sales_file_path = "sales_data.xlsx"          # example: "data/sales_data.xlsx"
promo_file_path = "promotional_items.xlsx"   # example: "data/promotional_items.xlsx"

# Load Excel files
try:
    sales_df = pd.read_excel(sales_file_path)
    promo_df = pd.read_excel(promo_file_path)
    st.success("✅ Both Sales and Promotional files loaded successfully.")
except Exception as e:
    st.error(f"❌ Error loading files: {e}")
    st.stop()

# ===========================================================
# --- Data Cleaning ---
# ===========================================================
sales_df.columns = [c.strip() for c in sales_df.columns]
promo_df.columns = [c.strip() for c in promo_df.columns]

if "Item Code" not in sales_df.columns:
    st.error("❌ 'Item Code' column missing in sales file.")
    st.stop()

if "Barcode" not in promo_df.columns:
    st.error("❌ 'Barcode' column missing in promo file.")
    st.stop()

# Clean merge keys
sales_df["Item Code"] = sales_df["Item Code"].astype(str).str.strip()
promo_df["Barcode"] = promo_df["Barcode"].astype(str).str.strip()

# ===========================================================
# --- Merge Sales and Promotion Data ---
# ===========================================================
merged_df = pd.merge(
    sales_df,
    promo_df[
        [
            "Barcode", "Item Name", "Promo Disc%", "Promo Price1",
            "Promo Price Inc Tax1", "Margin%"
        ]
    ],
    left_on="Item Code",
    right_on="Barcode",
    how="left"
)

# ===========================================================
# --- Add Computed Columns ---
# ===========================================================
# Flag promo inclusion
merged_df["Promo Included"] = merged_df["Promo Disc%"].notna().map({True: "Yes", False: "No"})

# GP% calculation
if "Total Profit" in merged_df.columns and "Total Sales" in merged_df.columns:
    merged_df["GP%"] = (merged_df["Total Profit"] / merged_df["Total Sales"]) * 100
else:
    merged_df["GP%"] = None

# Promo impact ratio
merged_df["Promo Impact"] = merged_df["Promo Disc%"] / merged_df["GP%"]

# Recommendation logic
def promo_suggestion(row):
    if row["Promo Included"] == "No":
        return "⚪ Not Promoted"
    elif pd.isna(row["Promo Impact"]):
        return "⚪ Not Promoted"
    elif row["Promo Impact"] > 1:
        return "❌ Avoid - GP dropped"
    elif 0.3 <= row["Promo Impact"] <= 1:
        return "✅ Focus - Good balance"
    elif row["Promo Impact"] < 0.3:
        return "⭐ Strong - Low discount, healthy GP"
    else:
        return "⚪ Neutral"

merged_df["Recommendation"] = merged_df.apply(promo_suggestion, axis=1)

# ===========================================================
# --- Display Data ---
# ===========================================================
st.markdown("### 📈 Sales Data with Promotion Status")

display_cols = [
    "Item Code", "Items", "Category", "Category4",
    "Qty Sold", "Total Sales", "Total Profit", "GP%",
    "Promo Included", "Promo Disc%", "Promo Price1",
    "Promo Price Inc Tax1", "Margin%", "Recommendation"
]
display_cols = [col for col in display_cols if col in merged_df.columns]

# Format numeric columns for readability
for col in ["Qty Sold", "Total Sales", "Total Profit", "Promo Disc%", "GP%", "Margin%"]:
    if col in merged_df.columns:
        merged_df[col] = merged_df[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "")

st.dataframe(merged_df[display_cols], use_container_width=True, hide_index=True)

# ===========================================================
# --- Download Option ---
# ===========================================================
csv = merged_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Download Merged Sales + Promo Data (CSV)",
    data=csv,
    file_name="Sales_with_Promotion_Data.csv",
    mime="text/csv"
)
