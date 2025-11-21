"""
BeatOven Runpod Launcher

GPU cloud execution via Runpod infrastructure.
"""

import os
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class RunpodStatus(Enum):
    """Runpod job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RunpodConfig:
    """Configuration for Runpod execution."""
    gpu_type: str = "NVIDIA RTX A4000"
    gpu_count: int = 1
    container_image: str = "beatoven/runtime:latest"
    volume_size_gb: int = 20
    max_runtime_hours: float = 1.0
    env_vars: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gpu_type": self.gpu_type,
            "gpu_count": self.gpu_count,
            "container_image": self.container_image,
            "volume_size_gb": self.volume_size_gb,
            "max_runtime_hours": self.max_runtime_hours,
            "env_vars": self.env_vars
        }


@dataclass
class RunpodJob:
    """Represents a Runpod job."""
    job_id: str
    status: RunpodStatus
    config: RunpodConfig
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "config": self.config.to_dict(),
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "cost_usd": self.cost_usd
        }


class RunpodLauncher:
    """
    Launches BeatOven jobs on Runpod GPU cloud.

    Handles job submission, monitoring, and result retrieval.
    """

    # Available GPU types on Runpod
    GPU_TYPES = [
        "NVIDIA RTX A4000",
        "NVIDIA RTX A5000",
        "NVIDIA RTX A6000",
        "NVIDIA A100 40GB",
        "NVIDIA A100 80GB",
        "NVIDIA H100",
        "NVIDIA RTX 3090",
        "NVIDIA RTX 4090"
    ]

    # Approximate costs per hour (USD)
    GPU_COSTS = {
        "NVIDIA RTX A4000": 0.39,
        "NVIDIA RTX A5000": 0.49,
        "NVIDIA RTX A6000": 0.79,
        "NVIDIA A100 40GB": 1.89,
        "NVIDIA A100 80GB": 2.49,
        "NVIDIA H100": 3.99,
        "NVIDIA RTX 3090": 0.44,
        "NVIDIA RTX 4090": 0.74
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://api.runpod.io/v2"
    ):
        """
        Initialize Runpod launcher.

        Args:
            api_key: Runpod API key (or from RUNPOD_API_KEY env var)
            endpoint: Runpod API endpoint
        """
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY")
        self.endpoint = endpoint
        self._jobs: Dict[str, RunpodJob] = {}

    def is_configured(self) -> bool:
        """Check if Runpod is properly configured."""
        return self.api_key is not None

    def estimate_cost(
        self,
        config: RunpodConfig,
        estimated_hours: float
    ) -> float:
        """
        Estimate job cost.

        Args:
            config: Job configuration
            estimated_hours: Estimated runtime in hours

        Returns:
            Estimated cost in USD
        """
        hourly_rate = self.GPU_COSTS.get(config.gpu_type, 1.0)
        return hourly_rate * config.gpu_count * estimated_hours

    def create_job(
        self,
        input_data: Dict[str, Any],
        config: Optional[RunpodConfig] = None
    ) -> RunpodJob:
        """
        Create a new Runpod job (local simulation).

        Args:
            input_data: Input data for the job
            config: Job configuration

        Returns:
            Created job object
        """
        if config is None:
            config = RunpodConfig()

        # Generate job ID
        job_id = hashlib.sha256(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()[:16]

        job = RunpodJob(
            job_id=job_id,
            status=RunpodStatus.PENDING,
            config=config,
            input_data=input_data
        )

        self._jobs[job_id] = job
        return job

    def submit_job(self, job: RunpodJob) -> bool:
        """
        Submit job to Runpod.

        Note: This is a simulation. Real implementation requires
        Runpod API integration.

        Args:
            job: Job to submit

        Returns:
            True if submitted successfully
        """
        if not self.is_configured():
            # Simulate local execution
            job.status = RunpodStatus.RUNNING
            return True

        # Real API call would go here
        # For now, simulate submission
        job.status = RunpodStatus.RUNNING
        return True

    def get_job_status(self, job_id: str) -> Optional[RunpodStatus]:
        """Get job status."""
        if job_id in self._jobs:
            return self._jobs[job_id].status
        return None

    def get_job(self, job_id: str) -> Optional[RunpodJob]:
        """Get job by ID."""
        return self._jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self._jobs:
            self._jobs[job_id].status = RunpodStatus.CANCELLED
            return True
        return False

    def wait_for_completion(
        self,
        job_id: str,
        timeout_seconds: float = 3600,
        poll_interval: float = 5.0
    ) -> Optional[RunpodJob]:
        """
        Wait for job completion.

        Args:
            job_id: Job ID to wait for
            timeout_seconds: Maximum wait time
            poll_interval: Polling interval

        Returns:
            Completed job or None if timeout
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            job = self._jobs.get(job_id)
            if job is None:
                return None

            if job.status in (RunpodStatus.COMPLETED, RunpodStatus.FAILED, RunpodStatus.CANCELLED):
                return job

            # Simulate completion for local mode
            if not self.is_configured():
                job.status = RunpodStatus.COMPLETED
                job.output_data = {"simulated": True, "input": job.input_data}
                return job

            time.sleep(poll_interval)

        return None

    def run_generation(
        self,
        text_intent: str,
        seed: str,
        config: Optional[RunpodConfig] = None,
        **kwargs
    ) -> RunpodJob:
        """
        Run BeatOven generation on Runpod.

        Args:
            text_intent: Generation intent
            seed: ABX-Runes seed
            config: Runpod configuration
            **kwargs: Additional generation parameters

        Returns:
            Job object
        """
        input_data = {
            "action": "generate",
            "text_intent": text_intent,
            "seed": seed,
            **kwargs
        }

        job = self.create_job(input_data, config)
        self.submit_job(job)
        return job

    def run_batch(
        self,
        jobs_data: List[Dict[str, Any]],
        config: Optional[RunpodConfig] = None
    ) -> List[RunpodJob]:
        """
        Run batch of jobs on Runpod.

        Args:
            jobs_data: List of job input data
            config: Shared configuration

        Returns:
            List of job objects
        """
        jobs = []
        for data in jobs_data:
            job = self.create_job(data, config)
            self.submit_job(job)
            jobs.append(job)
        return jobs

    def get_available_gpus(self) -> List[Dict[str, Any]]:
        """Get list of available GPU types with pricing."""
        return [
            {"type": gpu, "cost_per_hour": self.GPU_COSTS.get(gpu, 0)}
            for gpu in self.GPU_TYPES
        ]


__all__ = [
    "RunpodLauncher", "RunpodConfig", "RunpodJob", "RunpodStatus"
]
