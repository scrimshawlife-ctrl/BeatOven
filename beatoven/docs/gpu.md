# BeatOven GPU Support

## Overview

BeatOven supports GPU acceleration for computationally intensive operations, with automatic fallback to CPU when GPU is unavailable.

## Supported Devices

### NVIDIA CUDA
- GeForce GTX 10-series and newer
- RTX 20/30/40-series
- Tesla, Quadro, A-series datacenter GPUs
- Requires CUDA toolkit 11.0+

### Apple Silicon (MPS)
- M1, M1 Pro, M1 Max, M1 Ultra
- M2, M2 Pro, M2 Max, M2 Ultra
- M3, M3 Pro, M3 Max
- Requires macOS 12.3+

### CPU Fallback
- All operations work on CPU
- NumPy-based implementations
- No special requirements

## Device Detection

```python
from beatoven.gpu import DeviceManager, is_gpu_available

# Check GPU availability
if is_gpu_available():
    print("GPU acceleration available")

# Get device info
manager = DeviceManager()
device = manager.get_device()
print(f"Using: {device.name}")
print(f"Memory: {device.memory_total / 1e9:.1f} GB")
```

## Device Selection

```python
from beatoven.gpu import DeviceManager, DeviceType

manager = DeviceManager(prefer_gpu=True)

# Force CPU
manager.set_device(DeviceType.CPU)

# Use specific CUDA device
manager.set_device(DeviceType.CUDA, device_id=1)

# Get PyTorch device string
device_str = manager.get_device_string()  # "cuda:0", "mps", or "cpu"
```

## PyTorch Integration

```python
import torch
from beatoven.gpu import get_device_manager

manager = get_device_manager()
device = manager.get_torch_device()

# Move tensors
tensor = torch.randn(1000, 1000)
tensor = manager.to_device(tensor)

# Synchronize after GPU operations
manager.synchronize()
```

## Runpod Cloud Execution

### Configuration

```python
from beatoven.gpu import RunpodLauncher, RunpodConfig

launcher = RunpodLauncher(api_key="your_api_key")

config = RunpodConfig(
    gpu_type="NVIDIA RTX A4000",
    gpu_count=1,
    container_image="beatoven/runtime:latest",
    volume_size_gb=20,
    max_runtime_hours=1.0
)
```

### Cost Estimation

```python
# Estimate cost before running
estimated_cost = launcher.estimate_cost(config, estimated_hours=0.5)
print(f"Estimated cost: ${estimated_cost:.2f}")
```

### Job Submission

```python
# Submit generation job
job = launcher.run_generation(
    text_intent="epic orchestral trailer",
    seed="my_seed",
    config=config,
    duration=60.0,
    tempo=120.0
)

# Wait for completion
result = launcher.wait_for_completion(job.job_id, timeout_seconds=3600)

if result.status == RunpodStatus.COMPLETED:
    print("Generation complete!")
    print(result.output_data)
```

### Batch Processing

```python
jobs_data = [
    {"text_intent": "ambient track 1", "seed": "seed1"},
    {"text_intent": "ambient track 2", "seed": "seed2"},
    {"text_intent": "ambient track 3", "seed": "seed3"},
]

jobs = launcher.run_batch(jobs_data, config)

for job in jobs:
    result = launcher.wait_for_completion(job.job_id)
    print(f"Job {job.job_id}: {result.status.value}")
```

### Available GPU Types

| GPU Type | Cost/Hour | VRAM | Best For |
|----------|-----------|------|----------|
| RTX A4000 | $0.39 | 16GB | Standard generation |
| RTX A5000 | $0.49 | 24GB | Medium batches |
| RTX A6000 | $0.79 | 48GB | Large batches |
| A100 40GB | $1.89 | 40GB | Training, large models |
| A100 80GB | $2.49 | 80GB | Very large models |
| H100 | $3.99 | 80GB | Maximum performance |
| RTX 3090 | $0.44 | 24GB | Cost-effective |
| RTX 4090 | $0.74 | 24GB | High performance |

## Local GPU Setup

### NVIDIA CUDA

1. Install NVIDIA drivers
2. Install CUDA toolkit
3. Install PyTorch with CUDA support:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Apple Silicon

1. Ensure macOS 12.3+
2. Install PyTorch with MPS support:

```bash
pip install torch
```

MPS is automatically detected on Apple Silicon.

## Performance Tips

### Memory Management

```python
# Clear GPU cache periodically
import torch
torch.cuda.empty_cache()

# Use mixed precision for memory savings
with torch.cuda.amp.autocast():
    output = model(input)
```

### Batch Size

- Larger batches = better GPU utilization
- Monitor VRAM usage
- Reduce batch size if OOM errors occur

### Data Transfer

- Minimize CPU-GPU transfers
- Keep data on GPU when possible
- Use pinned memory for faster transfers

## Troubleshooting

### CUDA Out of Memory

```python
# Reduce batch size
config.batch_size = config.batch_size // 2

# Clear cache
torch.cuda.empty_cache()

# Use gradient checkpointing
model.gradient_checkpointing_enable()
```

### Device Not Found

```python
# Check device availability
manager = DeviceManager()
for device in manager.list_devices():
    print(f"{device.device_type.value}: {device.name}")

# Force CPU if needed
manager.set_device(DeviceType.CPU)
```

### Performance Issues

1. Check GPU utilization: `nvidia-smi`
2. Profile with PyTorch profiler
3. Ensure data is on correct device
4. Check for CPU bottlenecks

## Environment Variables

```bash
# Force CPU mode
export BEATOVEN_DEVICE=cpu

# Specific CUDA device
export CUDA_VISIBLE_DEVICES=0

# Runpod API key
export RUNPOD_API_KEY=your_key_here
```
