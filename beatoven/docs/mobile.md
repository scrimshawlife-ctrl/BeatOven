# BeatOven Mobile Integration

## Overview

BeatOven provides native mobile libraries for iOS and Android, enabling on-device generative music with full SEED-chain determinism, compute tracking, and provenance.

## Architecture

```
┌─────────────────────────────────────────┐
│           Mobile Application            │
├─────────────────────────────────────────┤
│    BeatOvenKit (iOS) / Mobile (Android) │
├─────────────────────────────────────────┤
│         Inference Engine (ONNX)         │
├─────────────────────────────────────────┤
│            Audio Rendering              │
├─────────────────────────────────────────┤
│        Platform Audio Services          │
│    (AVFoundation / Android Audio)       │
└─────────────────────────────────────────┘
```

## Supported Platforms

| Platform | Minimum Version | Language |
|----------|-----------------|----------|
| iOS | 14.0+ | Swift 5.5+ |
| Android | API 21+ | Java 8+ / Kotlin |

## Quick Start

### iOS

```swift
import BeatOvenKit

let engine = BeatOvenEngine.shared
try engine.initialize()

let request = GenerationRequest(
    textIntent: "ambient pad",
    seed: "my_seed",
    duration: 16.0
)

let result = try await engine.generate(request: request)
```

### Android

```java
BeatOvenMobile engine = BeatOvenMobile.getInstance();
engine.initialize(context);

GenerationRequest request = new GenerationRequest();
request.textIntent = "ambient pad";
request.seed = "my_seed";
request.duration = 16.0f;

engine.generate(request, callback);
```

## On-Device Inference

### ONNX Runtime Mobile

BeatOven uses ONNX Runtime Mobile for cross-platform inference:

1. **Model Conversion**: Convert PyTorch/JAX models to ONNX format
2. **Optimization**: Apply mobile-specific optimizations
3. **Quantization**: INT8 quantization for smaller models
4. **Execution**: CPU or GPU (where available)

### Model Files

Place model files in:
- iOS: `Resources/Models/`
- Android: `assets/models/`

Required models:
- `input_encoder.onnx` (2 MB)
- `symbolic_translator.onnx` (1 MB)
- `rhythm_generator.onnx` (5 MB)
- `harmonic_generator.onnx` (5 MB)
- `timbre_synth.onnx` (10 MB)

## SEED-Chain Determinism

Mobile libraries maintain full seed lineage:

```
base_seed → input_hash → rhythm_seed → harmony_seed → ...
```

### Initialization

```swift
// iOS
let lineage = engine.initSeedLineage(baseSeed: 12345)
```

```java
// Android
SeedLineage lineage = engine.initSeedLineage(12345L);
```

### Verification

Same seed + same inputs = identical output across:
- iOS and Android
- Multiple runs
- Different devices

## Compute-Cost Tracking

Every operation logs:
- Runtime (ms)
- Memory usage (bytes)
- Device type
- Seed lineage hash

```swift
// iOS
let summary = engine.getComputeSummary()
print("Runtime: \(summary["totalRuntimeMs"]!)ms")
```

```java
// Android
Map<String, Object> summary = engine.getComputeSummary();
Log.d("BeatOven", "Runtime: " + summary.get("totalRuntimeMs") + "ms");
```

## Audio Export

### WAV Export

```swift
// iOS
try AudioExporter.exportToWAV(data: stemData, to: fileURL)
```

```java
// Android
BeatOvenMobile.exportToWAV(stemData, outputFile);
```

### Share to Files App (iOS)

```swift
let activityVC = UIActivityViewController(
    activityItems: [fileURL],
    applicationActivities: nil
)
present(activityVC, animated: true)
```

### Share Intent (Android)

```java
Intent shareIntent = new Intent(Intent.ACTION_SEND);
shareIntent.setType("audio/wav");
shareIntent.putExtra(Intent.EXTRA_STREAM, fileUri);
startActivity(Intent.createChooser(shareIntent, "Share audio"));
```

## Patch Loading

```swift
// iOS - from bundle
let patch = try PatchLoader.load(fromBundle: "my_patch")
```

```java
// Android - from assets
InputStream is = context.getAssets().open("patches/my_patch.json");
// Parse JSON...
```

## Memory Management

### Low Memory Mode

For devices with < 3GB RAM:

```swift
// iOS
let request = GenerationRequest(
    textIntent: "simple beat",
    duration: 8.0,  // Shorter
    fields: ABXRunesFields(density: 0.3)  // Simpler
)
```

### Memory Warnings (iOS)

```swift
NotificationCenter.default.addObserver(
    forName: UIApplication.didReceiveMemoryWarningNotification,
    object: nil,
    queue: .main
) { _ in
    // Reduce generation complexity
}
```

### Memory Pressure (Android)

```java
@Override
public void onTrimMemory(int level) {
    if (level >= TRIM_MEMORY_MODERATE) {
        // Reduce generation complexity
    }
}
```

## CPU-Only Mode

Both libraries default to CPU inference. This ensures:
- Universal device compatibility
- Consistent behavior
- Predictable performance

### GPU Acceleration (Optional)

iOS (CoreML backend):
```swift
// Requires additional CoreML model conversion
```

Android (NNAPI):
```java
// Requires NNAPI delegate setup
```

## Background Processing

### iOS

```swift
let taskId = UIApplication.shared.beginBackgroundTask {
    // Cleanup
}

Task {
    let result = try await engine.generate(request: request)
    UIApplication.shared.endBackgroundTask(taskId)
}
```

### Android

```java
ExecutorService executor = Executors.newSingleThreadExecutor();
executor.execute(() -> {
    GenerationResult result = engine.generateSync(request);
    // Handle result on main thread
});
```

## Offline Support

All generation happens on-device:
- No network required
- No data leaves device
- Full privacy

## File Storage

### iOS

```swift
let documentsURL = FileManager.default.urls(
    for: .documentDirectory,
    in: .userDomainMask
).first!
let stemURL = documentsURL.appendingPathComponent("stem.wav")
```

### Android

```java
File outputDir = context.getExternalFilesDir(Environment.DIRECTORY_MUSIC);
File stemFile = new File(outputDir, "stem.wav");
```

## Testing

### Unit Tests

```swift
// iOS
func testDeterminism() async throws {
    let request = GenerationRequest(textIntent: "test", seed: "seed123")
    let result1 = try await engine.generate(request: request)
    let result2 = try await engine.generate(request: request)
    XCTAssertEqual(result1.provenanceHash, result2.provenanceHash)
}
```

```java
// Android
@Test
public void testDeterminism() throws Exception {
    GenerationRequest request = new GenerationRequest();
    request.textIntent = "test";
    request.seed = "seed123";

    GenerationResult result1 = engine.generateSync(request);
    GenerationResult result2 = engine.generateSync(request);

    assertEquals(result1.provenanceHash, result2.provenanceHash);
}
```

### Mock Compile Check

For CI/CD validation of mobile builds:

```bash
# iOS
xcodebuild -scheme BeatOvenKit -sdk iphoneos -configuration Release build

# Android
./gradlew assembleRelease
```

## Troubleshooting

### "Engine not initialized"

Ensure `initialize()` is called before `generate()`.

### Memory crashes

- Reduce `duration`
- Lower `density` field
- Use shorter stems

### Slow generation

- Check device CPU usage
- Reduce model complexity
- Use quantized models

## Platform-Specific Notes

### iOS

- Requires CommonCrypto for SHA-256
- Background audio requires proper entitlements
- TestFlight builds may have memory limits

### Android

- Requires WRITE_EXTERNAL_STORAGE for file export
- Use scoped storage on Android 10+
- ProGuard rules needed for release builds
