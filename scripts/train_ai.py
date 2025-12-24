import sys
import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler

# --- CRITICAL: PROJECT ROOT CONFIGURATION ---
# This ensures the script can locate the 'strategy' and 'data' directories
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from strategy.ai_model import PricePredictorLSTM 

def train_with_real_data(file_path, epochs=50, seq_length=50):
    """
    Trains the LSTM model using real Binance OHLCV data.
    Implements fine-tuning if V1 weights are detected.
    """
    # 1. Path Resolution
    actual_file_path = os.path.join(project_root, file_path)
    if not os.path.exists(actual_file_path):
        print(f"❌ ERROR: Dataset not found at {actual_file_path}")
        return

    print(f"--- 🚀 AEGIS-LOB AI TRAINING INITIATED: {os.path.basename(actual_file_path)} ---")
    
    # 2. Data Preprocessing
    df = pd.read_csv(actual_file_path)
    if 'close' not in df.columns:
        print("❌ ERROR: 'close' column missing from the dataset.")
        return

    prices = df['close'].values.reshape(-1, 1)

    # Normalize data for LSTM stability
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    def create_sequences(data, length):
        xs, ys = [], []
        for i in range(len(data) - length):
            xs.append(data[i:(i + length)])
            ys.append(data[i + length])
        return np.array(xs), np.array(ys)

    X, y = create_sequences(scaled_prices, seq_length)
    X = torch.from_numpy(X).float()
    y = torch.from_numpy(y).float()

    # 3. Model & Hardware Configuration (GPU/CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PricePredictorLSTM().to(device)
    X, y = X.to(device), y.to(device)
    
    # Fine-tuning: Load V1 weights if they exist in the models directory
    model_dir = os.path.join(project_root, "data", "models")
    v1_path = os.path.join(model_dir, "price_lstm.pth")
    if os.path.exists(v1_path):
        model.load_state_dict(torch.load(v1_path, map_location=device))
        print("💡 Found existing intelligence (V1). Starting fine-tuning on new data...")

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0005)

    # 4. Training Loop
    print(f"Training on {device.type.upper()}...")
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] | Loss: {loss.item():.8f}")

    # 5. Persist Model Weights
    if not os.path.exists(model_dir): 
        os.makedirs(model_dir)
    
    save_path = os.path.join(model_dir, "price_lstm_v2.pth")
    torch.save(model.state_dict(), save_path)
    print(f"--- ✅ SUCCESS: Model saved at {save_path} ---")

if __name__ == "__main__":
    # Default path assumes execution from scripts/ folder
    train_with_real_data("data/binance_BTC_USDT_1m.csv")