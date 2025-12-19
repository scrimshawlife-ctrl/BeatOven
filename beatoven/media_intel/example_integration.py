"""
Example: Media Intelligence + dsp.coffee Bridge Integration

Shows complete pipeline from image/video upload to hardware control.
"""

from typing import Literal
from beatoven.dspcoffee_bridge import (
    BridgeRuntime,
    PresetRegistry,
    UdpRealtimeLane,
    SerialOpsLane,
)
from beatoven.dspcoffee_bridge.example_preset_pack import PRESETS
from beatoven.media_intel import analyze_image, analyze_video, media_to_resonance


class MediaDrivenBridge:
    """
    Combines media analysis + dsp.coffee bridge.
    Upload image/video → analyze → select preset → control hardware.
    """

    def __init__(
        self,
        hardware_host: str = "192.168.1.50",
        hardware_udp_port: int = 9000,
        hardware_serial_port: str = "/dev/ttyACM0",
        hardware_baud: int = 115200,
    ):
        # Setup preset registry
        self.registry = PresetRegistry(PRESETS)

        # Setup transport lanes
        self.rt_lane = UdpRealtimeLane(host=hardware_host, port=hardware_udp_port)
        self.op_lane = SerialOpsLane(port=hardware_serial_port, baud=hardware_baud)

        # Setup bridge runtime
        self.bridge = BridgeRuntime(
            presets=self.registry,
            realtime_lane=self.rt_lane,
            ops_lane=self.op_lane,
            score_thresholds=(0.72, 0.88),
        )

    def handle_upload(
        self, path: str, kind: Literal["image", "video"], media_id: str
    ) -> dict:
        """
        Process uploaded media:
        1. Analyze (extract features + affect)
        2. Convert to ResonanceFrame
        3. Feed to bridge (preset selection + hardware control)

        Returns analysis summary for logging/debugging.
        """
        # Analyze
        if kind == "image":
            media_frame = analyze_image(path, media_id=media_id)
        elif kind == "video":
            media_frame = analyze_video(path, media_id=media_id, sample_fps=2.0, max_seconds=60.0)
        else:
            raise ValueError(f"Invalid kind: {kind}")

        # Convert to ResonanceFrame
        resonance_frame = media_to_resonance(media_frame)

        # Feed to bridge (triggers preset selection + hardware commands)
        self.bridge.on_frame(resonance_frame)

        # Return summary for logging
        summary = {
            "media_id": media_frame.media_id,
            "kind": media_frame.kind,
            "path": media_frame.path,
            "duration_s": media_frame.duration_s,
            "affect": media_frame.affect,
            "affect_confidence": media_frame.confidence.get("affect_confidence", 0.0),
            "perceived_era": media_frame.perceived_era,
            "era_confidence": media_frame.era_confidence,
            "resonance_metrics": {
                "complexity": resonance_frame.metrics.complexity,
                "emotional_intensity": resonance_frame.metrics.emotional_intensity,
                "groove": resonance_frame.metrics.groove,
                "energy": resonance_frame.metrics.energy,
                "density": resonance_frame.metrics.density,
                "swing": resonance_frame.metrics.swing,
                "brightness": resonance_frame.metrics.brightness,
                "tension": resonance_frame.metrics.tension,
            } if resonance_frame.metrics else None,
            "provenance_hash": resonance_frame.provenance_hash,
        }
        return summary


# Example usage
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: python example_integration.py <image|video> <path>")
        sys.exit(1)

    kind = sys.argv[1]
    path = sys.argv[2]

    # Initialize bridge
    bridge = MediaDrivenBridge(
        hardware_host="192.168.1.50",
        hardware_udp_port=9000,
        hardware_serial_port="/dev/ttyACM0",
    )

    # Process media
    try:
        summary = bridge.handle_upload(path, kind=kind, media_id=f"cli_{kind}_001")
        print(json.dumps(summary, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
