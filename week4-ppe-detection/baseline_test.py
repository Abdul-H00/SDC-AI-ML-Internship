"""
Baseline Test — Pre-trained YOLOv8 (before any fine-tuning)
This runs the stock YOLOv8 model on our validation images, unchanged,
so we have a "before" result to compare our fine-tuned model against.
"""

from ultralytics import YOLO

# Load a pre-trained YOLOv8 model (trained on general COCO dataset,
# NOT on our specific hardhat/vest data yet)
model = YOLO("yolov8n.pt")  # "n" = nano, smallest/fastest version

# Run it on our validation set, as-is, with no training
results = model.val(data="HardHat-&-SafetyVest-1/data.yaml")

print("\n=== BASELINE RESULTS (pre-trained, no fine-tuning) ===")
print(f"mAP50: {results.box.map50}")
print(f"mAP50-95: {results.box.map}")