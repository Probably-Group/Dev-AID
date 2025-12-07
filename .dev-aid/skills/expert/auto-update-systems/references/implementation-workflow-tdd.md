## 8. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_update_system.py
import pytest
from unittest.mock import patch
from update_manager import UpdateManager

class TestUpdateManager:
    @pytest.fixture
    def manager(self):
        return UpdateManager(current_version="1.0.0", update_endpoint="https://updates.example.com")

    @pytest.mark.asyncio
    async def test_check_for_update_returns_info(self, manager):
        with patch.object(manager, '_fetch_manifest') as mock:
            mock.return_value = {"version": "2.0.0", "signature": "valid_sig"}
            result = await manager.check_for_update()
            assert result.version == "2.0.0"

    @pytest.mark.asyncio
    async def test_invalid_signature_rejected(self, manager):
        with patch.object(manager, '_verify_signature', return_value=False):
            with pytest.raises(SecurityError, match="signature"):
                await manager.download_and_verify("https://...", "bad_sig")

    @pytest.mark.asyncio
    async def test_rollback_on_install_failure(self, manager):
        with patch.object(manager, '_install', side_effect=InstallError):
            with patch.object(manager, '_restore_backup') as mock_restore:
                with pytest.raises(InstallError):
                    await manager.install_update("/path/to/update")
                mock_restore.assert_called_once()
```

### Step 2: Implement Minimum to Pass

```python
# update_manager.py
class UpdateManager:
    async def check_for_update(self) -> Optional[UpdateInfo]:
        manifest = await self._fetch_manifest()
        if self._is_newer(manifest["version"]):
            return UpdateInfo(**manifest)
        return None

    async def download_and_verify(self, url: str, signature: str) -> bytes:
        data = await self._download(url)
        if not self._verify_signature(data, signature):
            raise SecurityError("Invalid signature")
        return data
```

### Step 3: Refactor and Optimize

Add delta updates, caching, and bandwidth management after tests pass.

### Step 4: Verify

```bash
pytest tests/test_update_system.py -v --tb=short
pytest tests/test_update_system.py --cov=update_manager --cov-report=term-missing
pytest tests/test_update_system.py -k "signature or rollback" -v
```

---

