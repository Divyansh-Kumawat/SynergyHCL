from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os

app = Flask(__name__)
CORS(app)

# Global variables to hold data
customer_features = None
model = None

def load_resources():
    global customer_features, model
    
    # Load customer features
    features_path = r"d:\webdev\HCL\backend\customer_features.csv"
    if os.path.exists(features_path):
        customer_features = pd.read_csv(features_path)
        # Ensure cust_id is string for easy lookup
        customer_features['cust_id'] = customer_features['cust_id'].astype(str)
        # set index for fast lookup
        customer_features.set_index('cust_id', inplace=True)
        print(f"Loaded {len(customer_features)} customer records.")
    else:
        print(f"Warning: {features_path} not found. Please run prepare_data.py first.")
        
    # Load Model
    model_path = r"d:\webdev\HCL\final_xgboost_model.pkl"
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print("Model loaded successfully.")
    else:
        print(f"Warning: Model not found at {model_path}")

# Load on startup
load_resources()

@app.route('/api/customers', methods=['GET'])
def get_customers():
    if customer_features is None:
        return jsonify({"error": "Data not loaded"}), 500
        
    limit = request.args.get('limit', 100, type=int)
    search = request.args.get('search', '').lower()
    
    # Get all index values (customer IDs)
    cust_ids = customer_features.index.tolist()
    
    # Filter if search term is provided
    if search:
        cust_ids = [cid for cid in cust_ids if search in cid.lower()]
        
    # Take top N
    response_ids = cust_ids[:limit]
    
    return jsonify({
        "customers": response_ids,
        "total": len(cust_ids)
    })

@app.route('/api/predict/<cust_id>', methods=['GET'])
def predict_spend(cust_id):
    if customer_features is None or model is None:
        return jsonify({"error": "Server not ready"}), 500
        
    if cust_id not in customer_features.index:
        return jsonify({"error": f"Customer ID {cust_id} not found"}), 404
        
    # Retrieve customer data
    cust_data = customer_features.loc[cust_id]
    
    # Features required for the model
    # 'recency', 'frequency', 'monetary', 'avg_order_value', 'spend_per_day', 'loyalty_score'
    feature_cols = ['recency', 'frequency', 'monetary', 'avg_order_value', 'spend_per_day', 'loyalty_score']
    
    # Create DataFrame with exactly these columns in order
    X = pd.DataFrame([cust_data[feature_cols].values], columns=feature_cols)
    
    # Predict
    try:
        prediction = model.predict(X)[0]
        # Round prediction
        prediction = max(0, float(round(prediction, 2))) # can't have negative spend
        
        return jsonify({
            "cust_id": cust_id,
            "prediction": prediction,
            "metrics": {
                "recency": int(cust_data['recency']),
                "frequency": int(cust_data['frequency']),
                "monetary": float(round(cust_data['monetary'], 2)),
                "avg_order_value": float(round(cust_data['avg_order_value'], 2)),
            }
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
