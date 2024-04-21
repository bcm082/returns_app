import streamlit as st
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_resource
def load_data(folder_path):
    year = os.path.basename(folder_path)
    total_sold_file = os.path.join(folder_path, f"{year}-Total-Sold.csv")
    total_sold = pd.read_csv(total_sold_file)

# Load all monthly files except the total sold file
    monthly_files = [file for file in os.listdir(folder_path) if file.endswith('.csv') and 'Total-Sold' not in file]
    monthly_returns = []
    for file in monthly_files:
        df = pd.read_csv(os.path.join(folder_path, file))
        month_name = file.split('-')[0]  # Assuming file names are like 'January-2021.csv'
        if 'Month' not in df.columns:  # Add Month column if not exists
            df['Month'] = month_name
        monthly_returns.append(df)
    monthly_returns = pd.concat(monthly_returns, ignore_index=True)

    # Group by SKU, Reason, and Month, calculate total returns, find top reasons
    monthly_returns_aggregated = monthly_returns.groupby(['SKU', 'Reason', 'Month']).agg({'Quantity': 'sum'}).reset_index()
    top_reasons = monthly_returns_aggregated.loc[monthly_returns_aggregated.groupby(['SKU', 'Month'])['Quantity'].idxmax()].rename(columns={'Quantity': 'Quantity_Returned'})
    top_reasons = top_reasons.sort_values(['Month', 'Quantity_Returned'], ascending=[True, False]).reset_index(drop=True)

    # Merge total sold with returns and calculate return percentages
    merged_data = pd.merge(total_sold, monthly_returns_aggregated.groupby('SKU').agg({'Quantity': 'sum'}).reset_index(), on='SKU', how='left').fillna(0)
    merged_data.rename(columns={'Quantity_x': 'Total_Sold', 'Quantity_y': 'Total_Returned'}, inplace=True)
    merged_data['Percentage_Returns'] = (merged_data['Total_Returned'] / merged_data['Total_Sold']) * 100

    return merged_data, top_reasons, monthly_returns

@st.cache_resource
def load_yearly_data():
    all_data = {}
    monthly_data = {}  # New dictionary to store monthly data
    reasons_data = {}
    data_path = 'data'
    year_folders = [f for f in glob.glob(os.path.join(data_path, '*')) if os.path.isdir(f)]
    for year_folder in year_folders:
        year = os.path.basename(year_folder)
        merged_data, top_reasons, monthly_returns = load_data(year_folder)  # Adjust load_data to return monthly data too
        merged_data = merged_data.sort_values('Total_Returned', ascending=False).reset_index(drop=True)
        all_data[year] = merged_data
        monthly_data[year] = monthly_returns  # Store monthly data
        reasons_data[year] = top_reasons
    return all_data, monthly_data, reasons_data  # Return monthly data along with others


def plot_return_trends(data, year):
    if 'Month' in data.columns and 'Quantity' in data.columns:
        # Convert 'Month' to categorical and specify the order
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        data['Month'] = pd.Categorical(data['Month'], categories=month_order, ordered=True)

        # Group data by Month and sum up the returns
        monthly_returns = data.groupby('Month')['Quantity'].sum()
        print("Monthly returns:", monthly_returns)  # Debug: Print monthly returns to check if they are computed correctly

        if not monthly_returns.empty:
            fig, ax = plt.subplots(figsize=(12, 6))  # Adjusted for better fit of bars
            sns.barplot(x=monthly_returns.index, y=monthly_returns.values, ax=ax, color='skyblue')
            ax.set_title(f'Return Trends for {year}')
            ax.set_ylabel('Total Returns')
            ax.set_xlabel('Month')
            plt.xticks(rotation=45)  # Rotate month labels for better readability
            st.pyplot(fig)  # Pass the figure to streamlit for rendering using the local figure object
        else:
            st.write("No return data available for the selected year.")
    else:
        st.write("No monthly data available for plotting return trends.")


def plot_return_reasons(data, year):
    if 'Month' in data.columns:
        # Group by 'Reason' and 'Month', then sum 'Quantity_Returned'
        reasons = data.groupby(['Reason', 'Month'])['Quantity_Returned'].sum().sort_values(ascending=False)
        # Sum up all months for each reason and select the top 10 reasons
        reasons = reasons.groupby(level=0).sum().nlargest(10)
        
        # Plotting the top 10 reasons
        plt.figure(figsize=(10, 8))
        plt.pie(reasons, labels=reasons.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired(range(len(reasons))))
        plt.title(f'Top 10 Return Reasons for {year}')
        plt.tight_layout()
        st.pyplot()
    else:
        st.write("No monthly data available for plotting return reasons.")

def main():
    st.sidebar.title("Navigation")
    all_data, monthly_data, reasons_data = load_yearly_data()  # Adjust to receive monthly data
    year = st.sidebar.selectbox('Select Year', sorted(all_data.keys(), reverse=True))
    
    st.title('Customer Returns Dashboard')
    
    with st.expander(f"SKU Details for {year}"):
        st.dataframe(all_data[year], hide_index=True)
    
    with st.expander(f"Top Reasons for Returns in {year}"):
        st.dataframe(reasons_data[year], hide_index=True)

    with st.expander("Analysis"):
        plot_return_trends(monthly_data[year], year)  # Pass the correct monthly data
        plot_return_reasons(reasons_data[year], year)

if __name__ == "__main__":
    main()

