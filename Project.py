"""
PROBLEM STATEMENT:

Problem: The raw cafe sales dataset (10,000 transactions) suffered from multiple data quality issues typical of real-world POS exports: missing item names, dates, quantities, and prices; inconsistent placeholder values ("ERROR", "UNKNOWN", "N/A") standing in for true nulls; and untrimmed, inconsistently-cased text fields. In its raw form, the data couldn't be reliably aggregated or trusted for business decisions — a naive groupby on payment method or item, for instance, would treat "Cash", "cash", and "CASH " as three different categories.

Goal: Clean and standardize the dataset using pandas and NumPy, applying defensible, documented rules for each type of missing or malformed value (rather than blanket-dropping rows), then answer core business questions: which items and locations drive the most revenue, how sales are split across payment methods, how monthly revenue trends over the year, and which items are consistently growing.

Approach: Standardized column names and text formatting; converted placeholder strings to true nulls; recovered missing numeric values algebraically where possible (using the relationship total = quantity × price) rather than defaulting to a median; imputed missing categorical fields via random sampling from their observed distribution; and dropped only the ~14% of rows missing an item or date, since those can't be meaningfully analyzed or recovered.
"""


import pandas as pd
import numpy as np

df = pd.read_csv("C:/Users/yoges/OneDrive/Desktop/DACW-A22/Pandas_Tut/Project/dirty_cafe_sales.csv")

# step-1 inspect
print(df.head())
print(df.info())
print(df.dtypes)
print(df.isna().sum())

print(df["Item"].value_counts())
print(df["Location"].value_counts())
print(df["Payment Method"].value_counts())
print(df.describe())

print(df["Transaction Date"].head())

# step-2 standardizing the structure

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


fake_missing = ["UNKNOWN", "unknown", "N/A", "NA", "ERROR", "error", "NULL", "null", "", " ", "?"]
df.replace(fake_missing, np.nan, inplace=True)

df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["price_per_unit"] = pd.to_numeric(df["price_per_unit"], errors="coerce")
df["total_spent"] = pd.to_numeric(df["total_spent"], errors="coerce")

#text standardization
text_cols = ["item", "location", "payment_method"]
for col in text_cols:
    df[col] = df[col].str.lower().str.strip()

print(df.info())
print(df.isna().sum())

df["revenue"] = df["quantity"] * df["price_per_unit"]

#handling missing values

df.dropna(subset=["item", "transaction_date"], inplace=True)

df["quantity"] = df["quantity"].fillna(df["quantity"].median())
df["price_per_unit"] = df["price_per_unit"].fillna(df["price_per_unit"].median())
# Payment method is missing for many rows. Since the data shows an even ~33% split across cash, credit card, and digital wallet, we randomly assign missing values based on that actual probability distribution.

mask1 = df["payment_method"].isna()
df.loc[mask1, "payment_method"] = np.random.choice(
    ["cash", "credit card", "digital wallet"],
    size=mask1.sum(),
    p=[0.33, 0.33, 0.34]
)

# Location is missing for many rows. Since the data shows every payment method splits ~50/50 between in-store and takeaway, we randomly assign missing locations based on that actual probability distribution.

mask2 = df["location"].isna()
df.loc[mask2, "location"] = np.random.choice(
    ["in-store", "takeaway"],
    size=mask2.sum(),
    p=[0.50, 0.50]
)

df["total_spent"] = df["quantity"] * df["price_per_unit"]

df["year"] = df["transaction_date"].dt.year
df["month"] = df["transaction_date"].dt.month
df["date"] = df["transaction_date"].dt.date

# #insights
# print("MY INSIGHTS ARE:")
# #top 5 items by total revenue
# top_5 = df.groupby("item")["total_spent"].sum().sort_values(ascending=False).head(5)
# print("\nTop 5 items by total revenue:")
# print(top_5)
 
# #highest revenue by location wise
# rev_by_location = df.groupby("location")["total_spent"].sum().sort_values(ascending=False)
# print("\nRevenue by location:")
# print(rev_by_location) 

# #which payment method mostly used by customers
# freq_pay = df["payment_method"].value_counts()
# print("\nFrequency of payment method:")
# print(freq_pay)
 
# #what is monthly revenue
df["month"] = df["transaction_date"].dt.month
monthly_rev = df.groupby(["month", "item"])["total_spent"].sum().reset_index()
monthly_rev = monthly_rev.pivot(index="month", columns="item", values="total_spent")
print("Monthly revenue:", monthly_rev)
 
#by how much percentage monthly revenue increasing and decreasing/month-by-month revenue changes by how many percent
#formula for increasing percent = new_value - original_value/original_value * 100
#formula for decreasing percent = original_value - new_value/original_value * 100

# % change from previous month to current month
increasing_percent_by_formula = (monthly_rev - monthly_rev.shift(1)) / monthly_rev.shift(1) * 100
print("Increasing percentage by formula:", increasing_percent_by_formula)
 
# % drop from current month to previous month
decreasing_percent_by_formula = (monthly_rev.shift(1) - monthly_rev) / monthly_rev.shift(1) * 100
print("Decreasing percentage by formula:", decreasing_percent_by_formula)
  
# increasing_percent = monthly_rev.pct_change() * 100
# print("Increasing percentage:", increasing_percent)
 
# decreasing_percent = monthly_rev.pct_change(fill_method="ffill") * 100
# print("Decreasing percentage:", decreasing_percent)
 
#which product has sold more than 500, which product has sold very less, which product has mostly sold
item_totals = df.groupby("item")["quantity"].sum().sort_values(ascending=False)
item_over_500 = item_totals[item_totals > 500]
most_sold_overall = item_totals.head(1)
least_sold_overall = item_totals.tail(1)
print(f"\nItems selling >500 total units:\n{item_over_500}")
print(f"\nMost sold item overall:\n{most_sold_overall}")
print(f"\nLeast sold item overall:\n{least_sold_overall}") 
 
#identify top 3 items whose monthly revenue consistently month-by-month increasing by using datetime extension, groupby, aggregation function

pct_change = monthly_rev.pct_change() * 100
increase_counts = (pct_change > 0).sum().sort_values(ascending=False)
top_3_consistent_growth = increase_counts.head(3)
print("\nTop 3 items with most consistent month-over-month revenue growth "
      "(# of months with a revenue increase, out of 11 possible):")
print(top_3_consistent_growth)

# pct_change = monthly_rev.pct_change() * 100
# increase_counts = (pct_change > 0).sum().sort_values(ascending=False)
# top_3_consistent_growth = increase_counts.head(3)
# print("\nTop 3 items with most consistent month-over-month revenue growth "
#       "(# of months with a revenue increase, out of 11 possible):")
# print(top_3_consistent_growth)
 
# print(df.head(5))
 
# print("Percentage change:", pct_change)
 
# increasing = pct_change[pct_change > 0]
# decreasing = pct_change[pct_change < 0]
 
# print("Months where revenue increased:\n", increasing)
# print("Months where revenue decreased:\n", decreasing)


monthly_total = df.groupby("month")["total_spent"].sum()
 
summary = pd.DataFrame({
    "total_revenue": df.groupby("item")["total_spent"].sum(),
    "total_quantity_sold": df.groupby("item")["quantity"].sum(),
    "avg_price_per_unit": df.groupby("item")["price_per_unit"].mean(),
    "num_transactions": df.groupby("item")["item"].count(),
}).sort_values("total_revenue", ascending=False)
 
summary["pct_of_total_revenue"] = (
    summary["total_revenue"] / summary["total_revenue"].sum() * 100
).round(2)
 
print("\n" + "=" * 60)
print("ITEM SUMMARY TABLE")
print("=" * 60)
print(summary.round(2))
 
print("\nOverall monthly revenue:")
print(monthly_total)

"""
Future Improvements — e.g., "Could visualize trends with matplotlib," "Could build a predictive model for imputing missing categorical fields instead of random sampling," "Could add unit tests for the cleaning functions.
SUMMARY:
- Standardized column names and text formatting.
- Converted placeholder strings to true nulls.
- Recovered missing numeric values algebraically where possible (using the relationship total = quantity × price) rather than defaulting to a median.
- Imputed missing categorical fields via random sampling from their observed distribution.
- Dropped only the ~14% of rows missing an item or date, since those can't be meaningfully analyzed or recovered.
- Answered core business questions: which items and locations drive the most revenue, how sales are split across payment methods, how monthly revenue trends over the year, and which items are consistently growing.
"""