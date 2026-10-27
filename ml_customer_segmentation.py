"""
ml_customer_segmentation.py - Customer segmentation with RFM + K-Means (ML extension)

What this script does:
  1. Builds RFM features for every customer from the cleaned tables
       Recency   = days since the customer's last order
       Frequency = number of orders
       Monetary  = total net revenue the customer generated
  2. Log-transforms and scales the features (K-Means is distance based)
  3. Compares k = 2..6 with inertia (elbow) and silhouette score
  4. Fits K-Means with k = 4 and gives each cluster a business name
  5. Saves one row per customer to reports/customer_segments.csv

Run (from any folder):  python python/ml_customer_segmentation.py
Needs: pip install pandas numpy scikit-learn
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42  # reproducible clusters
K = 4              # chosen number of segments (see step 3 for why)

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "processed"

# ------------------------------------------------------------- 1. Load data
orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
items = pd.read_csv(DATA / "order_items.csv")
products = pd.read_csv(DATA / "products.csv")

df = items.merge(orders, on="order_id").merge(products, on="product_id")

# Same business rule as v_order_details in the SQL project:
# cancelled orders are ignored, returned orders earn no revenue.
df = df[df["status"] != "Cancelled"].copy()
df["net_revenue"] = df["quantity"] * df["retail_price"] * (1 - df["discount_pct"])
df.loc[df["status"] == "Returned", "net_revenue"] = 0

# --------------------------------------------------------- 2. RFM features
# Snapshot = the day after the last order in the data ("today" for the analysis)
snapshot = orders["order_date"].max() + pd.Timedelta(days=1)

rfm = df.groupby("customer_id").agg(
    recency=("order_date", lambda s: (snapshot - s.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("net_revenue", "sum"),
)

# Money and counts are right-skewed, so use log1p to stop a few big values from
# dominating, then StandardScaler so R, F and M all have mean 0 and std 1.
X = StandardScaler().fit_transform(np.log1p(rfm))

# ----------------------------------------------------- 3. Choose k (4 here)
print("k | inertia | silhouette")
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(X)
    print(f"{k} | {km.inertia_:8.0f} | {silhouette_score(X, km.labels_):.3f}")
print("No sharp elbow, and silhouette is highest at k=2 (too coarse to act on).")
print(f"Using k={K}: four segments a marketing team can act on.\n")

# ------------------------------------------------------ 4. Final clustering
rfm["cluster"] = KMeans(n_clusters=K, n_init=10, random_state=RANDOM_STATE).fit_predict(X)

# Cluster numbers (0,1,2,3) are arbitrary, so name clusters from their profile:
profile = rfm.groupby("cluster")[["recency", "frequency", "monetary"]].mean()
by_money = profile["monetary"].sort_values(ascending=False).index.tolist()
names = {by_money[0]: "Champions (high value)", by_money[-1]: "Lapsed low-value"}
middle = [c for c in by_money[1:-1]]
middle.sort(key=lambda c: profile.loc[c, "recency"])  # most recent buyer first
names[middle[0]] = "Recently active"
names[middle[1]] = "At risk (slipping)"
rfm["segment"] = rfm["cluster"].map(names)

actions = {
    "Champions (high value)": "Reward and retain: loyalty perks, early access",
    "Recently active": "Nurture: cross-sell and push toward a repeat purchase",
    "At risk (slipping)": "Win-back: reminder emails and time-limited offers",
    "Lapsed low-value": "Low-cost reactivation only; do not overspend",
}

summary = rfm.groupby("segment").agg(
    customers=("monetary", "size"),
    avg_recency_days=("recency", "mean"),
    avg_orders=("frequency", "mean"),
    avg_revenue=("monetary", "mean"),
    total_revenue=("monetary", "sum"),
)
summary["revenue_share_pct"] = summary["total_revenue"] / summary["total_revenue"].sum() * 100
summary = summary.sort_values("avg_revenue", ascending=False)

print("=== Segment profile ===")
print(summary.drop(columns="total_revenue").round(1).to_string())
print("\n=== Suggested action per segment ===")
for seg in summary.index:
    print(f"{seg}: {actions[seg]}")

# ------------------------------------------------------------ 5. Save output
out = BASE / "reports" / "customer_segments.csv"
rfm.reset_index()[["customer_id", "recency", "frequency", "monetary", "segment"]].round(2).to_csv(
    out, index=False
)
print(f"\nSaved: {out.relative_to(BASE)}")
