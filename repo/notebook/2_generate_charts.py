import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import json

plt.rcParams['font.family'] = 'DejaVu Sans'
NAVY = '#1F3864'
BLUE = '#2E75B6'
LIGHT = '#8FAADC'
GREEN = '#2E7D32'
RED = '#C00000'
GREY = '#666666'

with open('../dashboard/dashboard_data.json') as f:
    D = json.load(f)

IMG = '../images/'

def style_ax(ax, title):
    ax.set_title(title, fontsize=13, fontweight='bold', color=NAVY, pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.tick_params(colors='#444444', labelsize=9)

# ---------------- 1. Monthly trend + forecast ----------------
fig, ax = plt.subplots(figsize=(10, 4.5))
labels = D['monthly_trend']['labels']
actual = D['monthly_trend']['actual_sales']
forecast = D['monthly_trend']['forecast_sales']
x = np.arange(len(labels))
ax.plot(x, actual, color=BLUE, linewidth=2.2, label='Sales Aktual')
ax.plot(x, forecast, color=RED, linewidth=2.2, linestyle='--', label='Forecast (Trend Linear)')
ax.set_xticks(x[::4])
ax.set_xticklabels([labels[i] for i in range(0, len(labels), 4)], rotation=45, ha='right')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v/1000:.0f}K'))
ax.legend(frameon=False, fontsize=10)
style_ax(ax, 'Tren Sales Bulanan & Forecast 6 Bulan ke Depan')
plt.tight_layout()
plt.savefig(IMG + 'monthly_trend_forecast.png', dpi=150)
plt.close()

# ---------------- 2. Sales & Profit Margin by Category ----------------
cat = pd.DataFrame(D['category'])
fig, ax1 = plt.subplots(figsize=(8, 4.5))
bars = ax1.bar(cat['Category'], cat['Sales'], color=BLUE, width=0.5, label='Sales')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v/1000:.0f}K'))
ax1.set_ylabel('Sales ($)', color=BLUE)
ax2 = ax1.twinx()
ax2.plot(cat['Category'], cat['Profit Margin'] * 100, color=RED, marker='o', linewidth=2.2, label='Profit Margin (%)')
ax2.set_ylabel('Profit Margin (%)', color=RED)
ax2.set_ylim(0, 20)
for i, v in enumerate(cat['Profit Margin'] * 100):
    ax2.annotate(f'{v:.1f}%', (i, v + 0.8), ha='center', fontsize=9, color=RED, fontweight='bold')
style_ax(ax1, 'Sales vs Profit Margin per Kategori')
ax1.spines['right'].set_visible(True)
plt.tight_layout()
plt.savefig(IMG + 'sales_by_category.png', dpi=150)
plt.close()

# ---------------- 3. Profit by region ----------------
reg = pd.DataFrame(D['region']).sort_values('Profit', ascending=True)
fig, ax = plt.subplots(figsize=(8, 4))
colors = [RED if v < 45000 else BLUE for v in reg['Profit']]
ax.barh(reg['Region'], reg['Profit'], color=colors)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v/1000:.0f}K'))
for i, v in enumerate(reg['Profit']):
    ax.annotate(f'${v/1000:.0f}K', (v + 1500, i), va='center', fontsize=9, fontweight='bold', color='#333333')
style_ax(ax, 'Profit per Region')
plt.tight_layout()
plt.savefig(IMG + 'profit_by_region.png', dpi=150)
plt.close()

# ---------------- 4. Top 10 products by profit ----------------
top = pd.DataFrame(D['top_products']).head(10).sort_values('Profit')
fig, ax = plt.subplots(figsize=(9, 5))
names = [n if len(n) < 42 else n[:39] + '...' for n in top['Product Name']]
ax.barh(names, top['Profit'], color=GREEN)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'${v/1000:.0f}K'))
style_ax(ax, 'Top 10 Produk Berdasarkan Profit')
plt.tight_layout()
plt.savefig(IMG + 'top_products.png', dpi=150)
plt.close()

# ---------------- 5. RFM segment distribution ----------------
seg = D['rfm_distribution']
fig, ax = plt.subplots(figsize=(6.5, 5.5))
colors_map = {'Champions': GREEN, 'Loyal Customers': BLUE, 'At Risk / Lost': RED,
              'New / Occasional': '#F2A104', 'Needs Attention': '#999999'}
labels_id = list(seg.keys())
values = list(seg.values())
wedges, texts, autotexts = ax.pie(values, labels=labels_id, autopct='%1.0f%%', startangle=90,
                                    colors=[colors_map[l] for l in labels_id],
                                    textprops={'fontsize': 9.5})
for at in autotexts:
    at.set_color('white')
    at.set_fontweight('bold')
ax.set_title('Distribusi Segmen Customer (RFM)', fontsize=13, fontweight='bold', color=NAVY, pad=14)
plt.tight_layout()
plt.savefig(IMG + 'rfm_segments.png', dpi=150)
plt.close()

print("Semua chart PNG berhasil dibuat di folder images/")
