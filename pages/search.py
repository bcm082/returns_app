import streamlit as st
import pandas as pd

# Load the CSV files
returns = pd.read_csv('data/returns.csv')
total_sold = pd.read_csv('data/total_sold.csv')

# Streamlit page setup
st.title("SKU Search Tool")
search_query = st.text_input("Enter SKU for search:", "")

# Function to search SKU across dataframes
def search_sku(data, query):
    # Normalize the query to avoid case sensitivity issues
    query = query.lower().strip()
    # Filter data if query in SKU
    mask = data['SKU'].str.lower().str.contains(query)
    return data[mask]

# Search and display results
if search_query:
    filtered_returns = search_sku(returns, search_query)
    filtered_total_sold = search_sku(total_sold, search_query)
    
    st.write("### Returns Data")
    st.dataframe(filtered_returns)
    
    st.write("### Total Sold Data")
    st.dataframe(filtered_total_sold)
