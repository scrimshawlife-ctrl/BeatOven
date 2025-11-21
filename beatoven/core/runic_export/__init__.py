"""
BeatOven Runic-Visual Exporter

Generates deterministic runic signature images reflecting
spectral, symbolic, and emotional vectors.
"""

import hashlib
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class RunicGlyph:
    """A single runic glyph element."""
    x: float
    y: float
    size: float
    rotation: float
    glyph_type: int  # 0-15 for different rune shapes
    intensity: float
    color: Tuple[int, int, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "rotation": self.rotation,
            "glyph_type": self.glyph_type,
            "intensity": self.intensity,
            "color": list(self.color)
        }


@dataclass
class RunicSignature:
    """Complete runic visual signature."""
    width: int
    height: int
    glyphs: List[RunicGlyph] = field(default_factory=list)
    background_color: Tuple[int, int, int] = (0, 0, 0)
    border_pattern: List[int] = field(default_factory=list)
    spectral_ring: np.ndarray = field(default_factory=lambda: np.zeros(64))
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "glyphs": [g.to_dict() for g in self.glyphs],
            "background_color": list(self.background_color),
            "border_pattern": self.border_pattern,
            "spectral_ring": self.spectral_ring.tolist(),
            "provenance_hash": self.provenance_hash
        }


class RunicVisualExporter:
    """
    Generates deterministic runic visual signatures from audio analysis.

    Maps spectral, symbolic, and emotional vectors to visual elements
    for unique identification and artistic representation.
    """

    # Runic color palettes based on emotional valence
    PALETTES = {
        "positive": [
            (255, 215, 0),   # Gold
            (255, 165, 0),   # Orange
            (255, 255, 224), # Light yellow
            (152, 251, 152), # Pale green
        ],
        "neutral": [
            (192, 192, 192), # Silver
            (176, 196, 222), # Light steel blue
            (230, 230, 250), # Lavender
            (245, 245, 245), # White smoke
        ],
        "negative": [
            (138, 43, 226),  # Blue violet
            (75, 0, 130),    # Indigo
            (25, 25, 112),   # Midnight blue
            (47, 79, 79),    # Dark slate gray
        ],
        "energetic": [
            (255, 0, 0),     # Red
            (255, 69, 0),    # Orange red
            (255, 140, 0),   # Dark orange
            (255, 215, 0),   # Gold
        ]
    }

    # Rune shape definitions (as normalized point sequences)
    RUNE_SHAPES = [
        [(0.5, 0), (0.5, 1)],  # Vertical line
        [(0, 0.5), (1, 0.5)],  # Horizontal line
        [(0, 0), (1, 1)],      # Diagonal
        [(1, 0), (0, 1)],      # Anti-diagonal
        [(0.5, 0), (0, 1), (1, 1)],  # Triangle down
        [(0.5, 1), (0, 0), (1, 0)],  # Triangle up
        [(0, 0), (0.5, 0.5), (0, 1)],  # Left angle
        [(1, 0), (0.5, 0.5), (1, 1)],  # Right angle
        [(0.5, 0), (0.5, 0.4), (0, 0.7), (0.5, 1), (1, 0.7), (0.5, 0.4)],  # Diamond
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],  # Square
        [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5), (0.5, 0)],  # Rotated square
        [(0.25, 0), (0.75, 0), (1, 0.5), (0.75, 1), (0.25, 1), (0, 0.5)],  # Hexagon
        [(0.5, 0), (0.5, 0.3), (0, 0.5), (0.5, 0.7), (0.5, 1)],  # Y shape
        [(0, 0), (0.5, 0.5), (1, 0), (0.5, 1)],  # Arrow
        [(0.5, 0), (0, 0.5), (0.5, 0.5), (1, 0.5), (0.5, 1)],  # Cross
        [(0.3, 0), (0.7, 0), (0.7, 0.4), (1, 0.5), (0.7, 0.6), (0.7, 1), (0.3, 1), (0.3, 0.6), (0, 0.5), (0.3, 0.4)],  # Complex
    ]

    def __init__(self, seed: int = 0, width: int = 512, height: int = 512):
        """
        Initialize exporter.

        Args:
            seed: Deterministic seed
            width: Output image width
            height: Output image height
        """
        self.seed = seed
        self.width = width
        self.height = height
        self._rng = np.random.default_rng(seed)

    def generate(
        self,
        spectral_vector: Optional[np.ndarray] = None,
        symbolic_vector: Optional[np.ndarray] = None,
        emotional_vector: Optional[np.ndarray] = None,
        rune_vector: Optional[np.ndarray] = None
    ) -> RunicSignature:
        """
        Generate runic signature from vectors.

        Args:
            spectral_vector: Spectral analysis features
            symbolic_vector: ABX-Runes symbolic fields
            emotional_vector: PsyFi emotional state
            rune_vector: Raw rune seed vector

        Returns:
            RunicSignature containing visual elements
        """
        # Combine all vectors
        combined = self._combine_vectors(
            spectral_vector, symbolic_vector, emotional_vector, rune_vector
        )

        # Determine palette from emotional vector
        palette = self._select_palette(emotional_vector)

        # Generate glyphs
        glyphs = self._generate_glyphs(combined, palette)

        # Generate spectral ring
        spectral_ring = self._generate_spectral_ring(spectral_vector)

        # Generate border pattern
        border = self._generate_border(rune_vector)

        # Compute provenance
        provenance = self._compute_provenance(
            spectral_vector, symbolic_vector, emotional_vector, rune_vector
        )

        return RunicSignature(
            width=self.width,
            height=self.height,
            glyphs=glyphs,
            background_color=self._background_from_palette(palette),
            border_pattern=border,
            spectral_ring=spectral_ring,
            provenance_hash=provenance
        )

    def render_to_array(self, signature: RunicSignature) -> np.ndarray:
        """
        Render signature to numpy array (RGB).

        Args:
            signature: Runic signature to render

        Returns:
            RGB image as numpy array (height, width, 3)
        """
        # Create canvas
        canvas = np.zeros((signature.height, signature.width, 3), dtype=np.uint8)

        # Fill background
        canvas[:, :] = signature.background_color

        # Draw spectral ring
        self._draw_spectral_ring(canvas, signature.spectral_ring)

        # Draw border
        self._draw_border(canvas, signature.border_pattern)

        # Draw glyphs
        for glyph in signature.glyphs:
            self._draw_glyph(canvas, glyph)

        return canvas

    def export_svg(self, signature: RunicSignature) -> str:
        """
        Export signature as SVG string.

        Args:
            signature: Runic signature to export

        Returns:
            SVG document as string
        """
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{signature.width}" height="{signature.height}">'
        ]

        # Background
        bg = signature.background_color
        svg_parts.append(
            f'<rect width="100%" height="100%" fill="rgb({bg[0]},{bg[1]},{bg[2]})"/>'
        )

        # Spectral ring
        cx, cy = signature.width // 2, signature.height // 2
        for i, value in enumerate(signature.spectral_ring):
            angle = i * 2 * math.pi / len(signature.spectral_ring)
            r = 100 + value * 50
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            intensity = int(128 + value * 127)
            svg_parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" '
                f'fill="rgb({intensity},{intensity},{intensity})"/>'
            )

        # Glyphs
        for glyph in signature.glyphs:
            svg_parts.append(self._glyph_to_svg(glyph))

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def _combine_vectors(
        self,
        spectral: Optional[np.ndarray],
        symbolic: Optional[np.ndarray],
        emotional: Optional[np.ndarray],
        rune: Optional[np.ndarray]
    ) -> np.ndarray:
        """Combine all input vectors into unified representation."""
        vectors = []

        if spectral is not None:
            vectors.append(spectral.flatten()[:32])
        if symbolic is not None:
            vectors.append(symbolic.flatten()[:32])
        if emotional is not None:
            vectors.append(emotional.flatten()[:8])
        if rune is not None:
            vectors.append(rune.flatten()[:64])

        if not vectors:
            # Generate from seed
            return self._rng.uniform(-1, 1, 64).astype(np.float32)

        # Pad and concatenate
        padded = []
        for v in vectors:
            if len(v) < 32:
                v = np.pad(v, (0, 32 - len(v)))
            padded.append(v[:32])

        return np.concatenate(padded).astype(np.float32)

    def _select_palette(self, emotional: Optional[np.ndarray]) -> List[Tuple[int, int, int]]:
        """Select color palette based on emotional vector."""
        if emotional is None or len(emotional) < 2:
            return self.PALETTES["neutral"]

        valence = emotional[0] if len(emotional) > 0 else 0
        arousal = emotional[1] if len(emotional) > 1 else 0

        if arousal > 0.5:
            return self.PALETTES["energetic"]
        elif valence > 0.3:
            return self.PALETTES["positive"]
        elif valence < -0.3:
            return self.PALETTES["negative"]
        else:
            return self.PALETTES["neutral"]

    def _generate_glyphs(
        self,
        combined: np.ndarray,
        palette: List[Tuple[int, int, int]]
    ) -> List[RunicGlyph]:
        """Generate glyph elements from combined vector."""
        glyphs = []

        # Determine number of glyphs from vector energy
        n_glyphs = 12 + int(abs(np.mean(combined)) * 12)

        for i in range(n_glyphs):
            # Position from vector values
            idx = i % len(combined)
            x_val = combined[idx]
            y_val = combined[(idx + 1) % len(combined)]

            x = (x_val + 1) / 2 * (self.width - 100) + 50
            y = (y_val + 1) / 2 * (self.height - 100) + 50

            # Size and rotation from vector
            size = 20 + abs(combined[(idx + 2) % len(combined)]) * 40
            rotation = combined[(idx + 3) % len(combined)] * math.pi

            # Glyph type
            glyph_type = int(abs(combined[(idx + 4) % len(combined)]) * 15) % 16

            # Intensity
            intensity = 0.5 + abs(combined[(idx + 5) % len(combined)]) * 0.5

            # Color from palette
            color_idx = int(abs(combined[(idx + 6) % len(combined)]) * (len(palette) - 1))
            color = palette[color_idx % len(palette)]

            glyphs.append(RunicGlyph(
                x=float(x),
                y=float(y),
                size=float(size),
                rotation=float(rotation),
                glyph_type=glyph_type,
                intensity=float(intensity),
                color=color
            ))

        return glyphs

    def _generate_spectral_ring(self, spectral: Optional[np.ndarray]) -> np.ndarray:
        """Generate spectral ring data."""
        if spectral is None:
            return self._rng.uniform(0, 1, 64).astype(np.float32)

        # Resample to 64 points
        if len(spectral) >= 64:
            ring = spectral[:64]
        else:
            ring = np.interp(
                np.linspace(0, len(spectral) - 1, 64),
                np.arange(len(spectral)),
                spectral
            )

        # Normalize
        ring = (ring - ring.min()) / (ring.max() - ring.min() + 1e-10)
        return ring.astype(np.float32)

    def _generate_border(self, rune: Optional[np.ndarray]) -> List[int]:
        """Generate border pattern from rune vector."""
        if rune is None:
            return [int(x) for x in self._rng.integers(0, 4, 32)]

        # Map rune values to pattern indices
        border = []
        for i in range(32):
            val = rune[i % len(rune)]
            pattern = int((val + 1) / 2 * 4) % 4
            border.append(pattern)

        return border

    def _background_from_palette(self, palette: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
        """Generate dark background from palette."""
        if not palette:
            return (16, 16, 24)

        # Average and darken
        avg = [sum(c[i] for c in palette) // len(palette) for i in range(3)]
        return (avg[0] // 8, avg[1] // 8, avg[2] // 8)

    def _draw_spectral_ring(self, canvas: np.ndarray, ring: np.ndarray):
        """Draw spectral ring on canvas."""
        h, w = canvas.shape[:2]
        cx, cy = w // 2, h // 2
        base_radius = min(w, h) // 4

        for i, value in enumerate(ring):
            angle = i * 2 * math.pi / len(ring)
            r = base_radius + int(value * base_radius * 0.5)

            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle))

            if 0 <= x < w and 0 <= y < h:
                intensity = int(128 + value * 127)
                canvas[y, x] = [intensity, intensity, int(intensity * 0.8)]

    def _draw_border(self, canvas: np.ndarray, pattern: List[int]):
        """Draw border pattern on canvas."""
        h, w = canvas.shape[:2]
        border_width = 8

        for i, p in enumerate(pattern):
            segment_len = w // len(pattern)
            start_x = i * segment_len

            color = [(p + 1) * 50, (p + 2) * 40, (p + 1) * 60]

            # Top border
            canvas[:border_width, start_x:start_x + segment_len] = color
            # Bottom border
            canvas[-border_width:, start_x:start_x + segment_len] = color

    def _draw_glyph(self, canvas: np.ndarray, glyph: RunicGlyph):
        """Draw a single glyph on canvas."""
        shape = self.RUNE_SHAPES[glyph.glyph_type % len(self.RUNE_SHAPES)]
        h, w = canvas.shape[:2]

        # Transform points
        cos_r = math.cos(glyph.rotation)
        sin_r = math.sin(glyph.rotation)

        for i in range(len(shape) - 1):
            p1 = shape[i]
            p2 = shape[i + 1]

            # Scale and rotate
            x1 = (p1[0] - 0.5) * glyph.size
            y1 = (p1[1] - 0.5) * glyph.size
            x2 = (p2[0] - 0.5) * glyph.size
            y2 = (p2[1] - 0.5) * glyph.size

            rx1 = x1 * cos_r - y1 * sin_r + glyph.x
            ry1 = x1 * sin_r + y1 * cos_r + glyph.y
            rx2 = x2 * cos_r - y2 * sin_r + glyph.x
            ry2 = x2 * sin_r + y2 * cos_r + glyph.y

            # Draw line (simple Bresenham)
            self._draw_line(canvas, int(rx1), int(ry1), int(rx2), int(ry2),
                           glyph.color, glyph.intensity)

    def _draw_line(
        self,
        canvas: np.ndarray,
        x1: int, y1: int,
        x2: int, y2: int,
        color: Tuple[int, int, int],
        intensity: float
    ):
        """Draw line using Bresenham's algorithm."""
        h, w = canvas.shape[:2]

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1

        while True:
            if 0 <= x < w and 0 <= y < h:
                for c in range(3):
                    canvas[y, x, c] = int(color[c] * intensity)

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def _glyph_to_svg(self, glyph: RunicGlyph) -> str:
        """Convert glyph to SVG path element."""
        shape = self.RUNE_SHAPES[glyph.glyph_type % len(self.RUNE_SHAPES)]

        cos_r = math.cos(glyph.rotation)
        sin_r = math.sin(glyph.rotation)

        points = []
        for p in shape:
            x = (p[0] - 0.5) * glyph.size
            y = (p[1] - 0.5) * glyph.size
            rx = x * cos_r - y * sin_r + glyph.x
            ry = x * sin_r + y * cos_r + glyph.y
            points.append(f"{rx:.1f},{ry:.1f}")

        path_d = "M " + " L ".join(points)
        color = glyph.color
        opacity = glyph.intensity

        return (
            f'<path d="{path_d}" stroke="rgb({color[0]},{color[1]},{color[2]})" '
            f'stroke-width="2" fill="none" opacity="{opacity:.2f}"/>'
        )

    def _compute_provenance(
        self,
        spectral: Optional[np.ndarray],
        symbolic: Optional[np.ndarray],
        emotional: Optional[np.ndarray],
        rune: Optional[np.ndarray]
    ) -> str:
        """Compute provenance hash."""
        data = []
        if spectral is not None:
            data.append(spectral.tobytes())
        if symbolic is not None:
            data.append(symbolic.tobytes())
        if emotional is not None:
            data.append(emotional.tobytes())
        if rune is not None:
            data.append(rune.tobytes())

        combined = b''.join(data) if data else b'default'
        return hashlib.sha256(combined).hexdigest()


__all__ = [
    "RunicVisualExporter", "RunicSignature", "RunicGlyph"
]
