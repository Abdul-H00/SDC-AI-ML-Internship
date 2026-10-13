# Scope Statement

**Project**: SiteGuard AI - PPE (Personal Protective Equipment) Detection Tool for a Regional Real Estate Agency

**Problem**: During property inspections and construction-site visits, the agency needs a reliable way to verify that site workers and visitors are wearing required safety gear (hard hats, safety vests). Manual visual checks are slow and inconsistent.

**Approach**: Fine-tune a pre-trained YOLOv8n object detection model on a labeled hardhat/vest/head dataset, using transfer learning. Compare the untrained baseline against fine-tuned models trained at 3 data sizes (100, 300, 600 images) to measure how performance scales with training data.

**Success target**: Achieve at least 50% mAP50 on the validation set after fine-tuning (baseline achieves ~0.2%).

**Result so far**: Target already exceeded - 100 images reached 53.1% mAP50, 300 images reached 66.5% mAP50.
