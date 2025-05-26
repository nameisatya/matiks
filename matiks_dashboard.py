'''import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Cache data loading for better performance
@st.cache_data
def load_data():
    df = pd.read_csv("Matiks - Data Analyst Data - Sheet1.csv")
    df.columns = df.columns.str.replace(" ", "_").str.strip()

    # Parse date columns
    df["Signup_Date"] = pd.to_datetime(df["Signup_Date"], errors='coerce')
    df["Last_Login"] = pd.to_datetime(df["Last_Login"], errors='coerce')

    # Calculate Days Since Last Login and Days Active
    df["Days_Since_Last_Login"] = (df["Last_Login"].max() - df["Last_Login"]).dt.days
    df["Days_Active"] = (df["Last_Login"] - df["Signup_Date"]).dt.days.replace(0, 1)

    # Sessions per day metric
    df["Sessions_Per_Day"] = df["Total_Play_Sessions"] / df["Days_Active"]

    # High-value user flag (top 10% by revenue)
    df["High_Value_User"] = df["Total_Revenue_USD"] >= df["Total_Revenue_USD"].quantile(0.9)

    # Churn risk flag based on sessions, last login, and avg session duration
    df["Churn_Risk"] = (
        (df["Total_Play_Sessions"] < 5) | 
        (df["Days_Since_Last_Login"] > 14) | 
        (df["Avg_Session_Duration_Min"] < 5)
    )

    return df

df = load_data()

st.set_page_config(page_title="Matiks Analytics Dashboard", layout="wide")
st.title("\U0001F4CA Matiks Analytics Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
device_filter = st.sidebar.multiselect(
    "Select Device Type:", 
    options=df["Device_Type"].unique(), 
    default=list(df["Device_Type"].unique())
)
segment_filter = st.sidebar.multiselect(
    "Select Subscription Tier:", 
    options=df["Subscription_Tier"].unique(), 
    default=list(df["Subscription_Tier"].unique())
)

filtered_df = df[
    (df["Device_Type"].isin(device_filter)) & 
    (df["Subscription_Tier"].isin(segment_filter))
]

# KPIs in columns for responsive layout
col1, col2, col3 = st.columns(3)
col1.metric("Total Users", len(filtered_df))
col2.metric("Revenue ($)", f"{filtered_df['Total_Revenue_USD'].sum():,.2f}")
col3.metric("Churn Risk Users", filtered_df["Churn_Risk"].sum())

# Prepare data for DAU/WAU/MAU
filtered_df["Login_Date"] = filtered_df["Last_Login"].dt.date
dau = filtered_df.groupby("Login_Date")["User_ID"].nunique()

# Use 7-day rolling average for WAU and 14-day rolling average for MAU
wau = dau.rolling(7).mean()
mau = dau.rolling(14).mean()  # shorter window ensures MAU is more visible

st.subheader("\U0001F4C8 DAU / WAU / MAU (Actual)")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(dau.index, dau, label="DAU", marker='o')
ax.plot(wau.index, wau, label="WAU", marker='s')
ax.plot(mau.index, mau, label="MAU", marker='^')

ax.set_title("User Activity Over Time")
ax.set_ylabel("Unique Users")
ax.legend()

# Improve date formatting on x-axis
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
fig.autofmt_xdate()

st.pyplot(fig)

# Revenue Trend Bar Chart
st.subheader("\U0001F4B0 Revenue Trend")

rev_trend = (
    filtered_df.groupby(filtered_df["Last_Login"].dt.to_period("M"))["Total_Revenue_USD"]
    .sum()
    .sort_index()
)
rev_trend.index = rev_trend.index.to_timestamp().strftime('%b %Y')

fig2, ax2 = plt.subplots(figsize=(10, 5))
rev_trend.plot(kind="bar", color="green", ax=ax2)

ax2.set_title("Monthly Revenue")
ax2.set_ylabel("USD")
ax2.set_xlabel("Month")
fig2.autofmt_xdate()

st.pyplot(fig2)

# Reordered churn reason logic to prioritize most critical churn causes
def churn_reason(row):
    if row["Days_Since_Last_Login"] > 14:
        return "Inactive >14 Days"
    elif row["Avg_Session_Duration_Min"] < 5:
        return "Short Sessions (<5 min)"
    elif row["Total_Play_Sessions"] < 5:
        return "Low Sessions (<5)"
    return "Engaged"

filtered_df["Churn_Category"] = filtered_df.apply(churn_reason, axis=1)
churn_counts = filtered_df["Churn_Category"].value_counts()

st.subheader("\U0001F4C9 Churn Segments")
fig3, ax3 = plt.subplots(figsize=(6, 6))
churn_counts.plot(kind="pie", autopct="%1.1f%%", startangle=90, ax=ax3)
ax3.set_ylabel("")
ax3.set_title("Churn Category Breakdown")
st.pyplot(fig3)

# High-Value Users Bar Chart
st.subheader("\U0001F3C6 High-Value Users Breakdown")
hv_counts = filtered_df["High_Value_User"].value_counts().rename({True: "High Value", False: "Others"})

fig4, ax4 = plt.subplots(figsize=(6, 4))
hv_counts.plot(kind="bar", color=["gold", "gray"], ax=ax4)
ax4.set_title("High-Value Users vs Others")
ax4.set_ylabel("User Count")
ax4.set_xlabel("User Type")
st.pyplot(fig4)

# Footer and Dashboard Link
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; font-size:14px; color:gray;">
    Matiks Analyst Task | Built with Streamlit &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; 
    🔗 <a href="https://matiks-bhj9w9wj7hqekq3ryzachp.streamlit.app/" target="_blank">Live Dashboard Link</a>
    </div>
    """,
    unsafe_allow_html=True,
)
'''

import streamlit as st
import pandas as pd
import altair as alt

# Load the data
df = pd.read_csv("Matiks - Data Analyst Data - Sheet1.csv")

# Preprocess dates
df['Signup_Date'] = pd.to_datetime(df['Signup_Date'], format='%d-%b-%y')
df['Last_Login'] = pd.to_datetime(df['Last_Login'], format='%d-%b-%y')
df['Days_Since_Last_Login'] = (pd.to_datetime("2025-05-26") - df['Last_Login']).dt.days
df['Churn_Risk'] = df['Days_Since_Last_Login'] > 14
df['Signup_Month'] = df['Signup_Date'].dt.to_period('M').astype(str)
df['Last_Login_Month'] = df['Last_Login'].dt.to_period('M').astype(str)

st.title("📊 Matiks User Analytics Dashboard")

# Filters
with st.sidebar:
    st.header("Filters")
    device = st.multiselect("Device Type", options=df['Device_Type'].unique(), default=df['Device_Type'].unique())
    tier = st.multiselect("Subscription Tier", options=df['Subscription_Tier'].unique(), default=df['Subscription_Tier'].unique())
    mode = st.multiselect("Game Mode", options=df['Preferred_Game_Mode'].unique(), default=df['Preferred_Game_Mode'].unique())

# Apply filters
filtered_df = df[df['Device_Type'].isin(device) & df['Subscription_Tier'].isin(tier) & df['Preferred_Game_Mode'].isin(mode)]

# DAU / WAU / MAU approximation using last login
login_counts = filtered_df.groupby('Last_Login').size().reset_index(name='Active_Users')
st.subheader("📈 Daily Active Users (DAU)")
st.line_chart(login_counts.set_index('Last_Login'))

# Revenue trend
rev_month = filtered_df.groupby('Last_Login_Month')['Total_Revenue_USD'].sum().reset_index()
st.subheader("💰 Monthly Revenue Trend")
st.bar_chart(rev_month.set_index('Last_Login_Month'))

# Breakdown by device type
st.subheader("📱 Revenue by Device Type")
device_rev = filtered_df.groupby('Device_Type')['Total_Revenue_USD'].sum().reset_index()
st.altair_chart(alt.Chart(device_rev).mark_bar().encode(x='Device_Type', y='Total_Revenue_USD', tooltip=['Device_Type', 'Total_Revenue_USD']), use_container_width=True)

# Churn risk overview
st.subheader("⚠️ Churn Risk Breakdown")
st.dataframe(filtered_df[['User_ID', 'Last_Login', 'Days_Since_Last_Login', 'Churn_Risk']].sort_values(by='Days_Since_Last_Login', ascending=False).head(10))

# High-value users
st.subheader("🌟 Top 10 High-Value Users")
hv_users = filtered_df.sort_values(by='Total_Revenue_USD', ascending=False).head(10)
st.table(hv_users[['Username', 'Total_Revenue_USD', 'Total_Hours_Played', 'Total_Play_Sessions']])
