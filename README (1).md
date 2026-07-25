# Cafe Sales — Data Cleaning & Analysis (Pandas / NumPy)

An end-to-end pandas/NumPy project: taking a messy, real-world-style cafe
sales dataset (missing values, placeholder strings like `"ERROR"` and
`"UNKNOWN"`, inconsistent types) and turning it into a clean dataset plus
business insights — using only pandas and NumPy, no plotting libraries.

## Dataset

- `dirty_cafe_sales.csv` — 10,000 transactions with 8 columns: transaction
  ID, item, quantity, price per unit, total spent, payment method,
  location, transaction date.
- Deliberately "dirty": missing values, and placeholder strings
  (`ERROR`, `UNKNOWN`, `N/A`, etc.) standing in for missing data.

## What the project does

1. **Standardizes structure** — lowercases/snake_cases column names,
   converts placeholder strings to real `NaN`, casts columns to their
   proper dtypes (dates, numerics).
2. **Handles missing values deliberately, not just by dropping everything:**
   - Rows missing `item` or `transaction_date` are dropped (13.9% of rows)
     — these can't be meaningfully analyzed or imputed.
   - `quantity`, `price_per_unit`, and `total_spent` are linked by
     `total_spent = quantity × price_per_unit`. Where exactly two of the
     three are known, the third is **recovered algebraically** instead of
     estimated — only rows missing all three fall back to the column
     median.
   - `payment_method` and `location` are imputed using **random sampling
     from their observed distribution** (roughly even 3-way split for
     payment method, ~50/50 for location), with a fixed random seed for
     reproducibility.
3. **Derives** year/month/date fields for time-based analysis.
4. **Answers business questions:** top-selling items, revenue by location,
   most-used payment method, monthly revenue trends, which items are sold
   in high volume, and which items show the most consistent month-over-month
   revenue growth.
5. **Summarizes** everything into a single item-level summary table
   (revenue, quantity sold, average price, transaction count, % of total
   revenue) built entirely with `groupby`/`agg` — no plotting libraries.

## Key findings

- **Salad, Sandwich, and Smoothie** are the top 3 items by total revenue.
- Revenue is split almost evenly between **in-store and takeaway**
  locations.
- Payment method usage is close to an even 3-way split across cash,
  credit card, and digital wallet.
- Monthly revenue is fairly volatile month-to-month for most items
  rather than trending steadily in one direction — **Cake, Coffee, and
  Juice** showed revenue increases in the most months (6 of 11) of any
  items, but no item increased every single month.
- **Coffee** sells the highest total volume; **Cookie** the lowest, among
  items selling 500+ units.

## Repo structure

```
.
├── dirty_cafe_sales.csv          # raw input data
├── cafe_sales_analysis.py        # cleaning + analysis
├── cleaned_cafe_sales.csv        # output: cleaned dataset
└── README.md
```

## How to run

```bash
pip install pandas numpy
python cafe_sales_analysis.py
```

## Tools used

Python, pandas, NumPy.

## Notes on methodology

Missing `payment_method` and `location` values were imputed via random
sampling from the observed distribution rather than a single fixed value
(e.g. always "cash"), since always picking one category would distort the
true distribution. This is a reasonable simplifying assumption for a
learning project — a production pipeline would likely use a
predictive model or simply flag/exclude these rows from certain
analyses instead.
