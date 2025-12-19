from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import MediaKind, ProviderStatus, SemanticProvider

@dataclass
class ActionProvider(SemanticProvider):
    """
    Lightweight action cues for video using torchvision video models.
    Requires: torch, torchvision, opencv-python
    """
    name: str = "action"

    def status(self) -> ProviderStatus:
        try:
            import torch  # noqa
            import torchvision  # noqa
            import cv2  # noqa
            return ProviderStatus(name=self.name, available=True, version="torchvision-r3d18")
        except Exception as e:
            return ProviderStatus(name=self.name, available=False, reason=str(e))

    def analyze(self, *, kind: MediaKind, path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if kind != "video":
            return {}
        import torch
        import torchvision
        import cv2
        import numpy as np

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = torchvision.models.video.r3d_18(weights=torchvision.models.video.R3D_18_Weights.DEFAULT).to(device)
        model.eval()
        weights = torchvision.models.video.R3D_18_Weights.DEFAULT
        preprocess = weights.transforms()

        # sample 16 frames evenly
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return {}
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        idxs = [int(i) for i in np.linspace(0, max(0, total - 1), 16)] if total > 16 else list(range(16))
        frames = []
        for i in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, bgr = cap.read()
            if ok and bgr is not None:
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                frames.append(rgb)
        cap.release()
        if len(frames) < 8:
            return {}

        # shape to (T,H,W,C) uint8
        vid = np.stack(frames, axis=0).astype(np.uint8)
        # preprocess expects PIL or torch video; use torch conversion
        v = torch.from_numpy(vid).permute(3,0,1,2)  # C,T,H,W
        v = v.unsqueeze(0)  # N,C,T,H,W
        v = preprocess(v)
        v = v.to(device)

        with torch.no_grad():
            logits = model(v)[0]
            probs = torch.softmax(logits, dim=0).detach().cpu().numpy()

        cats = weights.meta["categories"]
        top = sorted([(cats[i], float(probs[i])) for i in range(len(cats))], key=lambda kv: kv[1], reverse=True)[:5]
        return {"top_actions": top}
