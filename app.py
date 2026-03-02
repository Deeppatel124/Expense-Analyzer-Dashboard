import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

#  Page Config
st.set_page_config(
    page_title="Expense Analyzer",
    layout="wide"
)

#  Load & Preprocess Data

try:
    df = pd.read_csv("dataset.csv")
except FileNotFoundError:
    st.error("dataset.csv not found. Please make sure the file is in the same folder.")
    st.stop()
except Exception as e:
    st.error(f"Something went wrong while loading the data: {e}")
    st.stop()


df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.month_name()
df["Category"] = df["Category"].replace("Medical", "Health")

st.sidebar.markdown("---")
st.sidebar.subheader("Filter by Date")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]

#  Feature Functions

def category_wise_spending():
    result = df.groupby("Category")["Amount"].sum().reset_index().sort_values("Amount",ascending=False)
    result.columns = ["Category", "Total Amount"]

    total = pd.DataFrame([["TOTAL", result["Total Amount"].sum()]], columns=result.columns)
    result = pd.concat([result, total], ignore_index=True)
    result.index = list(range(1, len(result))) + [""]

    st.dataframe(result, use_container_width=True)

    chart_data = result[result["Category"] != "TOTAL"].sort_values("Total Amount", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(chart_data["Category"], chart_data["Total Amount"], color="#4C72B0")
    ax.set_title("Category-Wise Total Spending")
    ax.set_xlabel("Amount")
    ax.set_ylabel("Category")
    plt.tight_layout()
    st.pyplot(fig)


def monthly_total_spending():
    month_order = df.sort_values("Date")["Month"].unique()
    result = df.groupby("Month")["Amount"].sum().reindex(month_order).reset_index()
    result.columns = ["Month", "Total Amount"]

    total = pd.DataFrame([["TOTAL", result["Total Amount"].sum()]], columns=result.columns)
    result = pd.concat([result, total], ignore_index=True)
    result.index = list(range(1, len(result))) + [""]

    st.dataframe(result, use_container_width=True)

    chart_data = result[result["Month"] != "TOTAL"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(chart_data["Month"], chart_data["Total Amount"], color=["#4C72B0", "#DD8452", "#55A868"])
    ax.set_title("Monthly Total Spending")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    plt.tight_layout()
    st.pyplot(fig)


def payment_method_summary():
    result = df.groupby("Payment_Method")["Amount"].sum().reset_index().sort_values(by="Payment_Method", ascending=False)
    result.columns = ["Payment Method", "Total Amount"]
    total = df["Amount"].sum()
    result["Percentage"] = ((result["Total Amount"] / total) * 100).map("{:.2f}%".format)

    total_row = pd.DataFrame([["TOTAL", total, "100%"]], columns=result.columns)
    result = pd.concat([result, total_row], ignore_index=True)
    result.index = list(range(1, len(result))) + [""]

    st.dataframe(result, use_container_width=True)

    chart_data = result[result["Payment Method"] != "TOTAL"]

    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(
        chart_data["Total Amount"],
        labels=chart_data["Payment Method"].values,
        colors = plt.cm.Set2.colors[:len(chart_data)],
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Payment Method Summary")
    plt.tight_layout()
    st.pyplot(fig)


def most_expensive_day():
    result = df.groupby("Date")["Amount"].sum().reset_index()
    result.columns = ["Date", "Total Amount"]
    result = result.sort_values("Total Amount", ascending=False).reset_index(drop=True)
    result.index = result.index + 1

    st.subheader("Top 5 Most Expensive Days")
    st.dataframe(result.head(), use_container_width=True)


def budget_tracker(budget):
    result = df.groupby("Category")["Amount"].sum().reset_index()
    result.columns = ["Category", "Total Spent"]
    result["Budget"] = result["Category"].map(budget)
    result["Remaining"] = result["Budget"] - result["Total Spent"]
    result["Status"] = result["Remaining"].apply(
        lambda x: "Under Budget" if x >= 0 else "Over Budget"
    )
    result.index = list(range(1, len(result) + 1))
    st.dataframe(result, use_container_width=True)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        result["Total Spent"],
        labels=result["Category"],
        autopct="%1.1f%%",
        startangle=140
    )
    ax.set_title("Budget Distribution by Category")
    plt.tight_layout()
    st.pyplot(fig)


def search_by_keyword(keyword):
    result = df[df["Notes"].str.contains(keyword, case=False, na=False)]
    result = result[["Date", "Category", "Amount", "Payment_Method", "Notes"]].reset_index(drop=True)
    result.index = result.index + 1
    result.index.name = "No."

    if len(result) == 0:
        st.warning(f"No transactions found for keyword: **'{keyword}'**")
    else:
        st.success(f"Found **{len(result)}** transaction(s) for keyword: **'{keyword}'**")
        st.dataframe(result, use_container_width=True)


#  Sidebar Menu

st.sidebar.title("Expense Analyzer")
st.sidebar.markdown("---")

feature = st.sidebar.selectbox(
    "Select a Feature",
    [
        "Home",
        "1. Category-wise Total Spending",
        "2. Monthly Total Spending",
        "3. Payment Method Summary",
        "4. Most Expensive Day",
        "5. Budget Tracker",
        "6. Search by Keyword"
    ]
)

#  Main Area

st.title("Expense Analyzer & Budget Tracker")
st.markdown("---")

if feature == "Home":
    st.header("Welcome!")
    st.write("Use the sidebar on the left to select any feature and analyze your expenses.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spending", f"₹{df['Amount'].sum():,.0f}")
    col2.metric("Top Category", df.groupby("Category")["Amount"].sum().idxmax())
    col3.metric("Total Transactions", len(df))

    st.markdown("---")
    st.subheader("Raw Dataset")
    st.dataframe(df, use_container_width=True)

elif feature == "1. Category-wise Total Spending":
    st.header("Category-wise Total Spending")
    category_wise_spending()

elif feature == "2. Monthly Total Spending":
    st.header("Monthly Total Spending")
    monthly_total_spending()

elif feature == "3. Payment Method Summary":
    st.header("Payment Method Summary")
    payment_method_summary()

elif feature == "4. Most Expensive Day":
    st.header("Most Expensive Day")
    most_expensive_day()

elif feature == "5. Budget Tracker":
    st.header("Budget Tracker")

    st.subheader("Set Your Budgets")
    categories = df["Category"].unique()
    budget = {}

    cols = st.columns(2)
    for i, cat in enumerate(categories):
        with cols[i % 2]:
            budget[cat] = st.number_input(
                f"Budget for {cat}",
                min_value=0,
                value=1000,
                step=100,
                key=cat
            )

    budget_tracker(budget)

elif feature == "6. Search by Keyword":
    st.header("Search by Keyword")
    keyword = st.text_input("Enter keyword to search in Notes:")
    if keyword:
        search_by_keyword(keyword)