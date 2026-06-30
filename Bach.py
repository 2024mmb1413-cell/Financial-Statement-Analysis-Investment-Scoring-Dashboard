import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
st.set_page_config(
    page_title="Financial Statement Analysis Dashboard",
    layout="wide"
)

st.title(" Financial Statement Analysis Dashboard")

df = pd.read_excel("Company_data2.xlsx")
df['Year'] = df['Year'].str.extract('(\d+)').astype(int)
df = df.sort_values(['Company', 'Year'])
df['ROE'] = df['Profit for the year'] / df['Total equity']
df['Prev Assets'] = df.groupby('Company')['Total assets'].shift(1)
df['Avg Assets'] = (df['Total assets'] + df['Prev Assets']) / 2
df['Avg Assets'] = df['Avg Assets'].fillna(df['Total assets'])
df['ROA'] = df['Profit for the year'] / df['Avg Assets']
df['Net Margin'] = df['Profit for the year'] / df['Revenue from operation']
df['Debt_to_Equity'] = df['Total debt'] / df['Total equity']
df['Asset Turnover'] = df['Revenue from operation'] / df['Total assets']
df['Earnings Quality'] = df['Profit for the year'] / df['Profit before tax']
df['Revenue Growth'] = df.groupby('Company')['Revenue from operation'].pct_change()
df['Profit Growth'] = df.groupby('Company')['Profit for the year'].pct_change()
print(df[['Company','Year','ROE','ROA','Net Margin','Debt_to_Equity','Revenue Growth','Profit Growth']].head(10))
df = df.fillna(0)
def norm(col):
    return (col - col.min()) / (col.max() - col.min() + 1e-9)
df['roe_s'] = norm(df['ROE'])
df['roa_s'] = norm(df['ROA'])
df['margin_s'] = norm(df['Net Margin'])
df['rev_growth_s'] = norm(df['Revenue Growth'])
df['profit_growth_s'] = norm(df['Profit Growth'])
df['de_s'] = 1 - norm(df['Debt_to_Equity'])
df['roe_std'] = df.groupby('Company')['ROE'].transform('std')
df['stability_s'] = 1 - norm(df['roe_std'])
df['Investment Score'] = (
    0.20 * df['roe_s'] +
    0.10 * df['roa_s'] +
    0.10 * df['margin_s'] +
    
    0.15 * df['rev_growth_s'] +
    0.10 * df['profit_growth_s'] +
    
    0.20 * df['de_s'] +
    
    0.15 * df['stability_s']
) * 100
result = df.groupby('Company')['Investment Score'].mean().sort_values(ascending=False)
print("\n FINAL COMPANY RANKING:\n")
print(result)
print(df[['Company','Year','Investment Score']].sort_values('Investment Score', ascending=False))
rev_cagr = df.groupby('Company').apply(
    lambda x: (
        x['Revenue from operation'].iloc[-1] /
        x['Revenue from operation'].iloc[0]
    ) ** (1 / (x['Year'].iloc[-1] - x['Year'].iloc[0])) - 1
).rename('Revenue CAGR')

df = df.merge(rev_cagr, on='Company')
profit_cagr = df.groupby('Company').apply(
    lambda x: (
        x['Profit for the year'].iloc[-1] /
        x['Profit for the year'].iloc[0]
    ) ** (1 / (x['Year'].iloc[-1] - x['Year'].iloc[0])) - 1
).rename('Profit CAGR')

df = df.merge(profit_cagr, on='Company')
print(df[['Company', 'Revenue CAGR', 'Profit CAGR']].drop_duplicates())
st.sidebar.header("Filters")

company = st.sidebar.selectbox(
    "Select Company",
    df["Company"].unique()
)

temp = df[df["Company"] == company]
st.header(f"{company} Financial Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Investment Score",
    f"{temp['Investment Score'].iloc[-1]:.2f}"
)

col2.metric(
    "ROE",
    f"{temp['ROE'].iloc[-1]*100:.2f}%"
)

col3.metric(
    "Revenue CAGR",
    f"{temp['Revenue CAGR'].iloc[-1]*100:.2f}%"
)
st.header("📋 Financial Ratios")

ratio_df = temp[[
    "Year",
    "ROE",
    "ROA",
    "Net Margin",
    "Debt_to_Equity",
    "Asset Turnover",
    "Earnings Quality",
    "Revenue Growth",
    "Profit Growth"
]].copy()

ratio_df["ROE"] *= 100
ratio_df["ROA"] *= 100
ratio_df["Net Margin"] *= 100
ratio_df["Revenue Growth"] *= 100
ratio_df["Profit Growth"] *= 100

ratio_df = ratio_df.round(2)

ratio_df.columns = [
    "Year",
    "ROE (%)",
    "ROA (%)",
    "Net Margin (%)",
    "Debt-to-Equity",
    "Asset Turnover",
    "Earnings Quality",
    "Revenue Growth (%)",
    "Profit Growth (%)"
]

st.dataframe(
    ratio_df,
    use_container_width=True
)
st.subheader("Revenue Trend")

fig, ax = plt.subplots(figsize=(8,5))

ax.plot(
    temp["Year"],
    temp["Revenue from operation"],
    marker='o',
    linewidth=2
)

ax.set_title(f"{company} Revenue Trend")
ax.set_xlabel("Year")
ax.set_ylabel("Revenue")
ax.grid(True)

st.pyplot(fig)
plt.close(fig)
st.subheader("Profit Trend")

fig, ax = plt.subplots(figsize=(8,5))

ax.plot(
    temp["Year"],
    temp["Profit for the year"],
    marker='o',
    linewidth=2
)

ax.set_title(f"{company} Profit Trend")
ax.set_xlabel("Year")
ax.set_ylabel("PAT")
ax.grid(True)

st.pyplot(fig)
plt.close(fig)
st.subheader("ROE Trend")

fig, ax = plt.subplots(figsize=(8,5))

ax.plot(
    temp["Year"],
    temp["ROE"] * 100,
    marker='o',
    linewidth=2
)

ax.set_title(f"{company} ROE Trend")
ax.set_xlabel("Year")
ax.set_ylabel("ROE (%)")
ax.grid(True)

st.pyplot(fig)
plt.close(fig)
st.subheader("Debt-to-Equity Trend")

fig, ax = plt.subplots(figsize=(8,5))

ax.plot(
    temp["Year"],
    temp["Debt_to_Equity"],
    marker='o',
    linewidth=2
)

ax.grid(True)

st.pyplot(fig)
plt.close(fig)
st.subheader("Investment Score Trend")

fig, ax = plt.subplots(figsize=(8,5))

ax.plot(
    temp["Year"],
    temp["Investment Score"],
    marker='o',
    linewidth=3
)

ax.set_ylim(0,100)
ax.grid(True)

st.pyplot(fig)
plt.close(fig)
avg = df.groupby("Company")["Investment Score"].mean()

plt.figure(figsize=(6,5))

avg.plot(kind='bar')

plt.ylabel("Average Investment Score")

plt.title("Company Ranking")
st.pyplot(plt.gcf())
plt.close()

cagr = df[['Company', 'Revenue CAGR']].drop_duplicates()

plt.figure(figsize=(6,5))

plt.bar(
    cagr['Company'],
    cagr['Revenue CAGR'] * 100
)

plt.ylabel("Revenue CAGR (%)")
plt.title("Revenue CAGR Comparison")

st.pyplot(plt.gcf())
plt.close()
