"""
Build a gallery of failure cases: images where the fine-tuned model's
predictions disagree with ground-truth labels (missed detections, false
positives, or wrong counts). Saves annotated images + a causes.txt summary.
"""

import os
import shutil
from pathlib import Path
from ultralytics import YOLO

MODEL_PATH = "runs/detect/train_size_600/weights/best.pt"
TEST_IMAGES_DIR = Path("dataset_size_600/test/images")
TEST_LABELS_DIR = Path("dataset_size_600/test/labels")
OUT_DIR = Path("failure_gallery")
NUM_FAILURES = 12

OUT_DIR.mkdir(exist_ok=True)
model = YOLO(MODEL_PATH)

CLASS_NAMES = {0: "head", 1: "helmet", 2: "vest"}

def load_gt_counts(label_path):
    counts = {0: 0, 1: 0, 2: 0}
    if label_path.exists():
        with open(label_path) as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    cls = int(parts[0])
                    counts[cls] = counts.get(cls, 0) + 1
    return counts

candidates = []
image_files = sorted(os.listdir(TEST_IMAGES_DIR))[:300]  # cap for speed

for img_name in image_files:
    img_path = TEST_IMAGES_DIR / img_name
    label_path = TEST_LABELS_DIR / (os.path.splitext(img_name)[0] + ".txt")

    gt_counts = load_gt_counts(label_path)
    results = model.predict(str(img_path), conf=0.25, verbose=False)
    pred_counts = {0: 0, 1: 0, 2: 0}
    for box in results[0].boxes:
        cls = int(box.cls[0])
        pred_counts[cls] = pred_counts.get(cls, 0) + 1

    mismatch = sum(abs(gt_counts.get(c, 0) - pred_counts.get(c, 0)) for c in CLASS_NAMES)
    if mismatch > 0:
        candidates.append((mismatch, img_name, gt_counts, pred_counts, results[0]))

candidates.sort(key=lambda x: -x[0])
top_failures = candidates[:NUM_FAILURES]

causes_log = []
for i, (mismatch, img_name, gt, pred, result) in enumerate(top_failures, 1):
    save_name = f"failure_{i:02d}_{img_name}"
    result.save(filename=str(OUT_DIR / save_name))

    missed = {CLASS_NAMES[c]: gt[c] - pred[c] for c in CLASS_NAMES if gt[c] > pred[c]}
    extra = {CLASS_NAMES[c]: pred[c] - gt[c] for c in CLASS_NAMES if pred[c] > gt[c]}

    if missed and not extra:
        cause = f"Missed detection(s): {missed} - likely occlusion, small scale, or low contrast against background"
    elif extra and not missed:
        cause = f"False positive(s): {extra} - likely background clutter or overlapping objects confused for PPE"
    else:
        cause = f"Mixed errors - missed {missed}, extra {extra} - likely difficult lighting/angle or class confusion (head vs helmet)"

    causes_log.append(f"{save_name}: GT={gt}, Pred={pred} -> {cause}")
    print(f"[{i}/{len(top_failures)}] {img_name}: {cause}")

with open(OUT_DIR / "causes.txt", "w") as f:
    f.write("Failure Gallery - Cause Analysis\n")
    f.write("=" * 50 + "\n\n")
    f.write("\n".join(causes_log))

print(f"\nDone! {len(top_failures)} failure cases saved to {OUT_DIR}/")