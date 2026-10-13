"""
Create 3 smaller training subsets (100, 300, 600 images) from the full
HardHat & SafetyVest dataset. This supports the Week 4 requirement to
repeat the key experiment at 3 different data sizes and compare results.

Validation and test sets stay the SAME across all 3 experiments, so the
comparison is fair (only the amount of training data changes).
"""

import os
import random
import shutil
from pathlib import Path

random.seed(42)  # reproducible randomness

SOURCE = Path("HardHat-&-SafetyVest-1")
SIZES = [100, 300, 600]

# Get all training images (the .jpg files; each has a matching .txt label)
train_images_dir = SOURCE / "train" / "images"
all_images = sorted([f for f in os.listdir(train_images_dir) if f.endswith((".jpg", ".png", ".jpeg"))])

print(f"Total training images available: {len(all_images)}")

for size in SIZES:
    subset_name = f"dataset_size_{size}"
    subset_path = Path(subset_name)

    # Create folder structure matching YOLO format
    (subset_path / "train" / "images").mkdir(parents=True, exist_ok=True)
    (subset_path / "train" / "labels").mkdir(parents=True, exist_ok=True)

    # Randomly pick `size` images for this subset's training set
    chosen = random.sample(all_images, min(size, len(all_images)))

    for img_name in chosen:
        label_name = os.path.splitext(img_name)[0] + ".txt"

        src_img = train_images_dir / img_name
        src_label = SOURCE / "train" / "labels" / label_name

        dst_img = subset_path / "train" / "images" / img_name
        dst_label = subset_path / "train" / "labels" / label_name

        if src_img.exists():
            shutil.copy(src_img, dst_img)
        if src_label.exists():
            shutil.copy(src_label, dst_label)

    # Copy the SAME valid and test sets into each subset (unchanged),
    # so all 3 experiments are evaluated fairly on identical data
    for split in ["valid", "test"]:
        src_split = SOURCE / split
        dst_split = subset_path / split
        if src_split.exists() and not dst_split.exists():
            shutil.copytree(src_split, dst_split)

    # Write a data.yaml for this subset
    data_yaml_content = f"""train: {subset_name}/train/images
val: {subset_name}/valid/images
test: {subset_name}/test/images

nc: 3
names: ['head', 'helmet', 'vest']
"""
    with open(subset_path / "data.yaml", "w") as f:
        f.write(data_yaml_content)

    print(f"Created {subset_name}: {len(chosen)} training images")

print("\nDone! 3 subsets created: dataset_size_100, dataset_size_300, dataset_size_600")