import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

print("Loading dataset...")
df = pd.read_csv("typing_data.csv")

print("Available columns:", df.columns.tolist())

# === Auto-select feature columns ===
possible_features = [
    'DU.key1.key1', 'DD.key1.key2', 'DU.key1.key2',
    'UD.key1.key2', 'UU.key1.key2'
]
features = [f for f in possible_features if f in df.columns]
if not features:
    raise ValueError("❌ No valid typing timing features found in dataset!")

print(f"✅ Using features: {features}")

# === Create target label ===
# Assuming 'session' = 1 → not stressed, 'session' = 2 → stressed
df["Label"] = df["session"].apply(lambda x: 1 if x == 2 else 0)

# === Prepare features ===
X = df[features].copy()

# Convert everything to numeric (non-numeric -> NaN)
X = X.apply(pd.to_numeric, errors='coerce')

# Fill NaNs with column means
X = X.fillna(X.mean())

y = df["Label"]

# === Split into train/test ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === Standardize & Train ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train_scaled, y_train)

# === Evaluation ===
y_pred = model.predict(X_test_scaled)
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# === Save model & scaler ===
joblib.dump(model, "typing_stress_model.pkl")
joblib.dump(scaler, "typing_scaler.pkl")

print("✅ Model and scaler saved successfully!")

# ✅ Save model and scaler separately


joblib.dump(model, "typing_stress_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("\n✅ Model and scaler saved successfully!")

