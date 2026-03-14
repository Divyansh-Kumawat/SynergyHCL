import pandas as pd
import numpy as np
import os

def prepare_data():
    print("Loading CSV...")
    csv_path = r"d:\webdev\HCL\sales_06_FY2020-21 copy.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return

    df = pd.read_csv(csv_path, low_memory=False)
    
    print("Processing dates and numerics...")
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['qty_ordered'] = pd.to_numeric(df['qty_ordered'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Fill missing values to avoid NaNs dropping
    df['qty_ordered'] = df['qty_ordered'].fillna(df['qty_ordered'].median())
    df['price'] = df['price'].fillna(df['price'].median())
    
    df['transaction_value'] = df['qty_ordered'] * df['price']
    
    print("Calculating RFM...")
    snapshot_date = df['order_date'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('cust_id').agg({
        'order_date': lambda x: (snapshot_date - x.max()).days,
        'cust_id': 'count',
        'transaction_value': 'sum'
    })
    
    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm.reset_index(inplace=True)
    
    print("Calculating advanced features...")
    rfm['avg_order_value'] = rfm['monetary'] / rfm['frequency']
    rfm['avg_order_value'] = rfm['avg_order_value'].fillna(0)
    
    rfm['spend_per_day'] = rfm['monetary'] / (rfm['recency'] + 1)
    rfm['loyalty_score'] = rfm['frequency'] * rfm['monetary']
    
    out_path = r"d:\webdev\HCL\backend\customer_features.csv"
    rfm.to_csv(out_path, index=False)
    print(f"Saved {len(rfm)} customers to {out_path}")

if __name__ == "__main__":
    prepare_data()
