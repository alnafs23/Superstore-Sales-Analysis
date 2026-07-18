"""
Analisis Superstore Sales Performance
Menggantikan Power BI: semua perhitungan dilakukan di sini dengan pandas,
lalu diekspor ke JSON untuk dashboard HTML interaktif dan ke PNG untuk README.
"""
import pandas as pd
import numpy as np
import json

df = pd.read_csv('../data/Superstore_Orders_Clean.csv', parse_dates=['Order Date', 'Ship Date'])
df['Order Month'] = df['Order Date'].values.astype('datetime64[M]')
df['Order Year'] = df['Order Date'].dt.year

out = {}

# ---------------- KPI ----------------
total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
profit_margin = total_profit / total_sales
distinct_orders = df['Order ID'].nunique()
avg_order_value = total_sales / distinct_orders

sales_2017 = df.loc[df['Order Year'] == 2017, 'Sales'].sum()
sales_2018 = df.loc[df['Order Year'] == 2018, 'Sales'].sum()
yoy_growth = (sales_2018 - sales_2017) / sales_2017

out['kpi'] = {
    'total_sales': round(total_sales, 2),
    'total_profit': round(total_profit, 2),
    'profit_margin': round(profit_margin, 4),
    'distinct_orders': int(distinct_orders),
    'avg_order_value': round(avg_order_value, 2),
    'yoy_growth': round(yoy_growth, 4),
}
print("KPI:", out['kpi'])

# ---------------- Monthly trend + forecast ----------------
monthly = df.groupby('Order Month').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
monthly = monthly.sort_values('Order Month').reset_index(drop=True)
monthly['idx'] = np.arange(1, len(monthly) + 1)

# Linear trend forecast (sama seperti FORECAST() di Excel) untuk 6 bulan ke depan
coeffs = np.polyfit(monthly['idx'], monthly['Sales'], 1)
future_idx = np.arange(len(monthly) + 1, len(monthly) + 7)
future_sales = np.polyval(coeffs, future_idx)
future_months = pd.date_range(monthly['Order Month'].max() + pd.DateOffset(months=1), periods=6, freq='MS')

trend_labels = [d.strftime('%b-%Y') for d in monthly['Order Month']] + [d.strftime('%b-%Y') for d in future_months]
actual_sales = monthly['Sales'].round(2).tolist() + [None] * 6
forecast_sales = [None] * (len(monthly) - 1) + [round(monthly['Sales'].iloc[-1], 2)] + [round(v, 2) for v in future_sales]

out['monthly_trend'] = {
    'labels': trend_labels,
    'actual_sales': actual_sales,
    'forecast_sales': forecast_sales,
}
print("Forecast bulan depan (6 bulan):", [round(v,2) for v in future_sales])

# ---------------- Category & Region ----------------
cat = df.groupby('Category').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
cat['Profit Margin'] = cat['Profit'] / cat['Sales']
out['category'] = cat.round(4).to_dict(orient='records')
print("\nKategori:\n", cat)

region = df.groupby('Region').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
out['region'] = region.round(2).to_dict(orient='records')
print("\nRegion:\n", region)

subcat = df.groupby(['Category', 'Sub-Category']).agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()
subcat['Profit Margin'] = subcat['Profit'] / subcat['Sales']
out['subcategory'] = subcat.round(4).to_dict(orient='records')

segment = df.groupby('Segment').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'),
                                     Orders=('Order ID', 'nunique')).reset_index()
segment['AOV'] = segment['Sales'] / segment['Orders']
out['segment'] = segment.round(2).to_dict(orient='records')

# ---------------- Product performance ----------------
prod = df.groupby('Product Name').agg(Category=('Category', 'first'), Sales=('Sales', 'sum'),
                                       Profit=('Profit', 'sum'), Quantity=('Quantity', 'sum')).reset_index()
top15 = prod.sort_values('Profit', ascending=False).head(15).round(2)
bottom15 = prod.sort_values('Profit', ascending=True).head(15).round(2)
out['top_products'] = top15.to_dict(orient='records')
out['bottom_products'] = bottom15.to_dict(orient='records')
print("\nTop 5 produk (profit):\n", top15.head())
print("\nBottom 5 produk (rugi):\n", bottom15.head())

# ---------------- RFM Segmentation ----------------
snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)
rfm = df.groupby('Customer Name').agg(
    Recency=('Order Date', lambda x: (snapshot_date - x.max()).days),
    Frequency=('Order ID', 'nunique'),
    Monetary=('Sales', 'sum')
).reset_index()

rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1]).astype(int)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4]).astype(int)
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4]).astype(int)

def segment_label(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    elif r >= 3 and f >= 3:
        return 'Loyal Customers'
    elif r <= 2 and f <= 2 and m <= 2:
        return 'At Risk / Lost'
    elif r >= 3 and f <= 2:
        return 'New / Occasional'
    else:
        return 'Needs Attention'

rfm['Segment'] = rfm.apply(segment_label, axis=1)
seg_dist = rfm['Segment'].value_counts().reindex(
    ['Champions', 'Loyal Customers', 'At Risk / Lost', 'New / Occasional', 'Needs Attention']
).fillna(0).astype(int)
out['rfm_distribution'] = seg_dist.to_dict()
out['rfm_avg_monetary'] = rfm.groupby('Segment')['Monetary'].mean().round(2).reindex(seg_dist.index).to_dict()
print("\nDistribusi segmen RFM:\n", seg_dist)

rfm.to_csv('../data/customer_rfm_segmentation.csv', index=False)

with open('../dashboard/dashboard_data.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)

print("\nData JSON untuk dashboard berhasil disimpan.")
