import streamlit as st
import pandas as pd

# Load the CSV files
returns = pd.read_csv('data/returns.csv')
total_sold = pd.read_csv('data/total_sold.csv')

# Convert 'Quantity' columns to numeric
returns['Quantity'] = pd.to_numeric(returns['Quantity'], errors='coerce')
total_sold['Quantity'] = pd.to_numeric(total_sold['Quantity'].str.replace(',', ''), errors='coerce')

# Assuming the Year column exists or extracting it if necessary
if 'Year' not in returns.columns:
    returns['Year'] = pd.to_datetime(returns['Date']).dt.year.astype(int)
if 'Year' not in total_sold.columns:
    total_sold['Year'] = pd.to_datetime(total_sold['Date']).dt.year.astype(int)

# Streamlit page setup
st.title("SKU Search Tool")
search_query = st.text_input("Enter SKU for search:", "")

def search_sku(data, query, year):
    query = query.lower().strip()
    filtered_data = data[(data['SKU'].str.lower().str.contains(query)) & (data['Year'] == year)]
    return filtered_data.groupby('SKU')['Quantity'].sum().reset_index()

def compute_results(year):
    filtered_returns = search_sku(returns, search_query, year)
    filtered_total_sold = search_sku(total_sold, search_query, year)
    
    if not filtered_returns.empty and not filtered_total_sold.empty:
        merged_data = pd.merge(filtered_total_sold, filtered_returns, on='SKU', suffixes=('_sold', '_returned'))
        merged_data['Return Percentage'] = (merged_data['Quantity_returned'] / merged_data['Quantity_sold']) * 100
        return merged_data[['SKU', 'Quantity_sold', 'Quantity_returned', 'Return Percentage']]
    else:
        return pd.DataFrame(columns=['SKU', 'Quantity_sold', 'Quantity_returned', 'Return Percentage'])

def top_reasons(year):
    filtered_data = returns[(returns['SKU'].str.lower().str.contains(search_query.lower())) & (returns['Year'] == year)]
    if not filtered_data.empty:
        reasons_data = filtered_data.groupby('Reason')['Quantity'].sum().reset_index()
        reasons_data = reasons_data.sort_values(by='Quantity', ascending=False).head(5)
        return reasons_data
    else:
        return pd.DataFrame(columns=['Reason', 'Quantity'])

# Search and display results
if search_query:
    results_2023 = compute_results(2023)
    results_2024 = compute_results(2024)
    reasons_2023 = top_reasons(2023)
    reasons_2024 = top_reasons(2024)

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

