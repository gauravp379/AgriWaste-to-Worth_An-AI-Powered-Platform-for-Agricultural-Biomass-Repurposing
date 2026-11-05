import numpy as np
if not hasattr(np, 'object'):
    np.object = object
if not hasattr(np, 'bool'):
    np.bool = bool
if not hasattr(np, 'complex'):
    np.complex = complex
if not hasattr(np, 'float'):
    np.float = float
if not hasattr(np, 'int'):
    np.int = int

from tensorflowjs.converters.converter import main
import sys
import os

# Ensure output directory exists
os.makedirs('models/tfjs_model', exist_ok=True)

# Mock sys.argv to pass the parameters
sys.argv = [
    'tensorflowjs_converter',
    '--input_format=keras',
    '--output_format=tfjs_layers_model',
    'models/plant_classifier.keras',
    'models/tfjs_model'
]

print("Starting conversion with NumPy monkeypatch...")
try:
    main()
    print("Conversion successful!")
except Exception as e:
    print(f"Conversion failed: {e}")
    import traceback
    traceback.print_exc()
