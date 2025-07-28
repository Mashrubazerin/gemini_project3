import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Input

# Build dummy model
model = Sequential([
    Input(shape=(224, 224, 3)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(3, activation='softmax')  # 3 classes: Cool, Warm, Neutral
])

# Compile and save
model.compile(optimizer='adam', loss='categorical_crossentropy')
model.save("model.h5")
print("✅ Dummy model saved as model.h5")
