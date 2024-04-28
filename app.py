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

    # Load returns data for comparison across all years
    all_returns_data = pd.read_csv(returns_file)
    all_returns_data['Quantity_Returned'] = pd.to_numeric(all_returns_data['Quantity'], errors='coerce')  # Ensure column is numeric

    # Construct a pivot table with the correct months
    all_returns_data['Month'] = pd.Categorical(all_returns_data['Month'], categories=[
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'], ordered=True)
    returns_comparison_data = all_returns_data.pivot_table(values='Quantity_Returned', index='Month', columns='Year', aggfunc='sum').fillna(0)

    return merged_data, top_reasons, returns_comparison_data


def plot_comparison_graphs(data, year):
    if year in data.columns:
        current_year_data = data[year]
        previous_year = year - 1
        previous_year_data = data.get(previous_year, pd.Series())

        # Define month labels as they appear in the DataFrame
        month_labels = ['January', 'February', 'March', 'April', 'May', 'June', 
                        'July', 'August', 'September', 'October', 'November', 'December']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        # Plot current year data
        current_year_data.plot(kind='bar', ax=ax, color='b', position=0, width=0.4, label=f'Returns {year}')
        # Plot previous year data if it exists
        if not previous_year_data.empty:
            previous_year_data.plot(kind='bar', ax=ax, color='r', position=1, width=0.4, label=f'Returns {previous_year}')

        ax.set_title('Month-over-Month Returns Comparison')
        ax.set_xlabel('Month')
        ax.set_ylabel('Quantity Returned')
        ax.set_xticklabels(month_labels, rotation=45)  # Rotate labels for better visibility
        ax.legend()
        st.pyplot(fig)
    else:
        st.write(f"No return data available for the year {year}.")




def main():
    st.sidebar.title("Year Selection")
    year = st.sidebar.selectbox('Select Year', [2023, 2024])

    st.title('Customer Returns Dashboard')
    merged_data, top_reasons, returns_comparison_data = load_data(year)  # Load data for selected year
    
    with st.expander("SKU Details"):
        if merged_data.empty:
            st.write("No data available for the selected year.")
        else:
            st.dataframe(merged_data)
    
    with st.expander("Top Reasons for Returns"):
        st.dataframe(top_reasons)

    with st.expander("Returns Comparison"):
        plot_comparison_graphs(returns_comparison_data, year)

if __name__ == "__main__":
    main()
