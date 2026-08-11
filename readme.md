## MuseumSCAT @ CVNH ECCV26

### Experiment Results

| Approach               | LB Score (AURC) |
|------------------------|----------------:|
| Qwen3-VL 2B, Zero-shot |           0.345 |

### Run inference

Runs zero-shot Qwen3-VL OCR and writes a Kaggle submission.

#### Visual token count

The approximate number of visual tokens is calculated from the resized image dimensions:

$$
N_{\text{visual}} \approx
\frac{H_{\text{resized}} \times W_{\text{resized}}}
{(\text{patch size} \times \text{merge size})^2}.
$$

For Qwen2/Qwen2.5-VL, the effective spatial patch is $14 \times 2 = 28$ pixels:

$$
N_{\text{visual}} \approx
\frac{H_{\text{resized}} \times W_{\text{resized}}}{28 \times 28}.
$$

Qwen3-VL uses a patch size of 16 and a merge size of 2, so for the model used here:

$$
N_{\text{visual}} \approx
\frac{H_{\text{resized}} \times W_{\text{resized}}}{32 \times 32}.
$$

This is the image-token count only. The model sequence length must also accommodate the text prompt and generated output tokens.

```bash
python src/unsloth_engine.py \
  --data-dir /kaggle/input/competitions/museumscat-specimen-collection-annotation-task \
  --output /kaggle/working/submission.csv \
  --smoke-rows 1
```

Remove `--smoke-rows 1` to process the full test set.
