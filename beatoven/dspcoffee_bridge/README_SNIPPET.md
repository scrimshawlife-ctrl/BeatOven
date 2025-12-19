# BeatOven ↔ dsp.coffee Bridge

## How to wire into BeatOven:

### 1. Add dependencies

```bash
pip install pyserial cbor2
```

### 2. Instantiate runtime somewhere in BeatOven service layer

```python
from beatoven.dspcoffee_bridge import (
    BridgeRuntime, PresetRegistry, UdpRealtimeLane, SerialOpsLane
)
from beatoven.dspcoffee_bridge.example_preset_pack import PRESETS

registry = PresetRegistry(PRESETS)
rt_lane = UdpRealtimeLane(host="192.168.1.50", port=9000)     # dsp.coffee UDP listener
op_lane = SerialOpsLane(port="/dev/ttyACM0", baud=115200)      # dsp.coffee USB serial

bridge = BridgeRuntime(
    presets=registry,
    realtime_lane=rt_lane,
    ops_lane=op_lane,
    score_thresholds=(0.72, 0.88),
)
```

### 3. Feed frames

```python
# For structured inputs:
bridge.on_frame(ResonanceFrame.new(
    source="abraxas_struct",
    genre="techno",
    subgenre="dark",
    metrics=ResonanceMetrics(...),
    rhythm=RhythmTokens(...),
))

# For live stream deltas:
bridge.on_delta(FrameDelta(
    ts_ms=...,
    metrics=ResonanceMetrics(...),
))
```

## What you just got

This bridge provides the right "add to BeatOven" slice:

- A BeatOven-side bridge that unifies Abraxas live + structured into ResonanceFrame
- A deterministic PresetBank selection + action chooser
- A working two-lane transport to dsp.coffee (UDP realtime + serial ops with ACK)
- Tests for the scoring spine

## Next steps

For the dsp.coffee firmware counterparts, you'll want:

1. UDP parser for /macro + /meta messages
2. Serial CBOR frame reader + ACK writer
3. Macro table + safe scene switching + pattern commit handler

When you're ready, the Daisy/C++ side can be added in the same "no-mystery" style.
