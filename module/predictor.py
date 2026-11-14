import numpy as np
import pandas as pd
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class MLPredictor:
    """
    Machine Learning engine for predicting price movement directions (UP/DOWN)
    using Random Forest classification on engineered technical features.
    """
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        self.scaler = StandardScaler()
        self.logger = logging.getLogger("MLPredictor")
        self.is_trained = False

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        data['Returns'] = data['Close'].pct_change()
        data['SMA_10'] = data['Close'].rolling(10).mean()
        data['SMA_30'] = data['Close'].rolling(30).mean()
        data['Volatility'] = data['Returns'].rolling(10).std()
        
        # Target: 1 if next Close is higher, else 0
        data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
        return data.dropna()

    def train(self, df: pd.DataFrame) -> dict:
        data = self.extract_features(df)
        feature_cols = ['Returns', 'SMA_10', 'SMA_30', 'Volatility']
        
        X = data[feature_cols]
        y = data['Target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_state=42, test_size=0.2, shuffle=False)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        accuracy = self.model.score(X_test_scaled, y_test)
        self.logger.info(f"ML Model trained successfully. Test Accuracy: {accuracy:.4f}")
        return {"test_accuracy": round(accuracy, 4)}

    def predict(self, df: pd.DataFrame) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling predict().")
        
        data = self.extract_features(df)
        feature_cols = ['Returns', 'SMA_10', 'SMA_30', 'Volatility']
        latest_features = data[feature_cols].iloc[[-1]]
        
        scaled_features = self.scaler.transform(latest_features)
        prediction = self.model.predict(scaled_features)[0]
        probabilities = self.model.predict_proba(scaled_features)[0]
        
        signal = "BUY" if prediction == 1 else "SELL"
        confidence = probabilities[prediction]
        
        return {
            "prediction": signal,
            "confidence": round(float(confidence), 4),
            "prob_down": round(float(probabilities[0]), 4),
            "prob_up": round(float(probabilities[1]), 4)
        }

if __name__ == "__main__":
    dates = pd.date_range(end=pd.Timestamp.now(), periods=300)
    sample_df = pd.DataFrame({
        'Close': 100 + np.random.randn(300).cumsum()
    }, index=dates)

    predictor = MLPredictor()
    metrics = predictor.train(sample_df)
    res = predictor.predict(sample_df)
    print("Model Metrics:", metrics)
    print("Latest Signal Prediction:", res)