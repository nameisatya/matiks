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

'''

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from sklearn.cluster import KMeans

# Title
st.title("Matiks User Behavior & Revenue Dashboard")

# Load data
uploaded_file = st.file_uploader("Upload user activity CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.rename(columns={"User ID": "User_ID"}, inplace=True)

    # Ensure datetime columns are parsed correctly
    df["Last_Login"] = pd.to_datetime(df["Last_Login"], errors="coerce")
    df["Sign_Up"] = pd.to_datetime(df["Sign_Up"], errors="coerce")

    # Drop rows with invalid dates
    df = df.dropna(subset=["Last_Login", "Sign_Up"])

    # Calculate DAU
    dau = df.groupby(df["Last_Login"].dt.date)["User_ID"].nunique().reset_index(name="DAU")
    dau["Login_Date"] = pd.to_datetime(dau["Last_Login"])

    # Calculate WAU
    df["Week"] = df["Last_Login"] - pd.to_timedelta(df["Last_Login"].dt.weekday, unit='d')
    wau = df.groupby("Week")["User_ID"].nunique().reset_index(name="WAU")

    # Calculate MAU
    df["Month"] = df["Last_Login"].dt.to_period("M").dt.to_timestamp()
    mau = df.groupby("Month")["User_ID"].nunique().reset_index(name="MAU")

    # Revenue trend
    revenue_trend = df.groupby("Month")["Revenue"].sum().reset_index()

    # Revenue by segment breakdown
    rev_segment = df.groupby("Tier")["Revenue"].sum().reset_index().sort_values(by="Revenue", ascending=False)
    rev_device = df.groupby("Device_Type")["Revenue"].sum().reset_index()
    rev_game = df.groupby("Game_Mode")["Revenue"].sum().reset_index()
    rev_user_segment = df.groupby("User_Segment")["Revenue"].sum().reset_index()

    # User lifespan in days
    df["Lifespan"] = (df["Last_Login"] - df["Sign_Up"]).dt.days

    # Clustering: Frequency vs Revenue
    clustering_data = df[["Lifespan", "Revenue"]].dropna()
    kmeans = KMeans(n_clusters=4, random_state=42).fit(clustering_data)
    clustering_data["Cluster"] = kmeans.labels_

    # Plot charts
    st.subheader("Active Users Overview")
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    axs[0].plot(dau["Login_Date"], dau["DAU"], marker='o', color="steelblue")
    axs[0].set_title("Daily Active Users (DAU)")
    axs[0].set_ylabel("Users")

    axs[1].plot(wau["Week"], wau["WAU"], marker='o', color="darkorange")
    axs[1].set_title("Weekly Active Users (WAU)")
    axs[1].set_ylabel("Users")

    axs[2].plot(mau["Month"], mau["MAU"], marker='o', color="seagreen")
    axs[2].set_title("Monthly Active Users (MAU)")
    axs[2].set_ylabel("Users")
    axs[2].set_xlabel("Date")

    axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    for ax in axs:
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Revenue Trends Over Time")
    fig_rev, ax_rev = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=revenue_trend, x="Month", y="Revenue", marker='o', ax=ax_rev, color="green")
    ax_rev.set_title("Monthly Revenue")
    ax_rev.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax_rev.tick_params(axis='x', rotation=45)
    st.pyplot(fig_rev)

    st.subheader("Revenue by Segment")
    col1, col2 = st.columns(2)
    with col1:
        st.write("By Tier")
        st.dataframe(rev_segment)
    with col2:
        st.write("By Device Type")
        st.dataframe(rev_device)

    col3, col4 = st.columns(2)
    with col3:
        st.write("By Game Mode")
        st.dataframe(rev_game)
    with col4:
        st.write("By User Segment")
        st.dataframe(rev_user_segment)

    st.subheader("User Clusters: Frequency vs Revenue")
    fig_clust, ax_clust = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=clustering_data, x="Lifespan", y="Revenue", hue="Cluster", palette="deep", ax=ax_clust)
    ax_clust.set_title("User Clustering")
    st.pyplot(fig_clust)

    st.subheader("Cohort Analysis: User Growth and Revenue Trends")
    df["Signup_Month"] = df["Sign_Up"].dt.to_period("M").dt.to_timestamp()
    cohort_data = df.groupby("Signup_Month").agg(
        User_Count=("User_ID", "count"),
        Avg_Revenue=("Revenue", "mean")
    ).reset_index()

    fig_cohort_mix, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(cohort_data["Signup_Month"], cohort_data["User_Count"], color='skyblue', label='User Count')
    ax1.set_ylabel("User Count", color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')

    ax2 = ax1.twinx()
    ax2.plot(cohort_data["Signup_Month"], cohort_data["Avg_Revenue"], color='orange', marker='o', label='Avg Revenue/User')
    ax2.set_ylabel("Avg Revenue/User (USD)", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    ax1.set_title("Cohort Analysis: User Growth and Revenue Trends")
    ax1.set_xlabel("Cohort Month")
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig_cohort_mix)

    st.subheader("Revenue Breakdown Visualizations")
    fig_all, axs_all = plt.subplots(3, 1, figsize=(10, 15))
    sns.barplot(data=rev_device, x="Device_Type", y="Revenue", ax=axs_all[0])
    axs_all[0].set_title("Revenue by Device Type")

    sns.barplot(data=rev_segment, x="Tier", y="Revenue", ax=axs_all[1], palette="pastel")
    axs_all[1].set_title("Revenue by Subscription Tier")

    sns.barplot(data=rev_game, x="Game_Mode", y="Revenue", ax=axs_all[2])
    axs_all[2].set_title("Revenue by Preferred Game Mode")
    axs_all[2].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    st.pyplot(fig_all)

    st.subheader("Revenue vs User Loyalty")
    bins = [0, 100, 300, 500, df["Lifespan"].max() + 1]
    labels = ['<100 days', '100–300 days', '300–500 days', '500+ days']
    df['Loyalty_Band'] = pd.cut(df['Lifespan'], bins=bins, labels=labels, right=False)

    avg_rev_band = df.groupby("Loyalty_Band")["Revenue"].mean().reset_index()
    fig_avg_band, ax_avg_band = plt.subplots(figsize=(10, 5))
    sns.barplot(data=avg_rev_band, x="Loyalty_Band", y="Revenue", ax=ax_avg_band)
    ax_avg_band.set_title("Average Revenue by User Loyalty Band")
    ax_avg_band.set_ylabel("Average Revenue (USD)")
    ax_avg_band.set_xlabel("Loyalty Band (Lifespan)")
    st.pyplot(fig_avg_band)

    total_rev_band = df.groupby("Loyalty_Band")["Revenue"].sum().reset_index()
    fig_total_band, ax_total_band = plt.subplots(figsize=(10, 5))
    sns.barplot(data=total_rev_band, x="Loyalty_Band", y="Revenue", ax=ax_total_band)
    ax_total_band.set_title("Total Revenue by User Loyalty Band")
    ax_total_band.set_ylabel("Total Revenue (USD)")
    ax_total_band.set_xlabel("Loyalty Band (Lifespan)")
    st.pyplot(fig_total_band)

    st.subheader("Early Churn Segments: User Count, Revenue Share, and Avg Revenue")
    df = df[df["Lifespan"] >= 0]  # Ensure lifespan is non-negative
    churn_labels = ['Same-Day', '≤ 7 Days', '≤ 30 Days']
    df['Churn_Group'] = pd.cut(df["Lifespan"], bins=[-1, 0, 7, 30], labels=churn_labels)

    total_users = df["User_ID"].nunique()
    total_revenue = df["Revenue"].sum()

    churn_data = df.groupby("Churn_Group").agg(
        User_Count=("User_ID", "count"),
        Avg_Revenue=("Revenue", "mean"),
        Total_Revenue=("Revenue", "sum")
    ).reset_index()

    churn_data["User_%"] = (churn_data["User_Count"] / total_users * 100).round(2)
    churn_data["Revenue_%"] = (churn_data["Total_Revenue"] / total_revenue * 100).round(2)

    fig_churn, ax1 = plt.subplots(figsize=(10, 6))
    bar = ax1.bar(churn_data["Churn_Group"], churn_data["User_%"], color='skyblue', label='User %')
    ax1.set_ylabel("User %", color='blue')
    ax1.set_xlabel("Churn Risk Group")
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    line = ax2.plot(churn_data["Churn_Group"], churn_data["Avg_Revenue"], color='red', marker='o', linewidth=2, label='Avg Revenue')
    ax2.set_ylabel("Average Revenue (USD)", color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    for i, rect in enumerate(bar):
        height = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2.0, height, f"{churn_data['Revenue_%'][i]}%", ha='center', va='bottom', fontsize=10, color='black')

    ax1.set_title("Early Churn Segments: User %, Revenue Share, and Avg Revenue")
    st.pyplot(fig_churn)

    st.subheader("High-Value vs High-Retention Users: Key Characteristics")
    top_value = df.sort_values(by="Revenue", ascending=False).head(1000)
    top_retention = df.sort_values(by="Lifespan", ascending=False).head(1000)

    fig_hr, axs_hr = plt.subplots(2, 3, figsize=(18, 10))
    bar_colors = {
        "High-Value": "skyblue",
        "High-Retention": "lightgreen"
    }

    sns.countplot(data=top_value, x="Tier", ax=axs_hr[0, 0], color=bar_colors["High-Value"])
    axs_hr[0, 0].set_title("High-Value: Subscription Tiers")

    sns.countplot(data=top_value, x="Device_Type", ax=axs_hr[0, 1], color=bar_colors["High-Value"])
    axs_hr[0, 1].set_title("High-Value: Devices")

    sns.countplot(data=top_value, x="Game_Mode", ax=axs_hr[0, 2], color=bar_colors["High-Value"])
    axs_hr[0, 2].set_title("High-Value: Game Modes")

    sns.countplot(data=top_retention, x="Tier", ax=axs_hr[1, 0], color=bar_colors["High-Retention"])
    axs_hr[1, 0].set_title("High-Retention: Subscription Tiers")

    sns.countplot(data=top_retention, x="Device_Type", ax=axs_hr[1, 1], color=bar_colors["High-Retention"])
    axs_hr[1, 1].set_title("High-Retention: Devices")

    sns.countplot(data=top_retention, x="Game_Mode", ax=axs_hr[1, 2], color=bar_colors["High-Retention"])
    axs_hr[1, 2].set_title("High-Retention: Game Modes")

    for ax in axs_hr.flat:
        ax.set_ylabel("User Count")
        ax.set_xlabel("")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.suptitle("High-Value vs High-Retention Users: Key Characteristics", fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig_hr)
else:
    st.info("Please upload a CSV file with columns including 'User ID', 'Last_Login', 'Sign_Up', 'Revenue', 'Tier', 'Device_Type', 'Game_Mode', 'User_Segment'")

