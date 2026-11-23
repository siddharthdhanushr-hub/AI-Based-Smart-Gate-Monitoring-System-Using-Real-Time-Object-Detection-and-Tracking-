# Model Evaluation & Benchmark Comparison Report
# AI-Based Smart Gate Monitoring System

## 1. Overview & Objective
This report records the comparative evaluation between:
- **Experiment A**: Pretrained YOLOv8n baseline (MS COCO weights).
- **Experiment B**: Custom fine-tuned YOLOv8n on authorized campus gate footage.

The primary objective is to verify whether domain-specific fine-tuning yields measurable improvements in detection accuracy, IoU localization, and occlusion resistance on campus gate traffic compared to off-the-shelf COCO weights, while maintaining the required inference speed ($\ge 25\text{ FPS}$) for real-time processing.

---

## 2. Benchmark Protocol
- **Evaluation Hardware**: Standard GPU (Google Colab T4 / Local CUDA) with PyTorch 2.x and FP16 inference.
- **Test Dataset**: Identical held-out gate test split (`ai/dataset/images/test`) extracted from independent recording sessions (non-overlapping with training footage).
- **Evaluation Metrics**:
  - Precision ($P$)
  - Recall ($R$)
  - $\text{mAP}@50$
  - $\text{mAP}@50\text{-}95$
  - Inference Latency (ms per frame: Preprocess + Inference + NMS)
  - Frames Per Second (FPS)

---

## 3. Results Summary Table

| Metric | Baseline YOLOv8n (Exp A) | Custom Gate YOLOv8n (Exp B) | Delta ($\Delta$) |
|---|---|---|---|
| Precision ($P$) | *Pending Colab run* | *Pending Colab run* | -- |
| Recall ($R$) | *Pending Colab run* | *Pending Colab run* | -- |
| $\text{mAP}@50$ | *Pending Colab run* | *Pending Colab run* | -- |
| $\text{mAP}@50\text{-}95$ | *Pending Colab run* | *Pending Colab run* | -- |
| Latency (ms/frame) | *Pending Colab run* | *Pending Colab run* | -- |
| Throughput (FPS) | *Pending Colab run* | *Pending Colab run* | -- |

---

## 4. Per-Class Analysis Framework

| Class Name | Baseline AP@50 | Custom AP@50 | Observations |
|---|---|---|---|
| Person | *Pending* | *Pending* | Evaluates pedestrian crossing, small scale at distance |
| Bicycle | *Pending* | *Pending* | Evaluates thin frames and rider occlusion |
| Car | *Pending* | *Pending* | Evaluates side/front angles under varied lighting |
| Motorcycle | *Pending* | *Pending* | Evaluates two-wheelers, helmet vs rider separation |
| Bus | *Pending* | *Pending* | Evaluates large vehicles spanning multi-lane gates |
| Truck | *Pending* | *Pending* | Evaluates maintenance/delivery vehicles |

---

## 5. Decision Criterion
The custom model will only be designated for production deployment if:
1. $\text{mAP}@50$ on the gate test set is $\ge 5\%$ higher than the baseline model, OR
2. False negatives on key classes (bicycles, motorcycles) are significantly reduced, AND
3. Inference latency remains $\le 40\text{ ms}$ ($\ge 25\text{ FPS}$).
Otherwise, the baseline `yolov8n` remains the production default.
