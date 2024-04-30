import streamlit as st
import pandas as pd
import plotly.express as px

# Load the CSV files
returns = pd.read_csv('data/returns.csv')
total_sold = pd.read_csv('data/total_sold.csv')

# Convert 'Quantity' columns to numeric
returns['Quantity'] = pd.to_numeric(returns['Quantity'], errors='coerce')
total_sold['Quantity'] = pd.to_numeric(total_sold['Quantity'].str.replace(',', ''), errors='coerce')

# Streamlit page setup
st.title("SKU Search Tool")
search_query = st.text_input("Enter SKU for search:", "")

def search_sku(data, query, year):
    query = query.lower().strip()
    filtered_data = data[(data['SKU'].str.lower().str.contains(query)) & (data['Year'] == year)]
    return filtered_data

def compute_results(year):
    filtered_returns = search_sku(returns, search_query, year)
    filtered_total_sold = search_sku(total_sold, search_query, year)
    
    if not filtered_returns.empty and not filtered_total_sold.empty:
        total_sold_agg = filtered_total_sold.groupby('SKU', as_index=False)['Quantity'].sum()
        total_returned_agg = filtered_returns.groupby('SKU', as_index=False)['Quantity'].sum()
        merged_data = pd.merge(total_sold_agg, total_returned_agg, on='SKU', suffixes=('_sold', '_returned'))
        merged_data['Return Percentage'] = (merged_data['Quantity_returned'] / merged_data['Quantity_sold']) * 100
        return merged_data[['SKU', 'Quantity_sold', 'Quantity_returned', 'Return Percentage']]
    else:
        return pd.DataFrame(columns=['SKU', 'Quantity_sold', 'Quantity_returned', 'Return Percentage'])

def top_reasons(year):
    filtered_data = search_sku(returns, search_query, year)
    if not filtered_data.empty:
        reasons_data = filtered_data.groupby('Reason', as_index=False)['Quantity'].sum()
        reasons_data = reasons_data.sort_values(by='Quantity', ascending=False).head(5)
        return reasons_data
    else:
        return pd.DataFrame(columns=['Reason', 'Quantity'])

def monthly_returns(year):
    filtered_returns = search_sku(returns, search_query, year)
    if not filtered_returns.empty and 'Month' in filtered_returns.columns:
        monthly_data = filtered_returns.groupby('Month', as_index=False)['Quantity'].sum()
        monthly_data['Year'] = year  # Add year for distinguishing in the plot
        return monthly_data
    else:
        return pd.DataFrame(columns=['Month', 'Quantity', 'Year'])

# Define month order
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Ensure all months are represented for each year
def fill_missing_months(data, year):
    all_months = pd.DataFrame(month_order, columns=['Month'])
    all_months['Year'] = year
    data = pd.merge(all_months, data, on=['Month', 'Year'], how='left').fillna({'Quantity': 0})
    return data

# Search and display results
if search_query:
    results_2023 = compute_results(2023)
    results_2024 = compute_results(2024)
    reasons_2023 = top_reasons(2023)
    reasons_2024 = top_reasons(2024)
    monthly_returns_2023 = fill_missing_months(monthly_returns(2023), 2023)
    monthly_returns_2024 = fill_missing_months(monthly_returns(2024), 2024)
    
    # Combine 2023 and 2024 data for plotting
    combined_returns = pd.concat([monthly_returns_2023, monthly_returns_2024])
    combined_returns['Month'] = pd.Categorical(combined_returns['Month'], categories=month_order, ordered=True)
    combined_returns.sort_values(['Year', 'Month'], inplace=True)

    with st.expander("Monthly Returns Comparison Year over Year", expanded=True):
        if not combined_returns.empty:
            fig = px.line(combined_returns, x='Month', y='Quantity', color='Year', markers=True, title="Monthly Returns Comparison: 2023 vs 2024")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("### No monthly returns data available for comparison.")

    # Additional expander sections can be added here as per the previous setup.

    with st.expander("2024 Data", expanded=True):
        if not results_2024.empty:
            st.write("### 2024 Sales and Returns Data")
            st.dataframe(results_2024, hide_index=True)
        else:
            st.write("### No sales and returns data found for 2024.")

        if not reasons_2024.empty:
            st.write("### Top 5 Reasons for Returns in 2024")
            st.dataframe(reasons_2024, hide_index=True)
        else:
            st.write("### No returns data found for 2024.")

        if not monthly_returns_2024.empty:
            st.write("### Monthly Returns in 2024")
            st.dataframe(monthly_returns_2024, hide_index=True)
        else:
            st.write("### No monthly returns data found for 2024.")

    with st.expander("2023 Data", expanded=True):
        if not results_2023.empty:
            st.write("### 2023 Sales and Returns Data")
            st.dataframe(results_2023, hide_index=True)
        else:
            st.write("### No sales and returns data found for 2023.")
        
        if not reasons_2023.empty:
            st.write("### Top 5 Reasons for Returns in 2023")
            st.dataframe(reasons_2023, hide_index=True)
        else:
            st.write("### No returns data found for 2023.")

        if not monthly_returns_2023.empty:
            st.write("### Monthly Returns in 2023")
            st.dataframe(monthly_returns_2023, hide_index=True)
        else:
            st.write("### No monthly returns data found for 2023.")

