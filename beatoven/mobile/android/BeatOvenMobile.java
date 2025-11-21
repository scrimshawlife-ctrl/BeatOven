/*
 * BeatOvenMobile.java
 * Android wrapper for BeatOven generative music engine
 * Part of Applied Alchemy Labs ecosystem
 *
 * Apache License 2.0
 */

package io.appliedalchemy.beatoven;

import android.content.Context;
import android.media.AudioFormat;
import android.media.AudioTrack;
import android.os.Handler;
import android.os.Looper;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Main BeatOven engine for Android.
 * Provides on-device generative music with SEED-chain determinism.
 */
public class BeatOvenMobile {

    private static BeatOvenMobile instance;
    private Context context;
    private boolean initialized = false;
    private SeedLineage seedLineage;
    private ComputeLedger computeLedger;
    private ExecutorService executor;

    // MARK: - Singleton

    public static synchronized BeatOvenMobile getInstance() {
        if (instance == null) {
            instance = new BeatOvenMobile();
        }
        return instance;
    }

    private BeatOvenMobile() {
        computeLedger = new ComputeLedger(1000);
        executor = Executors.newSingleThreadExecutor();
    }

    // MARK: - Initialization

    /**
     * Initialize the engine with application context.
     */
    public void initialize(Context context) {
        this.context = context.getApplicationContext();
        this.initialized = true;
    }

    /**
     * Initialize seed lineage for deterministic generation.
     */
    public SeedLineage initSeedLineage(long baseSeed) {
        seedLineage = new SeedLineage(baseSeed);
        return seedLineage;
    }

    // MARK: - Generation

    /**
     * Generate music asynchronously.
     */
    public void generate(GenerationRequest request, GenerationCallback callback) {
        if (!initialized) {
            callback.onError(new BeatOvenException("Engine not initialized"));
            return;
        }

        executor.execute(() -> {
            try {
                GenerationResult result = generateSync(request);
                new Handler(Looper.getMainLooper()).post(() -> callback.onSuccess(result));
            } catch (Exception e) {
                new Handler(Looper.getMainLooper()).post(() -> callback.onError(e));
            }
        });
    }

    /**
     * Generate music synchronously.
     */
    public GenerationResult generateSync(GenerationRequest request) throws BeatOvenException {
        if (!initialized) {
            throw new BeatOvenException("Engine not initialized");
        }

        long startTime = System.currentTimeMillis();

        // Initialize seed lineage if not set
        if (seedLineage == null) {
            String seedHash = sha256(request.seed);
            long numericSeed = hexToLong(seedHash.substring(0, 16));
            seedLineage = new SeedLineage(numericSeed);
        }

        // Derive module seed
        long inputSeed = seedLineage.deriveSeed(
            "input",
            sha256(request.textIntent).substring(0, 16)
        );

        // Generate stems
        Map<String, byte[]> stems = new HashMap<>();
        for (StemType stemType : new StemType[]{StemType.DRUMS, StemType.BASS, StemType.PADS}) {
            byte[] stemData = generateStemData(
                stemType,
                request.duration,
                inputSeed,
                request.fields
            );
            stems.put(stemType.getValue(), stemData);
        }

        long runtimeMs = System.currentTimeMillis() - startTime;

        // Log compute metrics
        ComputeMetrics metrics = new ComputeMetrics(
            "generate",
            "full_generation",
            runtimeMs,
            Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory(),
            "cpu",
            seedLineage.getLineageHash()
        );
        computeLedger.log(metrics);

        // Compute provenance
        String provenanceData = request.seed + ":" + request.textIntent + ":" + seedLineage.getLineageHash();
        String provenanceHash = sha256(provenanceData);

        return new GenerationResult(
            UUID.randomUUID().toString().substring(0, 16),
            provenanceHash,
            stems,
            seedLineage.getLineageHash(),
            runtimeMs
        );
    }

    private byte[] generateStemData(StemType type, float duration, long seed, ABXRunesFields fields) {
        int sampleRate = 44100;
        int channels = 2;
        int samples = (int) (duration * sampleRate);

        ByteBuffer buffer = ByteBuffer.allocate(samples * channels * 2);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        Random rng = new Random(seed);

        for (int i = 0; i < samples; i++) {
            for (int c = 0; c < channels; c++) {
                short sample = (short) (rng.nextFloat() * fields.density * 1000);
                buffer.putShort(sample);
            }
        }

        return buffer.array();
    }

    // MARK: - Audio Export

    /**
     * Export stem data to WAV file.
     */
    public static void exportToWAV(byte[] audioData, File outputFile) throws IOException {
        int sampleRate = 44100;
        int channels = 2;
        int bitsPerSample = 16;

        FileOutputStream fos = new FileOutputStream(outputFile);

        // WAV header
        int dataSize = audioData.length;
        int fileSize = dataSize + 36;

        fos.write("RIFF".getBytes());
        fos.write(intToBytes(fileSize));
        fos.write("WAVE".getBytes());

        // fmt chunk
        fos.write("fmt ".getBytes());
        fos.write(intToBytes(16)); // chunk size
        fos.write(shortToBytes((short) 1)); // PCM
        fos.write(shortToBytes((short) channels));
        fos.write(intToBytes(sampleRate));
        fos.write(intToBytes(sampleRate * channels * bitsPerSample / 8));
        fos.write(shortToBytes((short) (channels * bitsPerSample / 8)));
        fos.write(shortToBytes((short) bitsPerSample));

        // data chunk
        fos.write("data".getBytes());
        fos.write(intToBytes(dataSize));
        fos.write(audioData);

        fos.close();
    }

    // MARK: - Audio Playback

    /**
     * Play stem data through device speaker.
     */
    public void playAudio(byte[] audioData) {
        int sampleRate = 44100;
        int channelConfig = AudioFormat.CHANNEL_OUT_STEREO;
        int audioFormat = AudioFormat.ENCODING_PCM_16BIT;

        int bufferSize = AudioTrack.getMinBufferSize(sampleRate, channelConfig, audioFormat);

        AudioTrack audioTrack = new AudioTrack.Builder()
            .setAudioFormat(new AudioFormat.Builder()
                .setEncoding(audioFormat)
                .setSampleRate(sampleRate)
                .setChannelMask(channelConfig)
                .build())
            .setBufferSizeInBytes(bufferSize)
            .build();

        audioTrack.play();
        audioTrack.write(audioData, 0, audioData.length);
        audioTrack.stop();
        audioTrack.release();
    }

    // MARK: - Utilities

    public Map<String, Object> getComputeSummary() {
        Map<String, Object> summary = new HashMap<>();
        summary.put("entries", computeLedger.getEntryCount());
        summary.put("totalRuntimeMs", computeLedger.getTotalRuntimeMs());
        return summary;
    }

    private static String sha256(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes());
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            return "";
        }
    }

    private static long hexToLong(String hex) {
        return Long.parseUnsignedLong(hex, 16);
    }

    private static byte[] intToBytes(int value) {
        return ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(value).array();
    }

    private static byte[] shortToBytes(short value) {
        return ByteBuffer.allocate(2).order(ByteOrder.LITTLE_ENDIAN).putShort(value).array();
    }

    // MARK: - Inner Classes

    /**
     * ABX-Runes semantic fields.
     */
    public static class ABXRunesFields {
        public float resonance = 0.5f;
        public float density = 0.5f;
        public float drift = 0.3f;
        public float tension = 0.5f;
        public float contrast = 0.5f;

        public ABXRunesFields() {}

        public ABXRunesFields(float resonance, float density, float drift, float tension, float contrast) {
            this.resonance = Math.max(0, Math.min(1, resonance));
            this.density = Math.max(0, Math.min(1, density));
            this.drift = Math.max(0, Math.min(1, drift));
            this.tension = Math.max(0, Math.min(1, tension));
            this.contrast = Math.max(0, Math.min(1, contrast));
        }
    }

    /**
     * Mood tag with intensity.
     */
    public static class MoodTag {
        public String name;
        public float intensity;

        public MoodTag(String name, float intensity) {
            this.name = name;
            this.intensity = Math.max(0, Math.min(1, intensity));
        }
    }

    /**
     * Generation request configuration.
     */
    public static class GenerationRequest {
        public String textIntent;
        public List<MoodTag> moodTags = new ArrayList<>();
        public String seed = "default";
        public float tempo = 120.0f;
        public float duration = 16.0f;
        public ABXRunesFields fields = new ABXRunesFields();
    }

    /**
     * Generation result with stems and provenance.
     */
    public static class GenerationResult {
        public final String jobId;
        public final String provenanceHash;
        public final Map<String, byte[]> stems;
        public final String seedLineage;
        public final long computeTimeMs;

        public GenerationResult(String jobId, String provenanceHash, Map<String, byte[]> stems,
                               String seedLineage, long computeTimeMs) {
            this.jobId = jobId;
            this.provenanceHash = provenanceHash;
            this.stems = stems;
            this.seedLineage = seedLineage;
            this.computeTimeMs = computeTimeMs;
        }
    }

    /**
     * Stem types.
     */
    public enum StemType {
        DRUMS("drums"),
        BASS("bass"),
        LEADS("leads"),
        MIDS("mids"),
        PADS("pads"),
        ATMOS("atmos"),
        FULL_MIX("full_mix");

        private final String value;
        StemType(String value) { this.value = value; }
        public String getValue() { return value; }
    }

    /**
     * SEED-chain determinism tracker.
     */
    public static class SeedLineage {
        private long baseSeed;
        private List<SeedEntry> chain = new ArrayList<>();

        public SeedLineage(long baseSeed) {
            this.baseSeed = baseSeed;
        }

        public long getCurrentSeed() {
            return chain.isEmpty() ? baseSeed : chain.get(chain.size() - 1).seed;
        }

        public long deriveSeed(String moduleName, String stateHash) {
            String combined = getCurrentSeed() + ":" + moduleName + ":" + stateHash;
            String hash = sha256(combined);
            long derived = hexToLong(hash.substring(0, 16));
            chain.add(new SeedEntry(moduleName, derived, stateHash));
            return derived;
        }

        public String getLineageHash() {
            StringBuilder sb = new StringBuilder(String.valueOf(baseSeed));
            for (SeedEntry entry : chain) {
                sb.append(":").append(entry.moduleName).append("_").append(entry.seed);
            }
            return sha256(sb.toString());
        }

        private static class SeedEntry {
            String moduleName;
            long seed;
            String stateHash;
            SeedEntry(String moduleName, long seed, String stateHash) {
                this.moduleName = moduleName;
                this.seed = seed;
                this.stateHash = stateHash;
            }
        }
    }

    /**
     * Compute metrics.
     */
    public static class ComputeMetrics {
        public final String moduleName;
        public final String operation;
        public final long runtimeMs;
        public final long memoryBytes;
        public final String device;
        public final String seedLineage;
        public final long timestamp;

        public ComputeMetrics(String moduleName, String operation, long runtimeMs,
                             long memoryBytes, String device, String seedLineage) {
            this.moduleName = moduleName;
            this.operation = operation;
            this.runtimeMs = runtimeMs;
            this.memoryBytes = memoryBytes;
            this.device = device;
            this.seedLineage = seedLineage;
            this.timestamp = System.currentTimeMillis();
        }
    }

    /**
     * Compute cost ledger.
     */
    public static class ComputeLedger {
        private List<ComputeMetrics> entries = new ArrayList<>();
        private int maxEntries;

        public ComputeLedger(int maxEntries) {
            this.maxEntries = maxEntries;
        }

        public void log(ComputeMetrics metrics) {
            entries.add(metrics);
            if (entries.size() > maxEntries) {
                entries.remove(0);
            }
        }

        public int getEntryCount() { return entries.size(); }

        public long getTotalRuntimeMs() {
            long total = 0;
            for (ComputeMetrics m : entries) total += m.runtimeMs;
            return total;
        }
    }

    /**
     * Generation callback interface.
     */
    public interface GenerationCallback {
        void onSuccess(GenerationResult result);
        void onError(Exception error);
    }

    /**
     * BeatOven exception.
     */
    public static class BeatOvenException extends Exception {
        public BeatOvenException(String message) {
            super(message);
        }
    }
}
