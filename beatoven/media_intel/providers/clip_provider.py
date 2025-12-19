from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import MediaKind, ProviderStatus, SemanticProvider

@dataclass
class ClipProvider(SemanticProvider):
    """
    CLIP-based tags: scene/object vibes + time-era cues when possible.
    Requires: torch, transformers, pillow
    Model: openai/clip-vit-base-patch32 (downloads weights on first run)
    """
    name: str = "clip"

    def status(self) -> ProviderStatus:
        try:
            import torch  # noqa
            import transformers  # noqa
            import PIL  # noqa
            return ProviderStatus(name=self.name, available=True, version="clip-vit-b32")
        except Exception as e:
            return ProviderStatus(name=self.name, available=False, reason=str(e))

    def analyze(self, *, kind: MediaKind, path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if kind not in ("image", "video"):
            return {}
        import torch
        from PIL import Image
        from transformers import CLIPProcessor, CLIPModel
        import numpy as np
        import cv2

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
        proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Prompts tuned for music-control semantics (edit freely)
        prompts = [
            "a dark nightclub scene", "a bright sunny outdoor scene", "a tense dramatic scene",
            "a nostalgic vintage photo", "a futuristic cyberpunk scene", "a calm meditative scene",
            "a chaotic crowded scene", "an intimate portrait", "a lonely empty street at night",
            "a 1990s aesthetic", "a 2000s aesthetic", "a 2010s aesthetic", "a 2020s aesthetic",
        ]

        def score_image(img: Image.Image) -> Dict[str, float]:
            inputs = proc(text=prompts, images=img, return_tensors="pt", padding=True).to(device)
            with torch.no_grad():
                logits = model(**inputs).logits_per_image[0]
            probs = torch.softmax(logits, dim=0).detach().cpu().numpy()
            return {prompts[i]: float(probs[i]) for i in range(len(prompts))}

        if kind == "image":
            img = Image.open(path).convert("RGB")
            scores = score_image(img)
        else:
            # video: sample N frames
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return {}
            frames = []
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            picks = [int(total * r) for r in (0.2, 0.5, 0.8)] if total > 0 else [0, 30, 60]
            for idx in picks:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ok, bgr = cap.read()
                if ok and bgr is not None:
                    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(rgb))
            cap.release()
            if not frames:
                return {}
            agg: Dict[str, float] = {p: 0.0 for p in prompts}
            for f in frames:
                s = score_image(f)
                for k, v in s.items():
                    agg[k] += v
            scores = {k: v / len(frames) for k, v in agg.items()}

        # Extract "era" distribution if present
        era = {
            "1990s": scores.get("a 1990s aesthetic", 0.0),
            "2000s": scores.get("a 2000s aesthetic", 0.0),
            "2010s": scores.get("a 2010s aesthetic", 0.0),
            "2020s": scores.get("a 2020s aesthetic", 0.0),
        }
        s = sum(era.values())
        era = {k: (v / s if s > 1e-9 else 0.0) for k, v in era.items()}

        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:6]
        return {"top_tags": top, "era_dist": era, "raw": scores}
