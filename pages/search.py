import streamlit as st
import pandas as pd

# Load the CSV files
returns = pd.read_csv('data/returns.csv')
total_sold = pd.read_csv('data/total_sold.csv')

# Convert 'Quantity' columns to numeric
returns['Quantity'] = pd.to_numeric(returns['Quantity'], errors='coerce')  # This might already be correct.
total_sold['Quantity'] = pd.to_numeric(total_sold['Quantity'].str.replace(',', ''), errors='coerce')  # Removing commas and converting to numeric.

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
        # Merge data on SKU
        merged_data = pd.merge(filtered_total_sold, filtered_returns, on='SKU', suffixes=('_sold', '_returned'))
        merged_data['Return Percentage'] = (merged_data['Quantity_returned'] / merged_data['Quantity_sold']) * 100
        return merged_data[['SKU', 'Quantity_sold', 'Quantity_returned', 'Return Percentage']]
    else:
        # Handle cases where no matching data is found
        return pd.DataFrame(columns=['SKU', 'Quantity_sold', 'Quantity_returned', 'Return Percentage'])

# Search and display results
if search_query:
    results_2023 = compute_results(2023)
    results_2024 = compute_results(2024)
    
    if not results_2023.empty:
        st.write("### 2023 Data")
        st.dataframe(results_2023, hide_index=True)
    else:
        st.write("### No data found for 2023.")

    if not results_2024.empty:
        st.write("### 2024 Data")
        st.dataframe(results_2024, hide_index=True)
    else:
        st.write("### No data found for 2024.")
