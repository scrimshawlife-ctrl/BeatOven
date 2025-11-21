# BeatOven iOS Integration

## Overview

BeatOvenKit provides native iOS integration for the BeatOven generative music engine. It supports on-device inference using ONNX Runtime Mobile with full SEED-chain determinism and compute tracking.

## Requirements

- iOS 14.0+
- Xcode 13.0+
- Swift 5.5+

## Installation

### Swift Package Manager

```swift
dependencies: [
    .package(url: "https://github.com/appliedalchemy/beatoven-ios", from: "1.0.0")
]
```

### Manual

Copy `BeatOvenKit.swift` to your project and add the CommonCrypto framework.

## Quick Start

```swift
import BeatOvenKit

// Initialize engine
let engine = BeatOvenEngine.shared
try engine.initialize()

// Create generation request
let request = GenerationRequest(
    textIntent: "dark ambient pad with subtle rhythm",
    moodTags: [
        MoodTag(name: "dark", intensity: 0.8),
        MoodTag(name: "ambient", intensity: 0.9)
    ],
    seed: "my_creative_seed",
    tempo: 90.0,
    duration: 16.0,
    fields: ABXRunesFields(
        resonance: 0.7,
        density: 0.4,
        drift: 0.5,
        tension: 0.3,
        contrast: 0.5
    )
)

// Generate
Task {
    let result = try await engine.generate(request: request)
    print("Job ID: \(result.jobId)")
    print("Provenance: \(result.provenanceHash)")
    print("Stems: \(result.stems.keys)")
}
```

## Seed Lineage

BeatOvenKit maintains SEED-chain determinism:

```swift
// Initialize lineage
let lineage = engine.initSeedLineage(baseSeed: 12345)

// Seeds are automatically derived for each module
// Same seed + same inputs = identical output
```

## Exporting Audio

```swift
// Export stem to WAV
if let drumsData = result.stems["drums"] {
    let url = FileManager.default.temporaryDirectory.appendingPathComponent("drums.wav")
    try AudioExporter.exportToWAV(data: drumsData, to: url)
}
```

## Loading Patches

```swift
// Load from bundle
let patch = try PatchLoader.load(fromBundle: "my_patch")

// Load from URL
let patch = try PatchLoader.load(from: patchURL)
```

## Compute Tracking

```swift
// Get compute summary
let summary = engine.getComputeSummary()
print("Total runtime: \(summary["totalRuntimeMs"]!)ms")
```

## Low Memory Mode

For devices with limited RAM:

```swift
// Configure for low memory
let request = GenerationRequest(
    textIntent: "simple beat",
    duration: 8.0,  // Shorter duration
    fields: ABXRunesFields(density: 0.3)  // Lower complexity
)
```

## CPU-Only Mode

BeatOvenKit runs entirely on CPU by default. For Neural Engine acceleration on supported devices, use the CoreML backend (requires additional setup).

## Thread Safety

`BeatOvenEngine.shared` is thread-safe. Generation operations run asynchronously.

## Provenance

Every generation includes:
- `provenanceHash`: SHA-256 of inputs
- `seedLineage`: Full seed chain hash
- `computeTimeMs`: Generation time

## ABX-Runes Fields

| Field | Range | Description |
|-------|-------|-------------|
| resonance | 0-1 | Harmonic richness |
| density | 0-1 | Event complexity |
| drift | 0-1 | Temporal evolution |
| tension | 0-1 | Harmonic tension |
| contrast | 0-1 | Dynamic range |

## Error Handling

```swift
do {
    let result = try await engine.generate(request: request)
} catch BeatOvenError.notInitialized {
    print("Engine not initialized")
} catch BeatOvenError.generationFailed {
    print("Generation failed")
}
```

## License

Apache 2.0 - See main repository LICENSE file.
