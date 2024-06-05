import pandas as pd
import os

# Define the list of filenames for each month
months = ['Januari', 'Februari', 'Maret', 'April', 'Mei']

# Directory paths
input_dir = '../dataset/raw_bmkg/2024/csv'
output_dir = '../dataset/filled/scenario3/filled_per_year'
output_file_year = os.path.join(output_dir, '2024-filled.csv')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List to hold the processed data frames
df_list = []

# Process each month's data file
for month in months:
    # Construct the filename
    input_file = os.path.join(input_dir, f'{month}-2024.csv')
    
    # Load the dataset
    df = pd.read_csv(input_file, parse_dates=['Tanggal'], index_col='Tanggal')
    
    # Replace '8888' with NaN for easier handling
    df.replace(8888, pd.NA, inplace=True)
    
    # Convert object types to more appropriate types before interpolation
    df = df.infer_objects()

    # Separate the ddd_car column
    ddd_car = df['ddd_car']
    df = df.drop(columns=['ddd_car'])
    
    # Apply Interpolation
    df_interpolated = df.interpolate(method='linear')
    
    # Check for any remaining missing values
    if df_interpolated.isna().sum().sum() > 0:
        # Apply forward fill
        df_interpolated = df_interpolated.ffill()
        
        # Apply backward fill for any remaining NaNs
        df_interpolated = df_interpolated.bfill()
        
        # Optionally, fill with a constant value (e.g., column mean) as a last resort
        df_interpolated = df_interpolated.fillna(df_interpolated.mean())

    # Round to 1 decimal place
    df_interpolated = df_interpolated.round(1)

    # Re-attach the ddd_car column
    df_interpolated['ddd_car'] = ddd_car
    
    # Append the processed DataFrame to the list
    df_list.append(df_interpolated)

    # Optional: Print the missing data info for verification
    missing_data_before = df.isna().sum()
    missing_data_interpolated = df_interpolated.isna().sum()
    print(f"{month} 2024:")
    print("Missing data before filling:", missing_data_before)
    print("Missing data after interpolation and additional filling:", missing_data_interpolated)
    print("-" * 50)

# Concatenate all monthly DataFrames into one yearly DataFrame
df_year = pd.concat(df_list)

# Save the combined yearly DataFrame to a CSV file
df_year.to_csv(output_file_year)

print(f"All monthly data has been combined and saved to {output_file_year}.")
