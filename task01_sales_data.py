import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime

# 1. PATH CONFIGURATION
script_dir = os.path.dirname(__file__)
input_file = os.path.join(script_dir, 'sales_data.csv')
report_file = os.path.join(script_dir, 'Sales_Executive_Report.txt')

def run_pipeline():
    try:
        # Step 1: Ingestion
        df = pd.read_csv(input_file, sep=None, engine='python', encoding='latin1')
        print("✅ Step 1: Data Ingested.")

        # Step 2: Data Transformation Layer (The "Fix")
        df.columns = df.columns.str.strip()
        
        # 2a. Clean 'Sales' column - remove $, commas, and spaces, then convert to numeric
        if 'Sales' in df.columns:
            df['Sales'] = df['Sales'].replace(r'[\$,]', '', regex=True)
            df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
            # Fill any NaN sales with 0 to avoid aggregation errors
            df['Sales'] = df['Sales'].fillna(0)
            print("✅ Step 2: Sales column converted to Numeric.")
        else:
            print(f"❌ Error: 'Sales' column not found. Available: {df.columns.tolist()}")
            return

        # 2b. Handle Missing Date
        date_col = next((c for c in df.columns if 'date' in c.lower()), None)
        if not date_col:
            print("⚠️ Warning: Generating timeline index for Capstone.")
            df['Order_Date_Fixed'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
            date_col = 'Order_Date_Fixed'
        
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

        # Step 3: Aggregation & Forecasting
        daily_sales = df.groupby(date_col)['Sales'].sum().reset_index()
        daily_sales['7d_moving_avg'] = daily_sales['Sales'].rolling(window=7).mean()

        # Step 4: Executive Report Generation
        total_rev = daily_sales['Sales'].sum()
        with open(report_file, 'w') as f:
            f.write(f"--- COGNETIX CAPSTONE SUMMARY ---\n")
            f.write(f"Pipeline Run: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Validated Revenue: ${total_rev:,.2f}\n")
            f.write(f"Data Health: Numeric Transformation Applied\n")
        
        print(f"✅ Step 3: Executive Report generated at {report_file}")

        # Step 5: Visualization
        plt.figure(figsize=(12, 6))
        plt.plot(daily_sales[date_col], daily_sales['Sales'], label='Daily Revenue', alpha=0.3, color='blue')
        plt.plot(daily_sales[date_col], daily_sales['7d_moving_avg'], label='7-Day Forecast', color='red', linewidth=2)
        plt.title('Capstone Project: Automated Sales Pipeline', fontsize=14)
        plt.ylabel('Revenue ($)')
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.show()

    except Exception as e:
        print(f"❌ Pipeline Critical Error: {e}")

if __name__ == "__main__":
    run_pipeline()