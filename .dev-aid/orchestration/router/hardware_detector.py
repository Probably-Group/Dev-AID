"""
Hardware Detection Module for Local LLM Support

Detects system hardware capabilities to recommend appropriate local models:
- GPU detection (NVIDIA, Apple Silicon, AMD)
- VRAM detection
- System RAM detection
- CPU information

Supports cross-platform detection (macOS, Linux, Windows).
"""

import logging
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Optional

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class GPUVendor(Enum):
    """GPU vendor types"""

    NVIDIA = "nvidia"
    APPLE = "apple"
    AMD = "amd"
    INTEL = "intel"
    UNKNOWN = "unknown"
    NONE = "none"


@dataclass
class GPUInfo:
    """GPU hardware information"""

    vendor: GPUVendor
    name: str
    vram_gb: float
    driver_version: Optional[str] = None
    cuda_version: Optional[str] = None
    metal_supported: bool = False


@dataclass
class HardwareProfile:
    """Complete hardware profile for model recommendations"""

    # CPU info
    cpu_name: str
    cpu_cores: int
    cpu_threads: int

    # Memory
    ram_gb: float

    # GPU info
    gpu: Optional[GPUInfo]

    # Platform
    os_name: str
    os_version: str
    architecture: str

    @property
    def available_vram_gb(self) -> float:
        """Get available VRAM in GB (0 if no GPU)"""
        if self.gpu and self.gpu.vendor != GPUVendor.NONE:
            return self.gpu.vram_gb
        return 0.0

    @property
    def has_gpu(self) -> bool:
        """Check if system has a usable GPU"""
        return self.gpu is not None and self.gpu.vendor != GPUVendor.NONE

    @property
    def is_apple_silicon(self) -> bool:
        """Check if running on Apple Silicon (M1/M2/M3/M4)"""
        return self.gpu is not None and self.gpu.vendor == GPUVendor.APPLE

    @property
    def recommended_tier(self) -> str:
        """Get recommended model tier based on hardware"""
        vram = self.available_vram_gb

        # Apple Silicon uses unified memory - use RAM as VRAM
        if self.is_apple_silicon:
            vram = self.ram_gb * 0.75  # ~75% of RAM usable for ML

        if vram >= 80:
            return "enterprise"
        elif vram >= 48:
            return "pro"
        elif vram >= 20:
            return "high"
        elif vram >= 14:
            return "mid"
        elif vram >= 3:
            return "entry"
        else:
            return "cpu_only"


class HardwareDetector:
    """Cross-platform hardware detection for local LLM support"""

    def __init__(self) -> None:
        self.system = platform.system().lower()

    def detect(self) -> HardwareProfile:
        """
        Detect system hardware capabilities

        Returns:
            HardwareProfile with detected hardware info
        """
        # Get CPU info
        cpu_name = self._detect_cpu_name()
        cpu_cores = self._detect_cpu_cores()
        cpu_threads = self._detect_cpu_threads()

        # Get RAM
        ram_gb = self._detect_ram()

        # Get GPU
        gpu = self._detect_gpu()

        # Get platform info
        os_name = platform.system()
        os_version = platform.release()
        architecture = platform.machine()

        profile = HardwareProfile(
            cpu_name=cpu_name,
            cpu_cores=cpu_cores,
            cpu_threads=cpu_threads,
            ram_gb=ram_gb,
            gpu=gpu,
            os_name=os_name,
            os_version=os_version,
            architecture=architecture,
        )

        logger.info(f"Detected hardware profile: {profile}")
        return profile

    def _detect_cpu_name(self) -> str:
        """Detect CPU name/model"""
        try:
            if self.system == "darwin":
                # macOS
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()

                # Apple Silicon check
                result = subprocess.run(
                    ["sysctl", "-n", "hw.chip"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return result.stdout.strip()

            elif self.system == "linux":
                # Linux - parse /proc/cpuinfo
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if line.startswith("model name"):
                            return line.split(":")[1].strip()

            elif self.system == "windows":
                # Windows - use wmic
                result = subprocess.run(
                    ["wmic", "cpu", "get", "name"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        return lines[1].strip()

        except Exception as e:
            logger.warning(f"Failed to detect CPU name: {e}")

        return platform.processor() or "Unknown CPU"

    def _detect_cpu_cores(self) -> int:
        """Detect number of physical CPU cores"""
        if PSUTIL_AVAILABLE:
            try:
                return psutil.cpu_count(logical=False) or 1
            except (AttributeError, OSError) as e:
                logger.debug("CPU core detection failed: %s", e)
        return 1

    def _detect_cpu_threads(self) -> int:
        """Detect number of CPU threads (logical cores)"""
        if PSUTIL_AVAILABLE:
            try:
                return psutil.cpu_count(logical=True) or 1
            except (AttributeError, OSError) as e:
                logger.debug("CPU thread detection failed: %s", e)
        return 1

    def _detect_ram(self) -> float:
        """Detect system RAM in GB"""
        if PSUTIL_AVAILABLE:
            try:
                ram: float = round(psutil.virtual_memory().total / (1024**3), 1)
                return ram
            except Exception as e:
                logger.warning(f"Failed to detect RAM with psutil: {e}")

        # Fallback methods
        try:
            if self.system == "darwin":
                result = subprocess.run(
                    ["sysctl", "-n", "hw.memsize"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return round(int(result.stdout.strip()) / (1024**3), 1)

            elif self.system == "linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal"):
                            kb = int(line.split()[1])
                            return round(kb / (1024**2), 1)

        except Exception as e:
            logger.warning(f"Failed to detect RAM: {e}")

        return 8.0  # Default fallback

    def _detect_gpu(self) -> Optional[GPUInfo]:
        """Detect GPU information"""
        # Try NVIDIA first (most common for ML)
        nvidia_gpu = self._detect_nvidia_gpu()
        if nvidia_gpu:
            return nvidia_gpu

        # Try Apple Silicon
        apple_gpu = self._detect_apple_gpu()
        if apple_gpu:
            return apple_gpu

        # Try AMD
        amd_gpu = self._detect_amd_gpu()
        if amd_gpu:
            return amd_gpu

        # No GPU detected
        logger.info("No dedicated GPU detected - will use CPU inference")
        return GPUInfo(vendor=GPUVendor.NONE, name="None", vram_gb=0.0)

    def _detect_nvidia_gpu(self) -> Optional[GPUInfo]:
        """Detect NVIDIA GPU using nvidia-smi"""
        try:
            # Query GPU name and memory
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,driver_version",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(",")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    # Memory is in MiB
                    vram_mb = float(parts[1].strip())
                    vram_gb = round(vram_mb / 1024, 1)
                    driver = parts[2].strip() if len(parts) > 2 else None

                    # Try to get CUDA version
                    cuda_version = self._detect_cuda_version()

                    logger.info(f"Detected NVIDIA GPU: {name} with {vram_gb}GB VRAM")
                    return GPUInfo(
                        vendor=GPUVendor.NVIDIA,
                        name=name,
                        vram_gb=vram_gb,
                        driver_version=driver,
                        cuda_version=cuda_version,
                    )

        except FileNotFoundError:
            logger.debug("nvidia-smi not found - no NVIDIA GPU or drivers not installed")
        except Exception as e:
            logger.debug(f"Failed to detect NVIDIA GPU: {e}")

        return None

    def _detect_cuda_version(self) -> Optional[str]:
        """Detect CUDA version if available"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # Try to get CUDA version from nvcc
                nvcc_result = subprocess.run(
                    ["nvcc", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if nvcc_result.returncode == 0:
                    for line in nvcc_result.stdout.split("\n"):
                        if "release" in line.lower():
                            # Extract version like "12.3"
                            parts = line.split("release")
                            if len(parts) > 1:
                                version = parts[1].split(",")[0].strip()
                                return version
        except Exception:
            pass
        return None

    def _detect_apple_gpu(self) -> Optional[GPUInfo]:
        """Detect Apple Silicon GPU"""
        if self.system != "darwin":
            return None

        try:
            # Check if running on Apple Silicon
            result = subprocess.run(
                ["sysctl", "-n", "hw.optional.arm64"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            is_arm = result.returncode == 0 and result.stdout.strip() == "1"

            if not is_arm:
                # Also check architecture
                if platform.machine() != "arm64":
                    return None

            # Get chip name
            chip_result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            chip_name = "Apple Silicon"
            if chip_result.returncode == 0:
                for line in chip_result.stdout.split("\n"):
                    if "Chip:" in line or "Model Name:" in line:
                        chip_name = line.split(":")[-1].strip()
                        break

            # Get unified memory (used as VRAM on Apple Silicon)
            ram_gb = self._detect_ram()

            # Apple Silicon uses unified memory - GPU can access most of it
            # Typically 75% is available for GPU/ML workloads
            usable_vram = round(ram_gb * 0.75, 1)

            logger.info(
                f"Detected Apple Silicon: {chip_name} with {ram_gb}GB unified memory "
                f"(~{usable_vram}GB usable for ML)"
            )

            return GPUInfo(
                vendor=GPUVendor.APPLE,
                name=chip_name,
                vram_gb=usable_vram,
                metal_supported=True,
            )

        except Exception as e:
            logger.debug(f"Failed to detect Apple GPU: {e}")

        return None

    def _detect_amd_gpu(self) -> Optional[GPUInfo]:
        """Detect AMD GPU using rocm-smi"""
        try:
            # Try rocm-smi (Linux with ROCm)
            result = subprocess.run(
                ["rocm-smi", "--showmeminfo", "vram", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                # Parse rocm-smi JSON output
                # Structure varies by version, handle common formats
                for card_id, card_data in data.items():
                    if isinstance(card_data, dict):
                        vram_total = card_data.get("VRAM Total Memory (B)", 0)
                        vram_gb = round(int(vram_total) / (1024**3), 1)

                        # Get GPU name
                        name_result = subprocess.run(
                            ["rocm-smi", "--showproductname"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        name = "AMD GPU"
                        if name_result.returncode == 0:
                            for line in name_result.stdout.split("\n"):
                                if "Card series" in line:
                                    name = line.split(":")[-1].strip()
                                    break

                        logger.info(f"Detected AMD GPU: {name} with {vram_gb}GB VRAM")
                        return GPUInfo(
                            vendor=GPUVendor.AMD,
                            name=name,
                            vram_gb=vram_gb,
                        )

        except FileNotFoundError:
            logger.debug("rocm-smi not found - no AMD GPU with ROCm")
        except Exception as e:
            logger.debug(f"Failed to detect AMD GPU: {e}")

        return None


_cached_profile: Optional[HardwareProfile] = None


def detect_hardware() -> HardwareProfile:
    """
    Convenience function to detect hardware (cached after first call)

    Returns:
        HardwareProfile with detected hardware info
    """
    global _cached_profile
    if _cached_profile is None:
        detector = HardwareDetector()
        _cached_profile = detector.detect()
    return _cached_profile


def create_manual_profile(
    vram_gb: float,
    ram_gb: float = 16.0,
    gpu_vendor: str = "nvidia",
) -> HardwareProfile:
    """
    Create a hardware profile manually when auto-detection fails

    Args:
        vram_gb: GPU VRAM in GB
        ram_gb: System RAM in GB
        gpu_vendor: GPU vendor ("nvidia", "apple", "amd", "none")

    Returns:
        HardwareProfile with specified values
    """
    vendor_map = {
        "nvidia": GPUVendor.NVIDIA,
        "apple": GPUVendor.APPLE,
        "amd": GPUVendor.AMD,
        "intel": GPUVendor.INTEL,
        "none": GPUVendor.NONE,
    }

    vendor = vendor_map.get(gpu_vendor.lower(), GPUVendor.UNKNOWN)

    gpu = GPUInfo(
        vendor=vendor,
        name=f"Manual {gpu_vendor.upper()} GPU",
        vram_gb=vram_gb,
    )

    return HardwareProfile(
        cpu_name="Manual Profile",
        cpu_cores=4,
        cpu_threads=8,
        ram_gb=ram_gb,
        gpu=gpu,
        os_name=platform.system(),
        os_version=platform.release(),
        architecture=platform.machine(),
    )


# CLI usage
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    print("Detecting hardware...")
    profile = detect_hardware()

    print(f"\n{'='*50}")
    print("Hardware Profile")
    print(f"{'='*50}")
    print(f"CPU: {profile.cpu_name}")
    print(f"Cores: {profile.cpu_cores} physical, {profile.cpu_threads} threads")
    print(f"RAM: {profile.ram_gb} GB")
    print(f"OS: {profile.os_name} {profile.os_version} ({profile.architecture})")

    if profile.has_gpu:
        gpu = profile.gpu
        print(f"\nGPU: {gpu.name}")
        print(f"Vendor: {gpu.vendor.value}")
        print(f"VRAM: {gpu.vram_gb} GB")
        if gpu.driver_version:
            print(f"Driver: {gpu.driver_version}")
        if gpu.cuda_version:
            print(f"CUDA: {gpu.cuda_version}")
        if gpu.metal_supported:
            print("Metal: Supported")
    else:
        print("\nGPU: None (CPU inference only)")

    print(f"\nRecommended Model Tier: {profile.recommended_tier}")

    sys.exit(0)
