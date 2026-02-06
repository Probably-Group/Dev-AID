"""Tests for HardwareDetector"""

from unittest.mock import Mock, patch

import pytest

from router.hardware_detector import (
    GPUInfo,
    GPUVendor,
    HardwareDetector,
    HardwareProfile,
    create_manual_profile,
    detect_hardware,
)


# ── Data Classes ─────────────────────────────────────────────────────────────


class TestGPUVendor:
    def test_all_vendors(self):
        assert GPUVendor.NVIDIA.value == "nvidia"
        assert GPUVendor.APPLE.value == "apple"
        assert GPUVendor.AMD.value == "amd"
        assert GPUVendor.INTEL.value == "intel"
        assert GPUVendor.UNKNOWN.value == "unknown"
        assert GPUVendor.NONE.value == "none"


class TestGPUInfo:
    def test_create(self):
        gpu = GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 4090", vram_gb=24.0)
        assert gpu.vendor == GPUVendor.NVIDIA
        assert gpu.name == "RTX 4090"
        assert gpu.vram_gb == 24.0
        assert gpu.driver_version is None
        assert gpu.cuda_version is None
        assert gpu.metal_supported is False

    def test_create_with_all_fields(self):
        gpu = GPUInfo(
            vendor=GPUVendor.NVIDIA,
            name="RTX 4090",
            vram_gb=24.0,
            driver_version="535.86",
            cuda_version="12.2",
        )
        assert gpu.driver_version == "535.86"
        assert gpu.cuda_version == "12.2"


class TestHardwareProfile:
    @pytest.fixture
    def nvidia_profile(self):
        return HardwareProfile(
            cpu_name="AMD Ryzen 9 7950X",
            cpu_cores=16,
            cpu_threads=32,
            ram_gb=64.0,
            gpu=GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 4090", vram_gb=24.0),
            os_name="Linux",
            os_version="6.5.0",
            architecture="x86_64",
        )

    @pytest.fixture
    def apple_profile(self):
        return HardwareProfile(
            cpu_name="Apple M3 Max",
            cpu_cores=14,
            cpu_threads=14,
            ram_gb=96.0,
            gpu=GPUInfo(vendor=GPUVendor.APPLE, name="M3 Max", vram_gb=72.0, metal_supported=True),
            os_name="Darwin",
            os_version="23.5.0",
            architecture="arm64",
        )

    @pytest.fixture
    def no_gpu_profile(self):
        return HardwareProfile(
            cpu_name="Intel i5",
            cpu_cores=4,
            cpu_threads=8,
            ram_gb=16.0,
            gpu=GPUInfo(vendor=GPUVendor.NONE, name="None", vram_gb=0.0),
            os_name="Linux",
            os_version="6.5.0",
            architecture="x86_64",
        )

    def test_available_vram_nvidia(self, nvidia_profile):
        assert nvidia_profile.available_vram_gb == 24.0

    def test_available_vram_none(self, no_gpu_profile):
        assert no_gpu_profile.available_vram_gb == 0.0

    def test_available_vram_null_gpu(self):
        profile = HardwareProfile(
            cpu_name="Test",
            cpu_cores=1,
            cpu_threads=1,
            ram_gb=8.0,
            gpu=None,
            os_name="Test",
            os_version="1.0",
            architecture="x86",
        )
        assert profile.available_vram_gb == 0.0

    def test_has_gpu_true(self, nvidia_profile):
        assert nvidia_profile.has_gpu is True

    def test_has_gpu_false(self, no_gpu_profile):
        assert no_gpu_profile.has_gpu is False

    def test_has_gpu_null(self):
        profile = HardwareProfile(
            cpu_name="Test",
            cpu_cores=1,
            cpu_threads=1,
            ram_gb=8.0,
            gpu=None,
            os_name="Test",
            os_version="1.0",
            architecture="x86",
        )
        assert profile.has_gpu is False

    def test_is_apple_silicon_true(self, apple_profile):
        assert apple_profile.is_apple_silicon is True

    def test_is_apple_silicon_false(self, nvidia_profile):
        assert nvidia_profile.is_apple_silicon is False

    def test_recommended_tier_enterprise(self):
        profile = HardwareProfile(
            cpu_name="Test",
            cpu_cores=1,
            cpu_threads=1,
            ram_gb=128.0,
            gpu=GPUInfo(vendor=GPUVendor.NVIDIA, name="A100", vram_gb=80.0),
            os_name="Linux",
            os_version="1.0",
            architecture="x86_64",
        )
        assert profile.recommended_tier == "enterprise"

    def test_recommended_tier_pro(self):
        profile = HardwareProfile(
            cpu_name="Test",
            cpu_cores=1,
            cpu_threads=1,
            ram_gb=64.0,
            gpu=GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 4090", vram_gb=48.0),
            os_name="Linux",
            os_version="1.0",
            architecture="x86_64",
        )
        assert profile.recommended_tier == "pro"

    def test_recommended_tier_high(self, nvidia_profile):
        assert nvidia_profile.recommended_tier == "high"

    def test_recommended_tier_mid(self):
        profile = HardwareProfile(
            cpu_name="Test",
            cpu_cores=1,
            cpu_threads=1,
            ram_gb=16.0,
            gpu=GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 3060", vram_gb=16.0),
            os_name="Linux",
            os_version="1.0",
            architecture="x86_64",
        )
        assert profile.recommended_tier == "mid"

    def test_recommended_tier_entry(self):
        profile = HardwareProfile(
            cpu_name="Test",
            cpu_cores=1,
            cpu_threads=1,
            ram_gb=8.0,
            gpu=GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 3050", vram_gb=4.0),
            os_name="Linux",
            os_version="1.0",
            architecture="x86_64",
        )
        assert profile.recommended_tier == "entry"

    def test_recommended_tier_cpu_only(self, no_gpu_profile):
        assert no_gpu_profile.recommended_tier == "cpu_only"

    def test_recommended_tier_apple_uses_ram(self, apple_profile):
        # Apple uses RAM * 0.75 as VRAM: 96 * 0.75 = 72 >= 48 => "pro"
        assert apple_profile.recommended_tier == "pro"


# ── HardwareDetector ─────────────────────────────────────────────────────────


class TestHardwareDetectorCPU:
    def test_detect_cpu_name_darwin(self):
        detector = HardwareDetector()
        detector.system = "darwin"
        with patch("router.hardware_detector.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Apple M3 Max\n")
            name = detector._detect_cpu_name()
            assert name == "Apple M3 Max"

    def test_detect_cpu_name_darwin_fallback_to_chip(self):
        detector = HardwareDetector()
        detector.system = "darwin"
        with patch("router.hardware_detector.subprocess.run") as mock_run:
            # First call fails (brand_string), second succeeds (hw.chip)
            mock_run.side_effect = [
                Mock(returncode=1, stdout=""),
                Mock(returncode=0, stdout="Apple M2\n"),
            ]
            name = detector._detect_cpu_name()
            assert name == "Apple M2"

    def test_detect_cpu_name_linux(self):
        detector = HardwareDetector()
        detector.system = "linux"
        cpu_info = "model name\t: Intel Core i9-13900K\n"
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__ = lambda s: iter([cpu_info])
            mock_open.return_value.__exit__ = Mock(return_value=False)
            name = detector._detect_cpu_name()
            assert "Intel" in name

    def test_detect_cpu_name_windows(self):
        detector = HardwareDetector()
        detector.system = "windows"
        with patch("router.hardware_detector.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Name\nIntel Core i7-13700K\n")
            name = detector._detect_cpu_name()
            assert "Intel" in name

    def test_detect_cpu_name_exception(self):
        detector = HardwareDetector()
        detector.system = "darwin"
        with patch("router.hardware_detector.subprocess.run", side_effect=OSError("fail")):
            name = detector._detect_cpu_name()
            assert isinstance(name, str)

    def test_detect_cpu_cores_with_psutil(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.PSUTIL_AVAILABLE", True):
            with patch("router.hardware_detector.psutil") as mock_psutil:
                mock_psutil.cpu_count.return_value = 8
                cores = detector._detect_cpu_cores()
                assert cores == 8

    def test_detect_cpu_cores_no_psutil(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.PSUTIL_AVAILABLE", False):
            cores = detector._detect_cpu_cores()
            assert cores == 1

    def test_detect_cpu_threads_with_psutil(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.PSUTIL_AVAILABLE", True):
            with patch("router.hardware_detector.psutil") as mock_psutil:
                mock_psutil.cpu_count.return_value = 16
                threads = detector._detect_cpu_threads()
                assert threads == 16


class TestHardwareDetectorRAM:
    def test_detect_ram_with_psutil(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.PSUTIL_AVAILABLE", True):
            with patch("router.hardware_detector.psutil") as mock_psutil:
                mock_psutil.virtual_memory.return_value = Mock(total=34359738368)  # 32GB
                ram = detector._detect_ram()
                assert ram == 32.0

    def test_detect_ram_darwin_fallback(self):
        detector = HardwareDetector()
        detector.system = "darwin"
        with patch("router.hardware_detector.PSUTIL_AVAILABLE", False):
            with patch("router.hardware_detector.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="17179869184\n")  # 16GB
                ram = detector._detect_ram()
                assert ram == 16.0

    def test_detect_ram_default_fallback(self):
        detector = HardwareDetector()
        detector.system = "unknown_os"
        with patch("router.hardware_detector.PSUTIL_AVAILABLE", False):
            ram = detector._detect_ram()
            assert ram == 8.0


class TestHardwareDetectorGPU:
    def test_detect_nvidia_gpu_success(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout="NVIDIA GeForce RTX 4090, 24564, 535.86\n"
            )
            gpu = detector._detect_nvidia_gpu()
            assert gpu is not None
            assert gpu.vendor == GPUVendor.NVIDIA
            assert "RTX 4090" in gpu.name
            assert gpu.vram_gb > 20

    def test_detect_nvidia_gpu_not_found(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run", side_effect=FileNotFoundError()):
            gpu = detector._detect_nvidia_gpu()
            assert gpu is None

    def test_detect_nvidia_gpu_error(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run", side_effect=OSError("fail")):
            gpu = detector._detect_nvidia_gpu()
            assert gpu is None

    def test_detect_apple_gpu_not_darwin(self):
        detector = HardwareDetector()
        detector.system = "linux"
        gpu = detector._detect_apple_gpu()
        assert gpu is None

    def test_detect_apple_gpu_arm64(self):
        detector = HardwareDetector()
        detector.system = "darwin"
        with patch("router.hardware_detector.subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0, stdout="1\n"),  # arm64 check
                Mock(returncode=0, stdout="  Chip: Apple M3 Max\n"),  # profiler
            ]
            with patch("router.hardware_detector.PSUTIL_AVAILABLE", True):
                with patch("router.hardware_detector.psutil") as mock_psutil:
                    mock_psutil.virtual_memory.return_value = Mock(total=103079215104)  # 96GB
                    gpu = detector._detect_apple_gpu()
                    assert gpu is not None
                    assert gpu.vendor == GPUVendor.APPLE
                    assert gpu.metal_supported is True

    def test_detect_apple_gpu_exception(self):
        detector = HardwareDetector()
        detector.system = "darwin"
        with patch("router.hardware_detector.subprocess.run", side_effect=OSError("fail")):
            gpu = detector._detect_apple_gpu()
            assert gpu is None

    def test_detect_amd_gpu_not_found(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run", side_effect=FileNotFoundError()):
            gpu = detector._detect_amd_gpu()
            assert gpu is None

    def test_detect_amd_gpu_error(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run", side_effect=OSError("fail")):
            gpu = detector._detect_amd_gpu()
            assert gpu is None

    def test_detect_gpu_none(self):
        detector = HardwareDetector()
        with patch.object(detector, "_detect_nvidia_gpu", return_value=None):
            with patch.object(detector, "_detect_apple_gpu", return_value=None):
                with patch.object(detector, "_detect_amd_gpu", return_value=None):
                    gpu = detector._detect_gpu()
                    assert gpu is not None
                    assert gpu.vendor == GPUVendor.NONE

    def test_detect_gpu_nvidia_found(self):
        detector = HardwareDetector()
        nvidia = GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 4090", vram_gb=24.0)
        with patch.object(detector, "_detect_nvidia_gpu", return_value=nvidia):
            gpu = detector._detect_gpu()
            assert gpu.vendor == GPUVendor.NVIDIA

    def test_detect_cuda_version_success(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0, stdout="535.86\n"),
                Mock(returncode=0, stdout="nvcc: NVIDIA\nCuda compilation tools, release 12.2\n"),
            ]
            version = detector._detect_cuda_version()
            assert version is not None
            assert "12.2" in version

    def test_detect_cuda_version_no_nvcc(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0, stdout="535.86\n"),
                Mock(returncode=1, stdout=""),
            ]
            version = detector._detect_cuda_version()
            assert version is None

    def test_detect_cuda_version_exception(self):
        detector = HardwareDetector()
        with patch("router.hardware_detector.subprocess.run", side_effect=OSError()):
            version = detector._detect_cuda_version()
            assert version is None


class TestHardwareDetectorDetect:
    def test_full_detect(self):
        detector = HardwareDetector()
        with patch.object(detector, "_detect_cpu_name", return_value="Test CPU"):
            with patch.object(detector, "_detect_cpu_cores", return_value=8):
                with patch.object(detector, "_detect_cpu_threads", return_value=16):
                    with patch.object(detector, "_detect_ram", return_value=32.0):
                        with patch.object(detector, "_detect_gpu", return_value=None):
                            profile = detector.detect()
                            assert profile.cpu_name == "Test CPU"
                            assert profile.cpu_cores == 8
                            assert profile.cpu_threads == 16
                            assert profile.ram_gb == 32.0


# ── Helper Functions ─────────────────────────────────────────────────────────


class TestCreateManualProfile:
    def test_nvidia_profile(self):
        profile = create_manual_profile(vram_gb=24.0, ram_gb=64.0, gpu_vendor="nvidia")
        assert profile.gpu.vendor == GPUVendor.NVIDIA
        assert profile.gpu.vram_gb == 24.0
        assert profile.ram_gb == 64.0

    def test_apple_profile(self):
        profile = create_manual_profile(vram_gb=72.0, ram_gb=96.0, gpu_vendor="apple")
        assert profile.gpu.vendor == GPUVendor.APPLE

    def test_amd_profile(self):
        profile = create_manual_profile(vram_gb=16.0, gpu_vendor="amd")
        assert profile.gpu.vendor == GPUVendor.AMD

    def test_none_gpu(self):
        profile = create_manual_profile(vram_gb=0.0, gpu_vendor="none")
        assert profile.gpu.vendor == GPUVendor.NONE

    def test_unknown_vendor(self):
        profile = create_manual_profile(vram_gb=8.0, gpu_vendor="quantum")
        assert profile.gpu.vendor == GPUVendor.UNKNOWN

    def test_defaults(self):
        profile = create_manual_profile(vram_gb=8.0)
        assert profile.ram_gb == 16.0
        assert profile.gpu.vendor == GPUVendor.NVIDIA


class TestDetectHardware:
    def test_detect_hardware_caches(self):
        import router.hardware_detector as hw_mod

        hw_mod._cached_profile = None
        with patch.object(HardwareDetector, "detect") as mock_detect:
            mock_detect.return_value = create_manual_profile(8.0)
            result1 = detect_hardware()
            result2 = detect_hardware()
            # Should only call detect once (cached)
            mock_detect.assert_called_once()
            assert result1 is result2
        # Reset cache
        hw_mod._cached_profile = None
