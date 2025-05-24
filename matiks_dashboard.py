import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Matiks - Data Analyst Data - Sheet1.csv")
    df.columns = df.columns.str.replace(" ", "_").str.strip()
    st.write("📋 Columns in your CSV:", df.columns.tolist())

    # Parse date columns safely
    if "Signup_Date" in df.columns and "Last_Login" in df.columns:
        df["Signup_Date"] = pd.to_datetime(df["Signup_Date"])
        df["Last_Login"] = pd.to_datetime(df["Last_Login"])

        df["Days_Since_Last_Login"] = (df["Last_Login"].max() - df["Last_Login"]).dt.days
        df["Days_Active"] = (df["Last_Login"] - df["Signup_Date"]).dt.days.replace(0, 1)
    else:
        st.error("❌ Missing 'Signup_Date' or 'Last_Login' columns in CSV.")
        df["Days_Since_Last_Login"] = 0
        df["Days_Active"] = 1

    # Derived metrics
    df["Sessions_Per_Day"] = df["Total_Play_Sessions"] / df["Days_Active"]
    df["High_Value_User"] = df["Total_Revenue_USD"] >= df["Total_Revenue_USD"].quantile(0.9)
    df["Churn_Risk"] = (df["Total_Play_Sessions"] < 5) | (df["Days_Since_Last_Login"] > 14) | (df["Avg_Session_Duration_Min"] < 5)

    return df

df = load_data()

st.title("📊 Matiks Analytics Dashboard")

st.sidebar.header("Filters")
device_filter = st.sidebar.multiselect("Select Device Type:", df["Device_Type"].unique(), default=list(df["Device_Type"].unique()))
segment_filter = st.sidebar.multiselect("Select Subscription Tier:", df["Subscription_Tier"].unique(), default=list(df["Subscription_Tier"].unique()))

filtered_df = df[df["Device_Type"].isin(device_filter) & df["Subscription_Tier"].isin(segment_filter)]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Users", len(filtered_df))
col2.metric("Revenue ($)", f"{filtered_df['Total_Revenue_USD'].sum():,.2f}")
col3.metric("Churn Risk Users", filtered_df["Churn_Risk"].sum())

# Daily/Weekly/Monthly Active Users
st.subheader("📈 DAU / WAU / MAU (Simulated)")
date_range = pd.date_range(start=filtered_df["Signup_Date"].min(), end=filtered_df["Last_Login"].max())
dau = pd.Series([filtered_df.sample(frac=0.2).shape[0] for _ in date_range], index=date_range)
wau = dau.rolling(window=7).mean()
mau = dau.rolling(window=30).mean()

fig, ax = plt.subplots()
ax.plot(dau.index, dau, label="DAU")
ax.plot(wau.index, wau, label="WAU")
ax.plot(mau.index, mau, label="MAU")
ax.set_title("User Activity Over Time")
ax.legend()
st.pyplot(fig)

# Revenue Trend
st.subheader("💰 Revenue Trend")
rev_trend = filtered_df.groupby(filtered_df["Last_Login"].dt.to_period("M")).sum(numeric_only=True)["Total_Revenue_USD"]
fig2, ax2 = plt.subplots()
rev_trend.plot(kind="bar", ax=ax2, color="green")
ax2.set_title("Monthly Revenue")
ax2.set_ylabel("USD")
st.pyplot(fig2)

# Churn Segments Pie Chart
st.subheader("📉 Churn Segments")
def churn_reason(row):
    if row["Total_Play_Sessions"] < 5:
        return "Low Sessions (<5)"
    elif row["Days_Since_Last_Login"] > 14:
        return "Inactive >14 Days"
    elif row["Avg_Session_Duration_Min"] < 5:
        return "Short Sessions (<5 min)"
    return "Engaged"

filtered_df["Churn_Category"] = filtered_df.apply(churn_reason, axis=1)
churn_counts = filtered_df["Churn_Category"].value_counts()
fig3, ax3 = plt.subplots()
churn_counts.plot(kind="pie", autopct="%1.1f%%", startangle=90, ax=ax3)
ax3.set_ylabel("")
ax3.set_title("Churn Category Breakdown")
st.pyplot(fig3)

# High-Value Users
st.subheader("🏆 High-Value Users Breakdown")
hv_counts = filtered_df["High_Value_User"].value_counts().rename({True: "High Value", False: "Others"})
fig4, ax4 = plt.subplots()
hv_counts.plot(kind="bar", color=["gold", "gray"], ax=ax4)
ax4.set_title("High-Value Users vs Others")
ax4.set_ylabel("User Count")
st.pyplot(fig4)

st.markdown("---")
st.caption("Matiks Analyst Task | Built with Streamlit")
