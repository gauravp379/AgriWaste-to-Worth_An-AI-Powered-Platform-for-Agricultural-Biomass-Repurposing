"""
Generate a clean TF.js LayersModel for the plant classifier
Properly tracks byte offsets for each weight tensor in the weights manifest
"""
import os, json, sys
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(BASE, 'models', 'tfjs_model')
os.makedirs(out_dir, exist_ok=True)

# Labels
class_names = ['Banana','Cotton','Groundnut','Sunflower','jute','maize','rice','sugarcane','wheat']
with open(os.path.join(out_dir, 'labels.json'), 'w') as f:
    json.dump(class_names, f)
print('Labels written')

import tensorflow as tf
print(f'TF {tf.__version__}')
model = tf.keras.models.load_model(os.path.join(BASE, 'models', 'plant_classifier.keras'))
print(f'Model input={model.input_shape} output={model.output_shape}')

# Collect all weights
all_weight_data = bytearray()
all_weight_specs = []

for layer in model.layers:
    try:
        weights = layer.get_weights()
    except Exception:
        continue
    if not weights:
        continue
    for i, w in enumerate(weights):
        w_f32 = w.astype(np.float32)
        raw = w_f32.tobytes()
        # append raw bytes
        all_weight_data.extend(raw)
        all_weight_specs.append({
            'name': f'{layer.name}/weight_{i}',
            'shape': list(w.shape),
            'dtype': 'float32',
        })

# Write a single weights.bin
with open(os.path.join(out_dir, 'weights.bin'), 'wb') as f:
    f.write(all_weight_data)
print(f'weights.bin: {len(all_weight_data):,} bytes, {len(all_weight_specs)} tensors')

# Build model.json with proper weightsManifest
model_config = json.loads(model.to_json())
model_json = {
    'format': 'layers-model',
    'generatedBy': 'custom-exporter-v2',
    'convertedBy': None,
    'modelTopology': model_config,
    'weightsManifest': [
        {
            'paths': ['weights.bin'],
            'weights': all_weight_specs
        }
    ]
}
with open(os.path.join(out_dir, 'model.json'), 'w') as f:
    json.dump(model_json, f)

print('model.json written')
print('Files:', os.listdir(out_dir))
print('\nSUCCESS!')
