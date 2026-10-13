"""
Fine-tune YOLOv8 on our hardhat/vest dataset at a given size.
Usage: python train.py <size>   e.g.  python train.py 100
"""

import sys
from ultralytics import YOLO

size = sys.argv[1] if len(sys.argv) > 1 else "100"
data_yaml = f"dataset_size_{size}/data.yaml"
run_name = f"train_size_{size}"

# Start from the same pre-trained weights as our baseline
model = YOLO("yolov8n.pt")

results = model.train(
    data=data_yaml,
    epochs=30,          # kept modest since we're training on CPU
    imgsz=416,           # smaller image size = faster on CPU
    batch=8,
    name=run_name,
    patience=10,          # stop early if no improvement
    # Augmentations (built into YOLOv8's training pipeline):
    hsv_h=0.015,          # 1. hue/color jitter
    hsv_s=0.7,            # 2. saturation jitter
    fliplr=0.5,           # 3. horizontal flip (50% chance)
    mosaic=1.0,           # 4. mosaic augmentation (combines 4 images)
)

print(f"\n=== Training complete for size={size} ===")
print(f"Results saved under: runs/detect/{run_name}")