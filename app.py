import streamlit as st
import pandas as pd
import os
import glob

@st.cache_resource
def load_data(folder_path):
    year = os.path.basename(folder_path)
    total_sold_file = os.path.join(folder_path, f"{year}-Total-Sold.csv")
    total_sold = pd.read_csv(total_sold_file)

    # Load all monthly files except the total sold file
    monthly_files = [file for file in os.listdir(folder_path) if file.endswith('.csv') and 'Total-Sold' not in file]
    monthly_returns = pd.concat([pd.read_csv(os.path.join(folder_path, file)) for file in monthly_files], ignore_index=True)

    # Group by SKU and Reason, calculate total returns, find top reasons
    monthly_returns_aggregated = monthly_returns.groupby(['SKU', 'Reason']).agg({'Quantity': 'sum'}).reset_index()
    top_reasons = monthly_returns_aggregated.loc[monthly_returns_aggregated.groupby('SKU')['Quantity'].idxmax()].rename(columns={'Quantity': 'Quantity_Returned'})
    top_reasons = top_reasons.sort_values('Quantity_Returned', ascending=False).reset_index(drop=True)

    # Merge total sold with returns and calculate return percentages
    merged_data = pd.merge(total_sold, monthly_returns_aggregated.groupby('SKU').agg({'Quantity': 'sum'}).reset_index(), on='SKU', how='left').fillna(0)
    merged_data.rename(columns={'Quantity_x': 'Total_Sold', 'Quantity_y': 'Total_Returned'}, inplace=True)
    merged_data['Percentage_Returns'] = (merged_data['Total_Returned'] / merged_data['Total_Sold']) * 100

    return merged_data, top_reasons

@st.cache_resource
def load_yearly_data():
    all_data = {}
    reasons_data = {}
    data_path = 'data'
    year_folders = [f for f in glob.glob(os.path.join(data_path, '*')) if os.path.isdir(f)]
    for year_folder in year_folders:
        year = os.path.basename(year_folder)
        merged_data, top_reasons = load_data(year_folder)
        merged_data = merged_data.sort_values('Total_Returned', ascending=False).reset_index(drop=True)
        all_data[year] = merged_data
        reasons_data[year] = top_reasons
    return all_data, reasons_data

def main():
    st.sidebar.title("Navigation")
    all_data, reasons_data = load_yearly_data()
    year = st.sidebar.selectbox('Select Year', sorted(all_data.keys(), reverse=True))
    
    st.title('Customer Returns Dashboard')
    
    with st.expander(f"SKU Details for {year}"):
        st.dataframe(all_data[year], hide_index=True)
    
    with st.expander(f"Top Reasons for Returns in {year}"):
        st.dataframe(reasons_data[year], hide_index=True)

    with st.expander("Analysis"):
        # Placeholder for future visualizations
        st.write("Visualizations will be added here.")

if __name__ == "__main__":
    main()
