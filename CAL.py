import pandas as pd
import streamlit as st

# Function to load the file
def Load_File(uploaded_file):
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            print("Data loaded from file:\n", df)  # Debugging line
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return None
    else:
        st.error("No file uploaded!")
        return None

# Capitalize column names
def Capitalize(df):
    df.columns = [' '.join([word.capitalize() for word in col.strip().split()]) for col in df.columns]
    print("Capitalized column names:\n", df.columns)  # Debugging line
    return df

# Add brackets to the 'Type' column for "Sell"
def Add_Brackets_To_Sell(df):
    print("Original 'Type' column:\n", df["Type"])  # Debugging line
    df["Type"] = df["Type"].apply(lambda x: f'[{x}]' if x.strip().lower() == "sell" else x)
    print("Brackets added to 'Type' column:\n", df["Type"])  # Debugging line
    return df

# Validate the file by checking required columns
def Validate_file(df):
    expected_columns = ["Type", "Rate Per Share", "Quantity"]
    if set(df.columns) != set(expected_columns):
        st.error("Invalid columns. Required columns are: Type, Rate Per Share, Quantity.")
        return False
    return True

# Initialize additional columns for calculations
def initialize_columns(df):
    df["Amount (R.S)"] = df["Quantity"] * df["Rate Per Share"]
    df["Cumulative Quantity"] = 0
    df["Cumulative Amount (R.S)"] = 0
    df["Avg Rate Per Share"] = 0
    df["Profit and Loss"] = 0
    df["Cumulative Profit (R.S)"] = 0
    return df

# Perform calculations for stock transactions
def Perform_Calculation(df):
    for i in range(len(df)):
        if i == 0:
            df.loc[i, "Cumulative Quantity"] = df.loc[i, "Quantity"]
            df.loc[i, "Cumulative Amount (R.S)"] = df.loc[i, "Amount (R.S)"]
            df.loc[i, "Avg Rate Per Share"] = df.loc[i, "Cumulative Amount (R.S)"] / df.loc[i, "Cumulative Quantity"]
            df.loc[i, "Profit and Loss"] = df.loc[i, "Quantity"] * (df.loc[i, "Rate Per Share"] - df.loc[i, "Avg Rate Per Share"])
        elif df.loc[i, "Type"].strip('[]') == "Purchase":
            df.loc[i, "Cumulative Quantity"] = df.loc[i - 1, "Cumulative Quantity"] + df.loc[i, "Quantity"]
            df.loc[i, "Cumulative Amount (R.S)"] = df.loc[i - 1, "Cumulative Amount (R.S)"] + df.loc[i, "Amount (R.S)"]
            if df.loc[i - 1, "Cumulative Quantity"] == 0:
                df.loc[i, "Avg Rate Per Share"] = df.loc[i, "Rate Per Share"]
            else:
                df.loc[i, "Avg Rate Per Share"] = df.loc[i, "Cumulative Amount (R.S)"] / df.loc[i, "Cumulative Quantity"]
        elif df.loc[i, "Type"].strip('[]') == "Sell":
            df.loc[i, "Cumulative Quantity"] = df.loc[i - 1, "Cumulative Quantity"] - df.loc[i, "Quantity"]
            df.loc[i, "Cumulative Amount (R.S)"] = df.loc[i - 1, "Cumulative Amount (R.S)"] - (df.loc[i - 1, "Avg Rate Per Share"] * df.loc[i, "Quantity"])
            if df.loc[i, "Cumulative Quantity"] == 0:
                df.loc[i, "Avg Rate Per Share"] = df.loc[i - 1, "Avg Rate Per Share"]
            else:
                df.loc[i, "Avg Rate Per Share"] = df.loc[i, "Cumulative Amount (R.S)"] / df.loc[i, "Cumulative Quantity"]
            df.loc[i, "Profit and Loss"] = df.loc[i, "Quantity"] * (df.loc[i, "Rate Per Share"] - df.loc[i, "Avg Rate Per Share"])

    return df.fillna(0)

# Cumulative Profit & Loss calculation
def Cummulative_Profit_Loss(df):
    mask = df["Type"].str.strip('[]') != "Purchase"
    df.loc[mask, "Cumulative Profit (R.S)"] = df.loc[mask, "Profit and Loss"].cumsum()
    df.loc[~mask, "Cumulative Profit (R.S)"] = 0
    df["Cumulative Profit (R.S)"] = df["Cumulative Profit (R.S)"].round(2)
    return df

# Run the pipeline
def run_pipeline(uploaded_file):
    df = Load_File(uploaded_file)
    if df is None:
        return

    df = Capitalize(df)
    df = Add_Brackets_To_Sell(df)

    if not Validate_file(df):
        return

    df = initialize_columns(df)
    df = Perform_Calculation(df)
    df = Cummulative_Profit_Loss(df)

    st.write("Processed Data:")
    st.dataframe(df)

    return df

# Export data to Excel
def Export_to_Excel(df, file_name):
    try:
        df.to_excel(file_name, index=False)
        st.success("File exported successfully!")
    except Exception as e:
        st.error(f"Failed to export file: {e}")

# Streamlit UI
st.title("Stock Calculation Tool")

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# Run button
if st.button("Run Calculation"):
    if uploaded_file:
        df = run_pipeline(uploaded_file)
    else:
        st.error("Please upload a file before proceeding.")

# Export to Excel button
if st.button("Export to Excel") and 'df' in locals():
    export_file_name = st.text_input("Enter the file name (without extension):", "output")
    if export_file_name:
        Export_to_Excel(df, f"{export_file_name}.xlsx")
    else:
        st.error("Please provide a valid file name.")
