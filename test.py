from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Input
import os

print("🔧 Creating dummy model...")

model = Sequential([
    Input(shape=(224, 224, 3)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("💾 Saving model as model.h5...")
model.save("model.h5")

# Check if saved
if os.path.exists("model.h5"):
    print("✅ model.h5 saved successfully in:", os.getcwd())
else:
    print("❌ model.h5 NOT found after saving.")