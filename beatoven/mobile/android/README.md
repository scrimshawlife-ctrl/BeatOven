# BeatOven Android Integration

## Overview

BeatOvenMobile provides native Android integration for the BeatOven generative music engine. It supports on-device inference with full SEED-chain determinism and compute tracking.

## Requirements

- Android API 21+ (Android 5.0 Lollipop)
- Java 8+ or Kotlin
- Android Studio 4.0+

## Installation

### Gradle

```groovy
dependencies {
    implementation 'io.appliedalchemy:beatoven-android:1.0.0'
}
```

### Manual

Copy `BeatOvenMobile.java` to your project's source directory.

## Quick Start

```java
import io.appliedalchemy.beatoven.BeatOvenMobile;
import io.appliedalchemy.beatoven.BeatOvenMobile.*;

// Initialize engine
BeatOvenMobile engine = BeatOvenMobile.getInstance();
engine.initialize(context);

// Create generation request
GenerationRequest request = new GenerationRequest();
request.textIntent = "dark ambient pad with subtle rhythm";
request.moodTags.add(new MoodTag("dark", 0.8f));
request.moodTags.add(new MoodTag("ambient", 0.9f));
request.seed = "my_creative_seed";
request.tempo = 90.0f;
request.duration = 16.0f;
request.fields = new ABXRunesFields(0.7f, 0.4f, 0.5f, 0.3f, 0.5f);

// Generate asynchronously
engine.generate(request, new GenerationCallback() {
    @Override
    public void onSuccess(GenerationResult result) {
        Log.d("BeatOven", "Job ID: " + result.jobId);
        Log.d("BeatOven", "Provenance: " + result.provenanceHash);
    }

    @Override
    public void onError(Exception error) {
        Log.e("BeatOven", "Generation failed", error);
    }
});
```

### Kotlin

```kotlin
val engine = BeatOvenMobile.getInstance()
engine.initialize(context)

val request = BeatOvenMobile.GenerationRequest().apply {
    textIntent = "dark ambient pad"
    moodTags.add(BeatOvenMobile.MoodTag("dark", 0.8f))
    seed = "my_seed"
    tempo = 90f
    duration = 16f
    fields = BeatOvenMobile.ABXRunesFields(0.7f, 0.4f, 0.5f, 0.3f, 0.5f)
}

engine.generate(request, object : BeatOvenMobile.GenerationCallback {
    override fun onSuccess(result: BeatOvenMobile.GenerationResult) {
        println("Generated: ${result.jobId}")
    }
    override fun onError(error: Exception) {
        error.printStackTrace()
    }
})
```

## Seed Lineage

BeatOvenMobile maintains SEED-chain determinism:

```java
// Initialize lineage
SeedLineage lineage = engine.initSeedLineage(12345L);

// Seeds are automatically derived for each module
// Same seed + same inputs = identical output
```

## Exporting Audio

```java
// Export stem to WAV file
byte[] drumsData = result.stems.get("drums");
File outputFile = new File(getExternalFilesDir(null), "drums.wav");
BeatOvenMobile.exportToWAV(drumsData, outputFile);
```

## Audio Playback

```java
// Play stem through device speaker
engine.playAudio(result.stems.get("drums"));
```

## Compute Tracking

```java
// Get compute summary
Map<String, Object> summary = engine.getComputeSummary();
Log.d("BeatOven", "Total runtime: " + summary.get("totalRuntimeMs") + "ms");
```

## Low Memory Mode

For devices with limited RAM:

```java
GenerationRequest request = new GenerationRequest();
request.duration = 8.0f;  // Shorter duration
request.fields = new ABXRunesFields();
request.fields.density = 0.3f;  // Lower complexity
```

## Thread Safety

`BeatOvenMobile.getInstance()` is thread-safe. Generation runs on a background thread with callbacks on the main thread.

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

## Permissions

Add to AndroidManifest.xml if exporting to external storage:

```xml
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

## ProGuard Rules

```proguard
-keep class io.appliedalchemy.beatoven.** { *; }
```

## Error Handling

```java
engine.generate(request, new GenerationCallback() {
    @Override
    public void onSuccess(GenerationResult result) {
        // Handle success
    }

    @Override
    public void onError(Exception error) {
        if (error instanceof BeatOvenException) {
            // BeatOven-specific error
        }
    }
});
```

## License

Apache 2.0 - See main repository LICENSE file.
