import tensorflow as tf
import json
import os
import numpy as np

def strip_keras3_keys(obj):
    if isinstance(obj, dict):
        # Remove Keras 3 specifics that TF.js might not like
        obj.pop('module', None)
        obj.pop('registered_name', None)
        obj.pop('build_config', None)
        for key in list(obj.keys()):
            strip_keras3_keys(obj[key])
    elif isinstance(obj, list):
        for item in obj:
            strip_keras3_keys(item)

# Load Keras 3 model
model_path = 'models/plant_classifier.keras'
print(f"Loading model from {model_path}...")
model = tf.keras.models.load_model(model_path)

# Save as H5 to get older-style configuration
h5_path = 'models/temp_model.h5'
model.save(h5_path)
print(f"Saved temporary H5 model to {h5_path}")

model_h5 = tf.keras.models.load_model(h5_path)

# Extract weights
weights_path = 'models/tfjs_model/weights.bin'
os.makedirs('models/tfjs_model', exist_ok=True)

all_weights = []
weight_data = bytearray()

for layer in model_h5.layers:
    weights = layer.get_weights()
    for i, w in enumerate(weights):
        w_f32 = w.astype(np.float32)
        raw = w_f32.tobytes()
        all_weights.append({
            'name': f'{layer.name}/weight_{i}',
            'shape': list(w.shape),
            'dtype': 'float32'
        })
        weight_data.extend(raw)

with open(weights_path, 'wb') as f:
    f.write(weight_data)

# Create model.json with correct wrapping for TF.js loadLayersModel
try:
    config = json.loads(model_h5.to_json())
    # Strip Keras 3 keys
    strip_keras3_keys(config)
    
    # Wrap in model_config as expected by TF.js
    wrapped_topology = {
        'model_config': config,
        'keras_version': '2.2.4', # Fake a compatible version
        'backend': 'tensorflow'
    }
except Exception as e:
    print(f"Error generating JSON: {e}")
    wrapped_topology = {}

model_json = {
    'format': 'layers-model',
    'generatedBy': 'Antigravity-Manual-Converter-v2',
    'convertedBy': None,
    'modelTopology': wrapped_topology,
    'weightsManifest': [
        {
            'paths': ['weights.bin'],
            'weights': all_weights
        }
    ]
}

with open('models/tfjs_model/model.json', 'w') as f:
    json.dump(model_json, f)

# Labels
class_names = ['Banana','Cotton','Groundnut','Sunflower','jute','maize','rice','sugarcane','wheat']
with open('models/tfjs_model/labels.json', 'w') as f:
    json.dump(class_names, f)

print("Manual conversion v2 finished. Created wrapped model.json.")
