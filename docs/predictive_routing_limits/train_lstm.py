"""Train a 2-layer LSTM (matched to the deployed GRU: 64 units, dropout 0.2)
on METR-LA, as a real architectural alternative for the predictor-ablation paper.
Saves models/saved/lstm_best.keras and prints inverse-transformed test MAE/RMSE.
"""
import os, pickle, numpy as np
import tensorflow as tf
from tensorflow.keras import layers, callbacks, Sequential

d = np.load("data/processed/training_data.npz")
Xtr, ytr = d["X_train"], d["y_train"]
Xva, yva = d["X_val"], d["y_val"]
Xte, yte = d["X_test"], d["y_test"]
N = Xtr.shape[-1]; NF = ytr.shape[1]
scaler = pickle.load(open("data/processed/scaler.pkl", "rb"))

model = Sequential([
    layers.Input(shape=(Xtr.shape[1], N)),
    layers.LSTM(64, return_sequences=True),
    layers.Dropout(0.2),
    layers.LSTM(64, return_sequences=False),
    layers.Dropout(0.2),
    layers.Dense(NF * N),
    layers.Reshape((NF, N)),
])
model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse", metrics=["mae"])
cbs = [
    callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True, verbose=1),
    callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6, verbose=1),
    callbacks.ModelCheckpoint("models/saved/lstm_best.keras", monitor="val_loss", save_best_only=True),
]
model.fit(Xtr, ytr, validation_data=(Xva, yva), epochs=100, batch_size=64, callbacks=cbs, verbose=2)

def inv(a):
    return scaler.inverse_transform(a.reshape(-1, N)).reshape(a.shape)
pred = model.predict(Xte, verbose=0)
mae = float(np.mean(np.abs(inv(pred) - inv(yte))))
rmse = float(np.sqrt(np.mean((inv(pred) - inv(yte)) ** 2)))
print(f"LSTM_TEST_MAE={mae:.3f} RMSE={rmse:.3f}")
open("results/lstm_metrics.txt", "w").write(f"MAE={mae:.3f}\nRMSE={rmse:.3f}\n")
