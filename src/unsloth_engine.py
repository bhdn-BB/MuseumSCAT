import os
from collections.abc import Sequence

import click
import pandas as pd
import torch
from tqdm.auto import tqdm
from transformers import AutoProcessor
from unsloth import FastModel

from system_prompts.public_baseline import SYSTEM_PROMPT
from utils import parse_prediction
from train_cfg.zero_shot_qwen import (
    MODEL_NAME,
    COLUMNS,
    MAX_NEW_TOKENS,
    MAX_VISUAL_TOKENS,
)


class UnslothOCREngine:

    def __init__(
            self,
            model_name: str = MODEL_NAME,
            columns: Sequence[str] = COLUMNS,
            max_new_tokens: int = MAX_NEW_TOKENS,
            max_visual_tokens: int = MAX_VISUAL_TOKENS,
    ) -> None:
        self.columns = list(columns)
        self.max_tokens = max_new_tokens

        self.model, _ = FastModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_visual_tokens,
            load_in_4bit=True,
            device_map={"": 0},
        )
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            min_pixels=512 * 512,
            max_pixels=1024 * 1536,
        )
        self.model.eval()

    @torch.inference_mode()
    def _extract(self, image_path: str) -> dict:
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": SYSTEM_PROMPT},
            ],
        }]
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)
        output = self.model.generate(
            **inputs,
            max_new_tokens=self.max_tokens,
            do_sample=False,
            use_cache=True,
        )
        generated = output[:, inputs["input_ids"].shape[1]:]
        text = self.processor.batch_decode(
            generated,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]
        return parse_prediction(text)

    def run_inference(self, df: pd.DataFrame, images_dir: str) -> pd.DataFrame:
        rows = []
        for image_file in tqdm(df["image_file"], total=len(df), desc="Zero-shot OCR"):
            prediction = self._extract(os.path.join(images_dir, image_file))
            rows.append({"image_file": image_file, **prediction})
        return pd.DataFrame(rows, columns=self.columns)


@click.command()
@click.option("--data-dir", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--output", default="submission.csv", show_default=True, type=click.Path())
@click.option("--model-name", default=MODEL_NAME, show_default=True)
@click.option("--smoke-rows", default=0, show_default=True, type=int)
def main(data_dir: str, output: str, model_name: str, smoke_rows: int) -> None:
    test = pd.read_csv(os.path.join(data_dir, "test.csv"))
    if smoke_rows > 0:
        test = test.head(smoke_rows)
    engine = UnslothOCREngine(model_name=model_name)
    submission = engine.run_inference(test, os.path.join(data_dir, "images"))
    submission.to_csv(output, index=False)
    click.echo(f"Saved {len(submission)} rows to {output}")


if __name__ == "__main__":
    main()
