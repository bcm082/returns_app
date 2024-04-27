import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_resource
def load_data(year):
    # Load the total sold data
    total_sold_file = 'data/total_sold.csv'
    total_sold = pd.read_csv(total_sold_file)
    total_sold = total_sold[total_sold['Year'] == year]  # Filter by year
    total_sold['Total_Sold'] = pd.to_numeric(total_sold['Quantity'].str.replace(',', ''), errors='coerce')  # Ensure column is numeric

    # Load the returns data
    returns_file = 'data/returns.csv'
    returns_data = pd.read_csv(returns_file)
    returns_data = returns_data[returns_data['Year'] == year]  # Filter by year
    returns_data['Quantity_Returned'] = pd.to_numeric(returns_data['Quantity'], errors='coerce')  # Ensure column is numeric

    # Group by SKU and calculate total returns
    returns_aggregated = returns_data.groupby(['SKU']).agg({'Quantity_Returned': 'sum'}).reset_index()

    # Merge total sold with returns and calculate return percentages
    merged_data = pd.merge(total_sold[['SKU', 'Total_Sold']], returns_aggregated, on='SKU', how='left').fillna(0)
    merged_data['Percentage_Returns'] = (merged_data['Quantity_Returned'] / merged_data['Total_Sold']) * 100

    # Aggregate returns by reason and SKU
    top_reasons = returns_data.groupby(['Reason', 'SKU']).agg({'Quantity_Returned': 'sum'}).reset_index()
    top_reasons = top_reasons.sort_values(['Quantity_Returned'], ascending=False).reset_index(drop=True)

    return merged_data, top_reasons

def main():
    st.sidebar.title("Year Selection")
    year = st.sidebar.selectbox('Select Year', [2023, 2024])

    st.title('Customer Returns Dashboard')
    merged_data, top_reasons = load_data(year)  # Load data for selected year
    
    with st.expander("SKU Details"):
        if merged_data.empty:
            st.write("No data available for the selected year.")
        else:
            st.dataframe(merged_data, hide_index=True)
    
    with st.expander("Top Reasons for Returns"):
        st.dataframe(top_reasons, hide_index=True)

if __name__ == "__main__":
    main()
