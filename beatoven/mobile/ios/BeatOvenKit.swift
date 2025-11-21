// BeatOvenKit.swift
// iOS Swift wrapper for BeatOven generative music engine
// Part of Applied Alchemy Labs ecosystem

import Foundation
import AVFoundation

// MARK: - Core Types

/// ABX-Runes semantic fields for generation control
public struct ABXRunesFields {
    public var resonance: Float
    public var density: Float
    public var drift: Float
    public var tension: Float
    public var contrast: Float

    public init(
        resonance: Float = 0.5,
        density: Float = 0.5,
        drift: Float = 0.3,
        tension: Float = 0.5,
        contrast: Float = 0.5
    ) {
        self.resonance = max(0, min(1, resonance))
        self.density = max(0, min(1, density))
        self.drift = max(0, min(1, drift))
        self.tension = max(0, min(1, tension))
        self.contrast = max(0, min(1, contrast))
    }
}

/// Mood tag with intensity
public struct MoodTag {
    public let name: String
    public let intensity: Float

    public init(name: String, intensity: Float = 1.0) {
        self.name = name
        self.intensity = max(0, min(1, intensity))
    }
}

/// Generation request configuration
public struct GenerationRequest {
    public var textIntent: String
    public var moodTags: [MoodTag]
    public var seed: String
    public var tempo: Float
    public var duration: Float
    public var fields: ABXRunesFields

    public init(
        textIntent: String,
        moodTags: [MoodTag] = [],
        seed: String = "default",
        tempo: Float = 120.0,
        duration: Float = 16.0,
        fields: ABXRunesFields = ABXRunesFields()
    ) {
        self.textIntent = textIntent
        self.moodTags = moodTags
        self.seed = seed
        self.tempo = tempo
        self.duration = duration
        self.fields = fields
    }
}

/// Generation result with stems and provenance
public struct GenerationResult {
    public let jobId: String
    public let provenanceHash: String
    public let stems: [String: Data]
    public let seedLineage: String
    public let computeTimeMs: Double
}

/// Stem types available for generation
public enum StemType: String, CaseIterable {
    case drums = "drums"
    case bass = "bass"
    case leads = "leads"
    case mids = "mids"
    case pads = "pads"
    case atmos = "atmos"
    case fullMix = "full_mix"
}

// MARK: - Seed Lineage

/// SEED-chain determinism tracker for iOS
public class SeedLineage {
    private var baseSeed: UInt64
    private var chain: [(String, UInt64, String)] = []

    public init(baseSeed: UInt64) {
        self.baseSeed = baseSeed
    }

    public var currentSeed: UInt64 {
        chain.last?.1 ?? baseSeed
    }

    public func deriveSeed(moduleName: String, stateHash: String) -> UInt64 {
        let combined = "\(currentSeed):\(moduleName):\(stateHash)"
        let hash = combined.sha256()
        let derived = hash.prefix(16).hexToUInt64()
        chain.append((moduleName, derived, stateHash))
        return derived
    }

    public func getLineageHash() -> String {
        var lineageStr = "\(baseSeed)"
        for (name, seed, _) in chain {
            lineageStr += ":\(name)_\(seed)"
        }
        return lineageStr.sha256()
    }
}

// MARK: - Compute Ledger

/// Compute metrics for a single operation
public struct ComputeMetrics {
    public let moduleName: String
    public let operation: String
    public let runtimeMs: Double
    public let memoryBytes: Int
    public let device: String
    public let seedLineage: String
    public let timestamp: Date
}

/// Compute cost ledger for tracking operations
public class ComputeLedger {
    private var entries: [ComputeMetrics] = []
    private let maxEntries: Int

    public init(maxEntries: Int = 1000) {
        self.maxEntries = maxEntries
    }

    public func log(_ metrics: ComputeMetrics) {
        entries.append(metrics)
        if entries.count > maxEntries {
            entries.removeFirst(entries.count - maxEntries)
        }
    }

    public var totalRuntimeMs: Double {
        entries.reduce(0) { $0 + $1.runtimeMs }
    }

    public var entryCount: Int { entries.count }
}

// MARK: - BeatOven Engine

/// Main BeatOven engine for iOS
public class BeatOvenEngine {

    // MARK: Properties

    public static let shared = BeatOvenEngine()

    private var seedLineage: SeedLineage?
    private let computeLedger = ComputeLedger()
    private var isInitialized = false
    private var modelPath: URL?

    // MARK: Initialization

    private init() {}

    /// Initialize the engine with model path
    public func initialize(modelPath: URL? = nil) throws {
        self.modelPath = modelPath ?? Bundle.main.resourceURL?.appendingPathComponent("Models")
        isInitialized = true
    }

    /// Initialize seed lineage for deterministic generation
    public func initSeedLineage(baseSeed: UInt64) -> SeedLineage {
        let lineage = SeedLineage(baseSeed: baseSeed)
        self.seedLineage = lineage
        return lineage
    }

    // MARK: Generation

    /// Generate music from request
    public func generate(request: GenerationRequest) async throws -> GenerationResult {
        guard isInitialized else {
            throw BeatOvenError.notInitialized
        }

        let startTime = CFAbsoluteTimeGetCurrent()

        // Initialize seed lineage if not set
        if seedLineage == nil {
            let seedHash = request.seed.sha256()
            let numericSeed = seedHash.prefix(16).hexToUInt64()
            seedLineage = SeedLineage(baseSeed: numericSeed)
        }

        // Derive module seeds
        let inputSeed = seedLineage!.deriveSeed(
            moduleName: "input",
            stateHash: request.textIntent.sha256().prefix(16).description
        )

        // Process through modules (simplified for mobile)
        let fields = request.fields

        // Generate stems (placeholder - real implementation uses ONNX)
        var stems: [String: Data] = [:]
        for stemType in [StemType.drums, StemType.bass, StemType.pads] {
            let stemData = generateStemData(
                type: stemType,
                duration: request.duration,
                seed: inputSeed,
                fields: fields
            )
            stems[stemType.rawValue] = stemData
        }

        let runtimeMs = (CFAbsoluteTimeGetCurrent() - startTime) * 1000

        // Log compute metrics
        let metrics = ComputeMetrics(
            moduleName: "generate",
            operation: "full_generation",
            runtimeMs: runtimeMs,
            memoryBytes: getMemoryUsage(),
            device: "cpu",
            seedLineage: seedLineage!.getLineageHash(),
            timestamp: Date()
        )
        computeLedger.log(metrics)

        // Compute provenance
        let provenanceData = "\(request.seed):\(request.textIntent):\(seedLineage!.getLineageHash())"
        let provenanceHash = provenanceData.sha256()

        return GenerationResult(
            jobId: UUID().uuidString.prefix(16).description,
            provenanceHash: provenanceHash,
            stems: stems,
            seedLineage: seedLineage!.getLineageHash(),
            computeTimeMs: runtimeMs
        )
    }

    // MARK: Stem Generation

    private func generateStemData(
        type: StemType,
        duration: Float,
        seed: UInt64,
        fields: ABXRunesFields
    ) -> Data {
        // Simplified audio generation for mobile
        // Real implementation would use ONNX Runtime Mobile

        let sampleRate = 44100
        let channels = 2
        let samples = Int(duration * Float(sampleRate))

        var audioData = Data(capacity: samples * channels * 2)
        var rng = SeededRNG(seed: seed)

        for _ in 0..<samples {
            for _ in 0..<channels {
                let sample = Int16(rng.nextFloat() * Float(fields.density) * 1000)
                withUnsafeBytes(of: sample.littleEndian) { audioData.append(contentsOf: $0) }
            }
        }

        return audioData
    }

    // MARK: Utilities

    private func getMemoryUsage() -> Int {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size) / 4
        let result = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }
        return result == KERN_SUCCESS ? Int(info.resident_size) : 0
    }

    /// Get compute ledger summary
    public func getComputeSummary() -> [String: Any] {
        return [
            "entries": computeLedger.entryCount,
            "totalRuntimeMs": computeLedger.totalRuntimeMs
        ]
    }
}

// MARK: - Audio Export

/// Audio exporter for saving stems to device
public class AudioExporter {

    /// Export stem data to WAV file
    public static func exportToWAV(
        data: Data,
        sampleRate: Int = 44100,
        channels: Int = 2,
        to url: URL
    ) throws {
        // WAV header
        var header = Data()

        let dataSize = UInt32(data.count)
        let fileSize = dataSize + 36

        // RIFF header
        header.append("RIFF".data(using: .ascii)!)
        header.append(withUnsafeBytes(of: fileSize.littleEndian) { Data($0) })
        header.append("WAVE".data(using: .ascii)!)

        // fmt chunk
        header.append("fmt ".data(using: .ascii)!)
        header.append(withUnsafeBytes(of: UInt32(16).littleEndian) { Data($0) })
        header.append(withUnsafeBytes(of: UInt16(1).littleEndian) { Data($0) }) // PCM
        header.append(withUnsafeBytes(of: UInt16(channels).littleEndian) { Data($0) })
        header.append(withUnsafeBytes(of: UInt32(sampleRate).littleEndian) { Data($0) })
        header.append(withUnsafeBytes(of: UInt32(sampleRate * channels * 2).littleEndian) { Data($0) })
        header.append(withUnsafeBytes(of: UInt16(channels * 2).littleEndian) { Data($0) })
        header.append(withUnsafeBytes(of: UInt16(16).littleEndian) { Data($0) })

        // data chunk
        header.append("data".data(using: .ascii)!)
        header.append(withUnsafeBytes(of: dataSize.littleEndian) { Data($0) })

        var fileData = header
        fileData.append(data)

        try fileData.write(to: url)
    }
}

// MARK: - Patch System

/// Patch configuration for routing
public struct PatchConfig: Codable {
    public var name: String
    public var nodes: [PatchNode]
    public var connections: [PatchConnection]
}

public struct PatchNode: Codable {
    public var id: String
    public var type: String
    public var params: [String: Float]
}

public struct PatchConnection: Codable {
    public var sourceNode: String
    public var sourcePort: String
    public var destNode: String
    public var destPort: String
}

/// Patch loader for mobile
public class PatchLoader {

    public static func load(from url: URL) throws -> PatchConfig {
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(PatchConfig.self, from: data)
    }

    public static func load(fromBundle name: String) throws -> PatchConfig {
        guard let url = Bundle.main.url(forResource: name, withExtension: "json") else {
            throw BeatOvenError.patchNotFound
        }
        return try load(from: url)
    }
}

// MARK: - Errors

public enum BeatOvenError: Error {
    case notInitialized
    case modelLoadFailed
    case generationFailed
    case exportFailed
    case patchNotFound
}

// MARK: - Helpers

extension String {
    func sha256() -> String {
        guard let data = self.data(using: .utf8) else { return "" }
        var hash = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
        data.withUnsafeBytes { _ = CC_SHA256($0.baseAddress, CC_LONG(data.count), &hash) }
        return hash.map { String(format: "%02x", $0) }.joined()
    }

    func hexToUInt64() -> UInt64 {
        return UInt64(self.prefix(16), radix: 16) ?? 0
    }
}

/// Seeded random number generator
struct SeededRNG {
    private var state: UInt64

    init(seed: UInt64) {
        state = seed
    }

    mutating func next() -> UInt64 {
        state = state &* 6364136223846793005 &+ 1442695040888963407
        return state
    }

    mutating func nextFloat() -> Float {
        return Float(next() & 0xFFFFFF) / Float(0xFFFFFF)
    }
}

// Required for SHA256
import CommonCrypto
