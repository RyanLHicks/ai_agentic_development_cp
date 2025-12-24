
import streamlit as st
import pandas as pd
import sqlalchemy
import os
import altair as alt
import io

# --- Configuration --- #
BASE_DIR = r"C:\Users\ryano\My Drive\Be Bob\Ai projects\Code Puppy\retail-pulse-dashboard\src"
DATABASE_PATH = os.path.join(BASE_DIR, "retail.db")

# --- Database Connection --- #
@st.cache_resource
def get_db_connection():
    """
    Establishes and caches a SQLAlchemy engine connection to the SQLite database.
    The connection is cached to prevent re-initializing it on every rerun of the script.
    """
    print(f"Attempting to connect to database: {DATABASE_PATH}") # For debugging
    engine = sqlalchemy.create_engine(f"sqlite:///{DATABASE_PATH}", connect_args={"check_same_thread": False})
    try:
        # Test connection
        with engine.connect() as connection:
            connection.execute(sqlalchemy.text("SELECT 1")).fetchall()
        print("Database connection successful.")
    except Exception as e:
        st.error(f"Failed to connect to the database: {e}")
        print(f"Database connection failed: {e}") # For debugging
        st.stop()
    return engine

engine = get_db_connection()

# --- SQL Queries --- #
# Zero Sales Alert query (reused from etl_pipeline.py)
ZERO_SALES_ALERT_QUERY = """
SELECT
    dsp.store_id,
    dsp.product_id,
    MAX(dsp.current_stock_on_hand) AS units_on_hand_latest
FROM
    daily_store_performance AS dsp
WHERE
    dsp.date >= DATE('now', '-7 days')
GROUP BY
    dsp.store_id, dsp.product_id
HAVING
    SUM(dsp.total_quantity_sold) = 0
    AND MAX(dsp.current_stock_on_hand) > 10
ORDER BY
    dsp.store_id, dsp.product_id;
"""

# Query for Total Units Sold over last 60 days
TOTAL_UNITS_SOLD_LAST_60_DAYS_QUERY = """
SELECT
    date,
    SUM(total_quantity_sold) AS total_units_sold
FROM
    daily_store_performance
WHERE
    date >= DATE('now', '-60 days')
GROUP BY
    date
ORDER BY
    date;
"""

# Query for Top 5 Stores by Revenue
TOP_5_STORES_BY_REVENUE_QUERY = """
SELECT
    store_id,
    SUM(total_revenue) AS total_revenue
FROM
    daily_store_performance
GROUP BY
    store_id
ORDER BY
    total_revenue DESC
LIMIT 5;
"""

# --- Dashboard Pages --- #
def executive_overview_page():
    st.title("Executive Overview")

    st.header("Total Units Sold per Day (Last 60 Days)")
    try:
        df_units_sold = pd.read_sql(TOTAL_UNITS_SOLD_LAST_60_DAYS_QUERY, engine)
        df_units_sold['date'] = pd.to_datetime(df_units_sold['date'])
        if not df_units_sold.empty:
            chart = alt.Chart(df_units_sold).mark_line().encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('total_units_sold:Q', title='Total Units Sold')
            ).properties(
                title='Total Units Sold per Day'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No units sold data available for the last 60 days.")
    except Exception as e:
        st.error(f"Error loading total units sold data: {e}")

    st.header("Top 5 Stores by Revenue")
    try:
        df_top_stores = pd.read_sql(TOP_5_STORES_BY_REVENUE_QUERY, engine)
        if not df_top_stores.empty:
            chart = alt.Chart(df_top_stores).mark_bar().encode(
                x=alt.X('store_id:N', title='Store ID', sort='-y'),
                y=alt.Y('total_revenue:Q', title='Total Revenue')
            ).properties(
                title='Top 5 Stores by Revenue'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No revenue data available to determine top stores.")
    except Exception as e:
        st.error(f"Error loading top stores by revenue data: {e}")

def risk_alerts_page():
    st.title("Risk Alerts (The Analyst Tool)")

    st.header("Zero Sales Alert: Products with Inventory > 10 and 0 Sales in Last 7 Days")
    try:
        df_zero_sales = pd.read_sql(ZERO_SALES_ALERT_QUERY, engine)
        if not df_zero_sales.empty:
            st.dataframe(df_zero_sales, use_container_width=True)

            # Export to Excel button
            excel_buffer = io.BytesIO()
            df_zero_sales.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            st.download_button(
                label="Export to Excel",
                data=excel_buffer,
                file_name="zero_sales_alert.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No products found matching the zero sales alert criteria.")
    except Exception as e:
        st.error(f"Error loading zero sales alerts: {e}")

def scenario_planner_page():
    st.title("Scenario Planner")
    st.markdown("Use the sliders below to simulate the impact of promotions on revenue.")

    # Input Widgets
    st.sidebar.header("What-If Scenario Inputs")
    discount_pct = st.sidebar.slider(
        "Proposed Price Discount (%)",
        min_value=0, max_value=50, value=10, step=1,
        format="%d%%", help="Percentage reduction in average price."
    )
    uplift_pct = st.sidebar.slider(
        "Expected Sales Uplift (%)",
        min_value=0, max_value=200, value=20, step=5,
        format="%d%%", help="Percentage increase in units sold."
    )

    # Convert percentages to decimals
    discount_factor = discount_pct / 100.0
    uplift_factor = uplift_pct / 100.0

    # Fetch baseline data (last 30 days)
    st.subheader("Baseline Data (Last 30 Days)")
    baseline_query = """
    SELECT
        SUM(total_revenue) AS current_revenue,
        SUM(total_quantity_sold) AS current_volume
    FROM
        daily_store_performance
    WHERE
        date >= DATE('now', '-30 days');
    """
    try:
        df_baseline = pd.read_sql(baseline_query, engine)
        current_revenue = df_baseline['current_revenue'].iloc[0] if not df_baseline.empty and not pd.isna(df_baseline['current_revenue'].iloc[0]) else 0.0
        current_volume = df_baseline['current_volume'].iloc[0] if not df_baseline.empty and not pd.isna(df_baseline['current_volume'].iloc[0]) else 0.0

        if current_volume > 0:
            avg_price = current_revenue / current_volume
        else:
            avg_price = 0

        st.write(f"Current Revenue (last 30 days): **${current_revenue:,.2f}**")
        st.write(f"Current Volume (last 30 days): **{current_volume:,.0f} units**")
        st.write(f"Average Price (last 30 days): **${avg_price:,.2f}**")

        # --- What-If Logic ---
        # New_Price = Avg_Price * (1 - Discount)
        # New_Volume = Current_Volume * (1 + Uplift)
        # Projected_Revenue = New_Price * New_Volume
        new_price = avg_price * (1 - discount_factor)
        new_volume = current_volume * (1 + uplift_factor)
        projected_revenue = new_price * new_volume
        net_impact = projected_revenue - current_revenue

        st.subheader("Projected Scenario")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Revenue", f"${current_revenue:,.2f}")
        with col2:
            st.metric("Projected Revenue", f"${projected_revenue:,.2f}")
        with col3:
            delta_color = "inverse" if net_impact < 0 else "normal"
            st.metric("Net Impact", f"${net_impact:,.2f}", delta=f"{net_impact:,.2f}", delta_color=delta_color)

        # Visuals: Bar chart comparing 'Baseline' vs 'Scenario'
        chart_data = pd.DataFrame({
            'Category': ['Baseline Revenue', 'Projected Revenue'],
            'Revenue': [current_revenue, projected_revenue]
        })

        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Category:N', title=''),
            y=alt.Y('Revenue:Q', title='Revenue'),
            color=alt.condition(
                alt.datum.Category == 'Baseline Revenue',
                alt.value('steelblue'),  # Baseline color
                alt.value('orange') # Projected color
            )
        ).properties(title='Revenue Comparison: Baseline vs. Scenario')

        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"Error calculating scenario: {e}")

# --- Main App Logic --- #
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Executive Overview", "Risk Alerts", "Scenario Planner"])

if selection == "Executive Overview":
    executive_overview_page()
elif selection == "Risk Alerts":
    risk_alerts_page()
elif selection == "Scenario Planner":
    scenario_planner_page()
