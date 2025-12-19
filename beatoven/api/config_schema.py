"""
BeatOven Config Schema API

JSON schema generation for all configuration options.

UI uses this to dynamically generate controls that are always visible,
with disabled states and tooltips for unavailable features.

Schema-driven UI ensures all options are discoverable and self-documenting.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class FieldSchema(BaseModel):
    """Schema for a single configuration field."""
    field_id: str
    name: str
    description: str
    type: str  # "float", "int", "string", "enum", "boolean"
    default: Any
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    options: Optional[List[str]] = None  # For enum types
    unit: Optional[str] = None  # e.g., "Hz", "dB", "ms"
    category: str  # "drums", "harmony", "rhythm", etc.
    requires_feature: Optional[str] = None  # Feature ID from capabilities


class ConfigSchemaResponse(BaseModel):
    """Complete configuration schema."""
    version: str
    categories: List[str]
    fields: List[FieldSchema]


def get_config_schema() -> ConfigSchemaResponse:
    """
    Get complete configuration schema.

    Returns all configuration options across all modules,
    with metadata for UI generation.
    """
    fields = []

    # ==================== DRUMS CATEGORY ====================

    fields.append(FieldSchema(
        field_id="drums.rig_profile",
        name="Rig Profile",
        description="Equipment profile constraining percussion generation",
        type="enum",
        default="eurorack_dspcoffee_4voice",
        options=[
            "eurorack_dspcoffee_4voice",
            "midi_drum_machine_8ch",
            "minimal_cvgate_2voice",
            "audio_stems_16lane",
            "eurorack_dspcoffee_8voice",
            "buchla_cvgate_4voice",
            "custom"
        ],
        category="drums",
        requires_feature=None
    ))

    fields.append(FieldSchema(
        field_id="drums.density",
        name="Density",
        description="Overall drum event density (0 = sparse, 1 = dense)",
        type="float",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        category="drums"
    ))

    fields.append(FieldSchema(
        field_id="drums.syncopation",
        name="Syncopation",
        description="Off-beat emphasis (0 = on-beat, 1 = highly syncopated)",
        type="float",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        category="drums"
    ))

    fields.append(FieldSchema(
        field_id="drums.swing",
        name="Swing",
        description="Swing amount (0 = straight, 1 = shuffled)",
        type="float",
        default=0.0,
        min_value=0.0,
        max_value=1.0,
        category="drums"
    ))

    fields.append(FieldSchema(
        field_id="drums.fill_policy",
        name="Fill Policy",
        description="Drum fill intensity",
        type="enum",
        default="moderate",
        options=["none", "sparse", "moderate", "dense"],
        category="drums"
    ))

    fields.append(FieldSchema(
        field_id="drums.humanize",
        name="Humanize",
        description="Timing/velocity humanization (0 = robotic, 1 = loose)",
        type="float",
        default=0.0,
        min_value=0.0,
        max_value=1.0,
        category="drums"
    ))

    # ==================== RHYTHM CATEGORY ====================

    fields.append(FieldSchema(
        field_id="rhythm.tempo",
        name="Tempo",
        description="BPM (beats per minute)",
        type="float",
        default=120.0,
        min_value=40.0,
        max_value=300.0,
        unit="BPM",
        category="rhythm"
    ))

    fields.append(FieldSchema(
        field_id="rhythm.time_signature",
        name="Time Signature",
        description="Meter (numerator/denominator)",
        type="enum",
        default="4/4",
        options=["3/4", "4/4", "5/4", "6/8", "7/8", "9/8"],
        category="rhythm"
    ))

    fields.append(FieldSchema(
        field_id="rhythm.length_bars",
        name="Pattern Length",
        description="Length in bars",
        type="int",
        default=4,
        min_value=1,
        max_value=32,
        unit="bars",
        category="rhythm"
    ))

    # ==================== HARMONY CATEGORY ====================

    fields.append(FieldSchema(
        field_id="harmony.key_root",
        name="Key Root",
        description="Root note (MIDI number, 60 = Middle C)",
        type="int",
        default=60,
        min_value=0,
        max_value=127,
        category="harmony"
    ))

    fields.append(FieldSchema(
        field_id="harmony.scale",
        name="Scale",
        description="Harmonic scale",
        type="enum",
        default="MINOR",
        options=["MAJOR", "MINOR", "DORIAN", "PHRYGIAN", "LYDIAN", "MIXOLYDIAN", "LOCRIAN", "HARMONIC_MINOR", "MELODIC_MINOR"],
        category="harmony"
    ))

    fields.append(FieldSchema(
        field_id="harmony.resonance",
        name="Resonance",
        description="Harmonic richness and sustain (0 = dry, 1 = rich)",
        type="float",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        category="harmony"
    ))

    fields.append(FieldSchema(
        field_id="harmony.tension",
        name="Tension",
        description="Harmonic tension (0 = consonant, 1 = dissonant)",
        type="float",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        category="harmony"
    ))

    fields.append(FieldSchema(
        field_id="harmony.contrast",
        name="Contrast",
        description="Dynamic range variation (0 = static, 1 = dynamic)",
        type="float",
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        category="harmony"
    ))

    # ==================== HARDWARE CATEGORY ====================

    fields.append(FieldSchema(
        field_id="hardware.emit_target",
        name="Output Target",
        description="Hardware output type",
        type="enum",
        default="audio_stems",
        options=["dsp_coffee", "midi", "cv_gate", "audio_stems"],
        category="hardware"
    ))

    fields.append(FieldSchema(
        field_id="hardware.external_clock",
        name="External Clock",
        description="Use external clock sync",
        type="boolean",
        default=False,
        category="hardware",
        requires_feature="hardware.dspcoffee"
    ))

    fields.append(FieldSchema(
        field_id="hardware.external_reset",
        name="External Reset",
        description="Use external reset signal",
        type="boolean",
        default=False,
        category="hardware",
        requires_feature="hardware.dspcoffee"
    ))

    # ==================== MEDIA CATEGORY ====================

    fields.append(FieldSchema(
        field_id="media.enable_semantic",
        name="Enable Semantic Analysis",
        description="Use CLIP/Action/Audio providers for deeper analysis",
        type="boolean",
        default=False,
        category="media",
        requires_feature="media.semantic.clip"
    ))

    fields.append(FieldSchema(
        field_id="media.era_inference",
        name="Era Inference",
        description="Automatically detect aesthetic era from media",
        type="boolean",
        default=True,
        category="media",
        requires_feature="media.basic"
    ))

    # ==================== FX CATEGORY ====================

    fields.append(FieldSchema(
        field_id="fx.binaural.enabled",
        name="Binaural Beats",
        description="Enable binaural beat injection",
        type="boolean",
        default=False,
        category="fx"
    ))

    fields.append(FieldSchema(
        field_id="fx.binaural.carrier_hz",
        name="Binaural Carrier Frequency",
        description="Carrier frequency for binaural beats",
        type="float",
        default=200.0,
        min_value=80.0,
        max_value=1000.0,
        unit="Hz",
        category="fx",
        requires_feature="fx.binaural"
    ))

    fields.append(FieldSchema(
        field_id="fx.binaural.beat_hz",
        name="Binaural Beat Frequency",
        description="Beat frequency (brain entrainment)",
        type="float",
        default=6.0,
        min_value=0.5,
        max_value=40.0,
        unit="Hz",
        category="fx",
        requires_feature="fx.binaural"
    ))

    # Collect categories
    categories = sorted(list(set(f.category for f in fields)))

    return ConfigSchemaResponse(
        version="1.0.0",
        categories=categories,
        fields=fields
    )


__all__ = ["get_config_schema", "ConfigSchemaResponse", "FieldSchema"]
