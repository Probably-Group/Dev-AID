---
name: dbus
version: 2.0.0
description: "D-Bus IPC on Linux for system service integration, signal handling, and inter-process communication."
risk_level: MEDIUM
---

# D-Bus Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-306: Missing Authentication**
- NEVER: System bus services without authentication
- ALWAYS: PolicyKit integration, verify caller credentials

**CWE-78: Method Injection**
- NEVER: Dynamic method names from untrusted input
- ALWAYS: Whitelist allowed methods, validate all parameters

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Policy Configuration (CWE-284)

**Principle:** Define explicit D-Bus policies. Default deny, allow specific methods.

```xml
<!-- ❌ WRONG - Overly permissive policy -->
<policy context="default">
  <allow send_destination="*"/>
  <allow receive_sender="*"/>
</policy>

<!-- ✅ CORRECT - Restrictive policy -->
<policy user="myapp">
  <allow own="com.company.MyApp"/>
  <allow send_destination="com.company.MyApp"/>
</policy>

<policy context="default">
  <deny own="com.company.MyApp"/>
  <deny send_destination="com.company.MyApp"/>
</policy>

<policy at_console="true">
  <allow send_destination="com.company.MyApp"
         send_interface="com.company.MyApp.Public"/>
</policy>
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all method arguments. Never trust client input.

```rust
// ❌ WRONG - No validation
fn set_value(&self, value: &str) -> Result<(), Error> {
    self.config.set(value);  // Unchecked input!
    Ok(())
}

// ✅ CORRECT - Validate all inputs
fn set_value(&self, value: &str) -> Result<(), Error> {
    if value.len() > MAX_VALUE_LENGTH {
        return Err(Error::InvalidArgument("Value too long"));
    }
    if !value.chars().all(|c| c.is_alphanumeric() || c == '_') {
        return Err(Error::InvalidArgument("Invalid characters"));
    }
    self.config.set(value);
    Ok(())
}
```

### 1.3 Caller Verification (CWE-863)

**Principle:** Verify caller identity for privileged operations.

### 1.4 Secret Handling (CWE-798)

**Principle:** Never send secrets over D-Bus without encryption.

### 1.5 Resource Limits (CWE-400)

**Principle:** Set message size limits. Implement rate limiting.

### 1.6 Error Disclosure (CWE-209)

**Principle:** Return generic errors. Don't leak internal details.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```toml
# Rust
[dependencies]
zbus = "4.0"
zvariant = "4.0"
tokio = { version = "1.35", features = ["rt-multi-thread", "macros"] }

# Python
dbus-next>=0.2.3
```

---

## 3. Code Patterns

### 3.1 WHEN creating a D-Bus service in Rust

```rust
// ❌ WRONG - No access control
use zbus::{interface, Connection};

struct MyService;

#[interface(name = "com.company.MyService")]
impl MyService {
    fn dangerous_operation(&self) -> String {
        // Anyone can call this!
        do_dangerous_thing()
    }
}

// ✅ CORRECT - D-Bus service with access control
use zbus::{interface, Connection, MessageHeader, fdo};
use std::sync::Arc;
use tokio::sync::RwLock;

const MAX_MESSAGE_SIZE: usize = 1024 * 1024;  // 1MB
const MAX_CALLS_PER_MINUTE: u32 = 60;

struct ServiceState {
    config: Config,
    call_counts: std::collections::HashMap<String, (u32, std::time::Instant)>,
}

struct MyService {
    state: Arc<RwLock<ServiceState>>,
    connection: Connection,
}

#[interface(name = "com.company.MyService")]
impl MyService {
    /// Public method - available to all
    async fn get_version(&self) -> fdo::Result<String> {
        Ok(env!("CARGO_PKG_VERSION").to_string())
    }

    /// Protected method - requires caller verification
    async fn get_config(
        &self,
        #[zbus(header)] header: MessageHeader<'_>,
        key: &str,
    ) -> fdo::Result<String> {
        // Rate limiting
        self.check_rate_limit(&header).await?;

        // Input validation
        if key.len() > 256 {
            return Err(fdo::Error::InvalidArgs("Key too long".into()));
        }
        if !key.chars().all(|c| c.is_alphanumeric() || c == '.') {
            return Err(fdo::Error::InvalidArgs("Invalid key format".into()));
        }

        // Verify caller is authorized
        self.verify_caller(&header, Permission::ReadConfig).await?;

        let state = self.state.read().await;
        state.config.get(key)
            .map(|v| v.to_string())
            .ok_or_else(|| fdo::Error::Failed("Key not found".into()))
    }

    /// Privileged method - requires elevated permissions
    async fn set_config(
        &self,
        #[zbus(header)] header: MessageHeader<'_>,
        key: &str,
        value: &str,
    ) -> fdo::Result<()> {
        // Rate limiting
        self.check_rate_limit(&header).await?;

        // Input validation
        if key.len() > 256 || value.len() > 4096 {
            return Err(fdo::Error::InvalidArgs("Input too long".into()));
        }

        // Require elevated permissions
        self.verify_caller(&header, Permission::WriteConfig).await?;

        let mut state = self.state.write().await;
        state.config.set(key, value);
        Ok(())
    }
}

impl MyService {
    async fn verify_caller(
        &self,
        header: &MessageHeader<'_>,
        permission: Permission,
    ) -> fdo::Result<()> {
        let sender = header.sender()
            .ok_or_else(|| fdo::Error::Failed("No sender".into()))?;

        // Get caller's UID via D-Bus daemon
        let creds = self.connection
            .call_method(
                Some("org.freedesktop.DBus"),
                "/org/freedesktop/DBus",
                Some("org.freedesktop.DBus"),
                "GetConnectionUnixUser",
                &(sender.as_str(),),
            )
            .await?;

        let uid: u32 = creds.body().deserialize()?;

        // Check permission
        match permission {
            Permission::ReadConfig => {
                // Allow any local user
                Ok(())
            }
            Permission::WriteConfig => {
                // Only allow root or app user
                if uid == 0 || uid == APP_UID {
                    Ok(())
                } else {
                    Err(fdo::Error::AccessDenied("Elevated permissions required".into()))
                }
            }
        }
    }

    async fn check_rate_limit(&self, header: &MessageHeader<'_>) -> fdo::Result<()> {
        let sender = header.sender()
            .map(|s| s.to_string())
            .unwrap_or_default();

        let mut state = self.state.write().await;
        let now = std::time::Instant::now();

        let (count, last_reset) = state.call_counts
            .entry(sender.clone())
            .or_insert((0, now));

        if now.duration_since(*last_reset) > std::time::Duration::from_secs(60) {
            *count = 0;
            *last_reset = now;
        }

        *count += 1;

        if *count > MAX_CALLS_PER_MINUTE {
            return Err(fdo::Error::LimitsExceeded("Rate limit exceeded".into()));
        }

        Ok(())
    }
}

#[derive(Clone, Copy)]
enum Permission {
    ReadConfig,
    WriteConfig,
}
```

### 3.2 WHEN creating a D-Bus client

```rust
// ❌ WRONG - No error handling, blocking
let connection = Connection::session().unwrap();
let proxy = Proxy::new(&connection, "com.company.MyService", "/", "com.company.MyService").unwrap();
let result: String = proxy.call("GetConfig", &("key",)).unwrap();

// ✅ CORRECT - Async client with proper error handling
use zbus::{Connection, proxy};
use std::time::Duration;

#[proxy(
    interface = "com.company.MyService",
    default_service = "com.company.MyService",
    default_path = "/com/company/MyService"
)]
trait MyService {
    async fn get_version(&self) -> zbus::Result<String>;
    async fn get_config(&self, key: &str) -> zbus::Result<String>;
    async fn set_config(&self, key: &str, value: &str) -> zbus::Result<()>;

    #[zbus(signal)]
    async fn config_changed(&self, key: &str, value: &str) -> zbus::Result<()>;
}

pub struct MyServiceClient {
    proxy: MyServiceProxy<'static>,
}

impl MyServiceClient {
    pub async fn connect() -> Result<Self, Error> {
        let connection = Connection::session().await?;

        // Verify service is available
        let proxy = MyServiceProxy::new(&connection).await?;

        // Set timeout
        proxy.inner().set_property("Timeout", Duration::from_secs(30)).await?;

        Ok(Self { proxy })
    }

    pub async fn get_config(&self, key: &str) -> Result<String, Error> {
        // Validate input before sending
        if key.len() > 256 {
            return Err(Error::InvalidArgument("Key too long"));
        }

        self.proxy.get_config(key).await
            .map_err(|e| match e {
                zbus::Error::MethodError(name, _, _) if name == "org.freedesktop.DBus.Error.AccessDenied" => {
                    Error::PermissionDenied
                }
                zbus::Error::MethodError(name, _, _) if name == "org.freedesktop.DBus.Error.LimitsExceeded" => {
                    Error::RateLimited
                }
                _ => Error::Communication(e.to_string()),
            })
    }

    pub async fn watch_config_changes<F>(&self, callback: F) -> Result<(), Error>
    where
        F: Fn(&str, &str) + Send + 'static,
    {
        let mut stream = self.proxy.receive_config_changed().await?;

        tokio::spawn(async move {
            while let Some(signal) = stream.next().await {
                if let Ok(args) = signal.args() {
                    callback(args.key, args.value);
                }
            }
        });

        Ok(())
    }
}
```

### 3.3 WHEN configuring D-Bus policy

```xml
<!-- ✅ CORRECT - /etc/dbus-1/system.d/com.company.MyService.conf -->
<!DOCTYPE busconfig PUBLIC
 "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <!-- Only myapp user can own the service -->
  <policy user="myapp">
    <allow own="com.company.MyService"/>
  </policy>

  <!-- Root can do anything with the service -->
  <policy user="root">
    <allow send_destination="com.company.MyService"/>
    <allow receive_sender="com.company.MyService"/>
  </policy>

  <!-- Default policy: deny everything -->
  <policy context="default">
    <deny own="com.company.MyService"/>
    <deny send_destination="com.company.MyService"/>
  </policy>

  <!-- Console users can access public interface only -->
  <policy at_console="true">
    <allow send_destination="com.company.MyService"
           send_interface="com.company.MyService.Public"/>

    <!-- Allow introspection -->
    <allow send_destination="com.company.MyService"
           send_interface="org.freedesktop.DBus.Introspectable"/>

    <allow send_destination="com.company.MyService"
           send_interface="org.freedesktop.DBus.Properties"/>
  </policy>

  <!-- Specific group can access config interface -->
  <policy group="myapp-admins">
    <allow send_destination="com.company.MyService"
           send_interface="com.company.MyService.Config"/>
  </policy>

  <!-- Message size limits -->
  <limit name="max_message_size">1000000</limit>
  <limit name="max_message_unix_fds">16</limit>

  <!-- Connection limits -->
  <limit name="max_connections_per_user">100</limit>
  <limit name="max_pending_service_starts">100</limit>
</busconfig>
```

### 3.4 WHEN using D-Bus with Python

```python
# ❌ WRONG - No error handling, synchronous
from dbus_next.aio import MessageBus

bus = MessageBus().connect_sync()
introspection = bus.introspect_sync('com.company.MyService', '/com/company/MyService')
proxy = bus.get_proxy_object('com.company.MyService', '/com/company/MyService', introspection)
result = proxy.get_interface('com.company.MyService').call_get_config_sync('key')

# ✅ CORRECT - Async client with validation
from dbus_next.aio import MessageBus
from dbus_next import BusType, Variant
from typing import Optional
import asyncio

class MyServiceClient:
    MAX_KEY_LENGTH = 256
    MAX_VALUE_LENGTH = 4096
    TIMEOUT = 30.0

    def __init__(self):
        self._bus: Optional[MessageBus] = None
        self._interface = None

    async def connect(self, bus_type: BusType = BusType.SESSION) -> None:
        """Connect to the D-Bus service."""
        self._bus = await MessageBus(bus_type=bus_type).connect()

        # Verify service exists
        try:
            introspection = await asyncio.wait_for(
                self._bus.introspect('com.company.MyService', '/com/company/MyService'),
                timeout=self.TIMEOUT,
            )
        except asyncio.TimeoutError:
            raise ConnectionError("Service not responding")
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

        proxy = self._bus.get_proxy_object(
            'com.company.MyService',
            '/com/company/MyService',
            introspection,
        )
        self._interface = proxy.get_interface('com.company.MyService')

    async def get_config(self, key: str) -> str:
        """Get a configuration value."""
        if not self._interface:
            raise RuntimeError("Not connected")

        # Validate input
        if len(key) > self.MAX_KEY_LENGTH:
            raise ValueError("Key too long")
        if not key.replace('.', '').replace('_', '').isalnum():
            raise ValueError("Invalid key format")

        try:
            return await asyncio.wait_for(
                self._interface.call_get_config(key),
                timeout=self.TIMEOUT,
            )
        except Exception as e:
            # Map D-Bus errors to Python exceptions
            error_name = getattr(e, 'type', '')
            if 'AccessDenied' in error_name:
                raise PermissionError("Access denied")
            if 'LimitsExceeded' in error_name:
                raise RuntimeError("Rate limit exceeded")
            raise

    async def watch_changes(self, callback) -> None:
        """Watch for configuration changes."""
        if not self._interface:
            raise RuntimeError("Not connected")

        def on_config_changed(key: str, value: str):
            # Validate before passing to callback
            if len(key) <= self.MAX_KEY_LENGTH and len(value) <= self.MAX_VALUE_LENGTH:
                callback(key, value)

        self._interface.on_config_changed(on_config_changed)

    async def close(self) -> None:
        """Close the connection."""
        if self._bus:
            self._bus.disconnect()
            self._bus = None
            self._interface = None


# Usage
async def main():
    client = MyServiceClient()
    try:
        await client.connect()
        value = await client.get_config("app.setting")
        print(f"Config value: {value}")
    except PermissionError:
        print("Permission denied")
    except ConnectionError as e:
        print(f"Connection failed: {e}")
    finally:
        await client.close()
```

### 3.5 WHEN creating a systemd service file

```ini
# ✅ CORRECT - /etc/systemd/system/myapp-dbus.service
[Unit]
Description=MyApp D-Bus Service
After=dbus.service
Requires=dbus.service

[Service]
Type=dbus
BusName=com.company.MyService
ExecStart=/usr/bin/myapp-service

# Security hardening
User=myapp
Group=myapp

# Capabilities
CapabilityBoundingSet=
NoNewPrivileges=yes

# Filesystem restrictions
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
ReadWritePaths=/var/lib/myapp

# Network restrictions (if not needed)
PrivateNetwork=yes

# System call filtering
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

# Resource limits
LimitNOFILE=1024
MemoryMax=256M
CPUQuota=50%

# Restart policy
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
Alias=dbus-com.company.MyService.service
```

---

## 4. Anti-Patterns

**NEVER:**
- Allow `send_destination="*"` in policies
- Skip caller verification for privileged methods
- Trust D-Bus message content without validation
- Send secrets over D-Bus unencrypted
- Use synchronous D-Bus calls in async code
- Expose internal error details in responses
- Allow unlimited message sizes
- Skip rate limiting for public interfaces

---

## 5. Testing

**ALWAYS test D-Bus services:**

```bash
#!/bin/bash
# Test D-Bus service

set -euo pipefail

SERVICE="com.company.MyService"
OBJECT="/com/company/MyService"
INTERFACE="com.company.MyService"

# Test service is running
dbus-send --session --print-reply \
  --dest=org.freedesktop.DBus / org.freedesktop.DBus.ListNames | \
  grep -q "$SERVICE" || echo "Service not running"

# Test public method
dbus-send --session --print-reply \
  --dest="$SERVICE" "$OBJECT" \
  "$INTERFACE.GetVersion"

# Test access control (should fail for unprivileged user)
if dbus-send --session --print-reply \
  --dest="$SERVICE" "$OBJECT" \
  "$INTERFACE.SetConfig" \
  string:"test.key" string:"value" 2>&1 | grep -q "AccessDenied"; then
  echo "Access control working"
else
  echo "WARNING: Access control may not be working"
fi

# Monitor signals
timeout 5 dbus-monitor "type='signal',interface='$INTERFACE'" || true
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any D-Bus code:**

- [ ] D-Bus policy file defines explicit permissions
- [ ] Default policy denies all access
- [ ] Caller verification for privileged methods
- [ ] Input validation on all method arguments
- [ ] Rate limiting implemented
- [ ] Message size limits configured
- [ ] Error responses don't leak internals
- [ ] Systemd service hardened
- [ ] Signals validated before processing
- [ ] Async patterns used (no blocking)
