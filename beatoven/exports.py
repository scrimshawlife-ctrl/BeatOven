# BeatOven — Explicit Function Exports (Canonical)
# Includes BOTH overlay ops and metrics as discoverable Function Descriptors.

EXPORTS = [
  # ----------------------------
  # OP: Generate Track
  # ----------------------------
  {
    "id": "beatoven.op.generate_track.v1",
    "name": "Generate Track",
    "kind": "overlay_op",
    "version": "1.0.0",
    "owner": "beatoven",
    "rune": "ᛒᛖᚨᛏ",
    "entrypoint": "beatoven.logic:generate_track",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "mood": {"type": "string"},
        "tempo": {"type": "number"},
        "duration_sec": {"type": "number"},
        "seed": {"type": "integer"}
      },
      "required": ["mood"],
      "additionalProperties": True
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "audio_path": {"type": "string"},
        "metadata": {"type": "object"}
      },
      "required": ["audio_path"]
    },
    "capabilities": ["cpu", "disk_write"],
    "cost_hint": {"ms_p50": 200, "ms_p95": 800},
    "provenance": {
      "repo": "beatoven",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  },

  # ----------------------------
  # METRIC: Groove Stability Index (GSI)
  # Measures rhythmic timing stability (0..1)
  # ----------------------------
  {
    "id": "beatoven.metric.gsi.v1",
    "name": "Groove Stability Index",
    "kind": "metric",
    "version": "1.0.0",
    "owner": "beatoven",
    "rune": "ᚷᛊᛁ",
    "entrypoint": "beatoven.metrics:compute_gsi",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "onsets_ms": {"type": "array", "items": {"type": "number"}},
        "grid_ms": {"type": "number"}
      },
      "required": ["onsets_ms", "grid_ms"],
      "additionalProperties": False
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "gsi": {"type": "number"},
        "timing_error_ms_mean": {"type": "number"},
        "timing_error_ms_p95": {"type": "number"}
      },
      "required": ["gsi"]
    },
    "capabilities": ["cpu", "no_net", "read_only"],
    "cost_hint": {"ms_p50": 2, "ms_p95": 8},
    "provenance": {
      "repo": "beatoven",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  },

  # ----------------------------
  # METRIC: Spectral Warmth Ratio (SWR)
  # Low-mid energy / high energy (proxy for "warmth")
  # ----------------------------
  {
    "id": "beatoven.metric.swr.v1",
    "name": "Spectral Warmth Ratio",
    "kind": "metric",
    "version": "1.0.0",
    "owner": "beatoven",
    "rune": "ᛊᚹᚱ",
    "entrypoint": "beatoven.metrics:compute_swr",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "band_energy": {
          "type": "object",
          "properties": {
            "low_mid": {"type": "number"},
            "high": {"type": "number"}
          },
          "required": ["low_mid", "high"],
          "additionalProperties": False
        }
      },
      "required": ["band_energy"],
      "additionalProperties": False
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "swr": {"type": "number"}
      },
      "required": ["swr"]
    },
    "capabilities": ["cpu", "no_net", "read_only"],
    "cost_hint": {"ms_p50": 1, "ms_p95": 3},
    "provenance": {
      "repo": "beatoven",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  },

  # ----------------------------
  # METRIC: Dynamic Range Score (DRS)
  # 1 - (rms / peak) normalized-ish proxy (0..1)
  # ----------------------------
  {
    "id": "beatoven.metric.drs.v1",
    "name": "Dynamic Range Score",
    "kind": "metric",
    "version": "1.0.0",
    "owner": "beatoven",
    "rune": "ᛞᚱᛊ",
    "entrypoint": "beatoven.metrics:compute_drs",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "rms": {"type": "number"},
        "peak": {"type": "number"}
      },
      "required": ["rms", "peak"],
      "additionalProperties": False
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "drs": {"type": "number"}
      },
      "required": ["drs"]
    },
    "capabilities": ["cpu", "no_net", "read_only"],
    "cost_hint": {"ms_p50": 1, "ms_p95": 3},
    "provenance": {
      "repo": "beatoven",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  },

  # ----------------------------
  # METRIC: Archetype Fit Score (AFS)
  # Compares intended archetype → produced feature vector similarity (0..1)
  # ----------------------------
  {
    "id": "beatoven.metric.afs.v1",
    "name": "Archetype Fit Score",
    "kind": "metric",
    "version": "1.0.0",
    "owner": "beatoven",
    "rune": "ᚨᚠᛊ",
    "entrypoint": "beatoven.metrics:compute_afs",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "intent_vector": {"type": "array", "items": {"type": "number"}},
        "audio_vector": {"type": "array", "items": {"type": "number"}}
      },
      "required": ["intent_vector", "audio_vector"],
      "additionalProperties": False
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "afs": {"type": "number"}
      },
      "required": ["afs"]
    },
    "capabilities": ["cpu", "no_net", "read_only"],
    "cost_hint": {"ms_p50": 3, "ms_p95": 12},
    "provenance": {
      "repo": "beatoven",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  }
]
