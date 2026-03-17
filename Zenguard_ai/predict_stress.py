import pandas as pd
import joblib
import numpy as np

# Load the trained model and scaler safely
try:
    model = joblib.load("typing_stress_model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("✅ Model and scaler loaded successfully!")
except Exception as e:
    print("❌ Error loading model or scaler:", e)
    exit()

# Try multiple encodings to handle Excel export issues
file_path = "new_typing_sample.csv"
encodings_to_try = ['utf-8', 'latin1', 'cp1252']

for enc in encodings_to_try:
    try:
        test_df = pd.read_csv(file_path, encoding=enc)
        print(f"✅ File loaded successfully using encoding: {enc}")
        break
    except Exception as e:
        if enc == encodings_to_try[-1]:
            print("❌ Could not read CSV with any encoding:", e)
            exit()
        continue

print("Columns in test file:", test_df.columns.tolist())

# Expected features (must match training)
features = ['DU.key1.key1', 'DD.key1.key2', 'DU.key1.key2', 'UD.key1.key2']

# Fix potential column name mismatches (strip spaces, lowercase, etc.)
test_df.columns = test_df.columns.str.strip()

# Check if all required columns exist
missing = [f for f in features if f not in test_df.columns]
if missing:
    print(f"⚠️ Missing columns in test file: {missing}")
    print("Please make sure your file has the same feature names as the training data.")
    exit()

# Select and clean features
X_test = test_df[features].apply(pd.to_numeric, errors='coerce')
X_test = X_test.fillna(X_test.mean())

# Scale features using saved scaler
X_test_scaled = scaler.transform(X_test)

# Predict probabilities (stress score)
pred_probs = model.predict_proba(X_test_scaled)[:, 1]  # probability of being stressed
stress_percent = (pred_probs * 100).round(2)

# Combine predictions with original data
test_df["Predicted_Stress_%"] = stress_percent

# Save result to new file
output_path = "predicted_stress_output.csv"
test_df.to_csv(output_path, index=False)
print(f"\n✅ Predictions saved to '{output_path}'")

# Show sample results
print("\nSample Predictions:")
print(test_df[["DU.key1.key1", "DD.key1.key2", "DU.key1.key2", "UD.key1.key2", "Predicted_Stress_%"]].head())
