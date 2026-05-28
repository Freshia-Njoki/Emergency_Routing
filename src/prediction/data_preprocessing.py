"""
Data Preprocessing for Traffic Prediction
Converts time series data into sequences for GRU/LSTM training
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pickle

class TrafficDataPreprocessor:
    """Prepare traffic data for prediction models"""
    
    def __init__(self, sequence_length=12, horizon=6):
        """
        Args:
            sequence_length: How many past timesteps to use (12 = 1 hour at 5-min intervals)
            horizon: How many future timesteps to predict (6 = 30 min)
        """
        self.sequence_length = sequence_length
        self.horizon = horizon
        self.scaler = StandardScaler()
        
        print(f"📊 Preprocessor initialized:")
        print(f"   - Input sequence: {sequence_length} timesteps ({sequence_length * 5} minutes)")
        print(f"   - Prediction horizon: {horizon} timesteps ({horizon * 5} minutes)")
    
    def create_sequences(self, data):
        """
        Convert time series to sequences for training
        
        Args:
            data: 2D array (timesteps, features)
            
        Returns:
            X: Input sequences (samples, sequence_length, features)
            y: Target sequences (samples, horizon, features)
        """
        X, y = [], []
        
        print(f"\n🔄 Creating sequences from {len(data)} timesteps...")
        
        for i in range(len(data) - self.sequence_length - self.horizon):
            # Input: past 'sequence_length' timesteps
            X.append(data[i:i + self.sequence_length])
            
            # Target: next 'horizon' timesteps
            y.append(data[i + self.sequence_length:i + self.sequence_length + self.horizon])
            
            # Progress indicator
            if (i + 1) % 5000 == 0:
                print(f"   Processed {i + 1} sequences...")
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"✅ Created {len(X)} sequences")
        print(f"   - X shape: {X.shape} (samples, sequence_length, features)")
        print(f"   - y shape: {y.shape} (samples, horizon, features)")
        
        return X, y
    
    def prepare_data(self, df, train_ratio=0.7, val_ratio=0.15):
        """
        Full preprocessing pipeline
        
        Args:
            df: DataFrame with traffic data
            train_ratio: Proportion for training
            val_ratio: Proportion for validation
            
        Returns:
            train_data: (X_train, y_train)
            val_data: (X_val, y_val)
            test_data: (X_test, y_test)
        """
        print("\n" + "="*60)
        print("DATA PREPROCESSING PIPELINE")
        print("="*60)
        
        # Convert to numpy array
        data = df.values
        print(f"\n📥 Input data shape: {data.shape}")
        print(f"   - Timesteps: {data.shape[0]:,}")
        print(f"   - Sensors: {data.shape[1]}")
        
        # Handle missing values (replace 0 with mean)
        print("\n🔧 Handling missing values...")
        for col in range(data.shape[1]):
            col_data = data[:, col]
            non_zero = col_data[col_data > 0]
            if len(non_zero) > 0:
                mean_val = non_zero.mean()
                data[col_data == 0, col] = mean_val
        
        print("✅ Missing values handled")
        
        # Normalize data
        print("\n📐 Normalizing data...")
        data_normalized = self.scaler.fit_transform(data)
        print(f"✅ Data normalized (mean=0, std=1)")
        
        # Create sequences
        X, y = self.create_sequences(data_normalized)
        
        # Split into train/val/test
        print(f"\n✂️ Splitting data...")
        n = len(X)
        train_size = int(n * train_ratio)
        val_size = int(n * val_ratio)
        
        X_train = X[:train_size]
        y_train = y[:train_size]
        
        X_val = X[train_size:train_size + val_size]
        y_val = y[train_size:train_size + val_size]
        
        X_test = X[train_size + val_size:]
        y_test = y[train_size + val_size:]
        
        print(f"✅ Data split complete:")
        print(f"   - Training: {len(X_train):,} samples ({train_ratio*100:.0f}%)")
        print(f"   - Validation: {len(X_val):,} samples ({val_ratio*100:.0f}%)")
        print(f"   - Test: {len(X_test):,} samples ({(1-train_ratio-val_ratio)*100:.0f}%)")
        
        # Save scaler for later use
        with open('models/saved/scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        print("\n💾 Scaler saved to: models/saved/scaler.pkl")
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)

# Test the preprocessor
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING DATA PREPROCESSOR")
    print("="*60)
    
    # Load data
    print("\n📂 Loading METR-LA data...")
    df = pd.read_hdf('data/raw/metr-la.h5')
    print(f"✅ Loaded: {df.shape}")
    
    # Create preprocessor
    preprocessor = TrafficDataPreprocessor(
        sequence_length=12,  # 1 hour of history
        horizon=6            # 30 min prediction
    )
    
    # Prepare data
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = preprocessor.prepare_data(df)
    
    print("\n" + "="*60)
    print("✅ PREPROCESSING TEST COMPLETE!")
    print("="*60)


# Save the preprocessed data
print("\n💾 Saving preprocessed data...")
np.savez(
    'data/processed/training_data.npz',
    X_train=X_train,
    y_train=y_train,
    X_val=X_val,
    y_val=y_val,
    X_test=X_test,
    y_test=y_test
)
print("✅ Saved: data/processed/training_data.npz")