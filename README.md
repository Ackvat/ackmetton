# ackmetton

**A base library for robotics, unmanned vehicles, and automation — compatible with Python and MicroPython.**

ackmetton provides a modular, reusable foundation of math primitives, control algorithms, logging, and platform abstraction designed to run the same code across CPython and MicroPython environments with minimal friction.

## Features

### Math Library (`ackmetton.mathlib`)

| Component | Description |
|---|---|
| `clamp`, `map`, `deadzone`, `low_pass`, `amplitude_impedance` | Utility functions for signal conditioning and filtering |
| `sin`, `cos`, `acos` | Convenience wrappers around `math` |
| `Vector2` | 2D vector with arithmetic, magnitude, normal, unit, dot, cross |
| `Vector3` | 3D vector with arithmetic, magnitude, normal, unit, dot, cross |
| `Basis` | Orthonormal basis container (3×3) |
| `Quaternion` | Full quaternion algebra — multiplication, conjugation, rotation, axis-angle construction, Euler angles, rotation matrix, basis extraction |
| `PID` | Proportional-Integral-Derivative controller with integral clamping, set-point tracking, and reset |

### Utilities (`ackmetton.utils`)

| Component | Description |
|---|---|
| `TimeStamp` | High-resolution timing with configurable unit mask, delta measurement |

### Base Classes (`ackmetton.base`)

| Component | Description |
|---|---|
| `Base` | Root class with name attribute shared by all library classes |
| `Logger` | File-based logging with leveled output, auto-rotating directory creation |
| `LogWrap` | Proxy that forwards log calls scoped to an object name |
| `Printer` | Timestamped console printer with configurable output level |
| `Logged` | Combined logging + printing class that bridges Logger and Printer |

### Platform Abstraction (`ackmetton.platform`)

| Function | Description |
|---|---|
| `is_micropython()` | Detect MicroPython runtime |
| `is_python()` | Detect CPython on Linux |

### Enums (`ackmetton.enums`)

| Enum | Description |
|---|---|
| `FEED_LEVELS` | Log/print severity levels (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL) |

## Requirements

- Python ≥ 3.14 **or** MicroPython (any version)
- No external dependencies

## Installation

```bash
pip install ackmetton
```

Or copy `src/ackmetton/` directly into your project for embedded/MicroPython targets.

### Installing from source

```bash
git clone https://github.com/<your-org>/ackmetton.git
cd ackmetton
pip install .
```

## Quick Start

```python
from ackmetton.mathlib import Vector3, Quaternion, PID, clamp

# Vector math
v = Vector3(1, 2, 3) + Vector3(4, 5, 6)
print(v.normal())

# Quaternion rotation
q = Quaternion.from_axis_angle(90, Vector3(0, 1, 0))

# PID control
pid = PID(kp=2.0, ki=0.1, kd=0.05, set_point=100)
output = pid.update(measured_value=85, dt=0.01)
```

## MicroPython Compatibility

ackmetton is designed for cross-platform use. Modules that rely on CPython stdlib (notably `Logger` which uses `logging`) raise a clear `ImportError` when imported on MicroPython. All other modules — `mathlib`, `utils`, `platform`, `enums`, and the core `Base`/`Printer` classes — work unchanged on MicroPython.

## Project Structure

```
src/
└── ackmetton/
    ├── __init__.py
    ├── base.py        # Base, Logger, LogWrap, Printer
    ├── enums.py       # FEED_LEVELS
    ├── mathlib.py     # Math utilities, vectors, quaternions, PID
    ├── platform.py    # is_micropython(), is_python()
    └── utils.py       # TimeStamp
```

## License

MIT
