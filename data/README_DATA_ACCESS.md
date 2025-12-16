# Simulation Data Access

## Data Location

All simulation data is stored in Google Cloud Storage:

**Bucket**: `gs://gkeyll-simulations-20251215/`

### Available Datasets

1. **v1_production/** - Original collisionless run (FROZEN)
   - 97 frames, t=0-96
   - Resolution: 8³ × 12³
   - Size: ~107 GB
   - Status: No relaxation (σ(v∥) frozen)

2. **v2_production/** - Strong forcing test (FROZEN)
   - 3 frames, t=0-3
   - 50% perturbations vs 15% in v1
   - Size: ~3.3 GB
   - Status: No relaxation (even worse than v1)

3. **v3_production/** - **Collision operator (SUCCESS!)** ⭐
   - 67 frames, t=0-100
   - Collision frequency ν/Ω = 0.01
   - Size: ~74 GB
   - Status: ✅ Full relaxation Δ: +0.5 → -0.5

## Downloading Data

### Prerequisites

Install Google Cloud SDK:
```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login
```

### Download v3 Production Data (Recommended)

```bash
# Download all v3 frames (~74 GB)
gsutil -m cp -r gs://gkeyll-simulations-20251215/v3_production/ ./

# Or download specific frames
gsutil cp gs://gkeyll-simulations-20251215/v3_production/gkeyll_papers_3_5_PRODUCTION_v3-elc_0.gkyl ./
gsutil cp gs://gkeyll-simulations-20251215/v3_production/gkeyll_papers_3_5_PRODUCTION_v3-elc_10.gkyl ./
```

### Download v1 Data (For Comparison)

```bash
# Download v1 frozen run
gsutil -m cp -r gs://gkeyll-simulations-20251215/v1_production/ ./
```

## File Format

Simulation output files are in Gkeyll binary format (`.gkyl`):

- **Distribution functions**: `*-elc_N.gkyl` (full 6D phase space, ~1.1 GB each)
- **Density moments**: `*-elc_M0_N.gkyl` (3D spatial, ~33 KB each)
- **Pressure moments**: `*-elc_M2ij_N.gkyl` (3D spatial tensor, ~193 KB each)

Where `N` is the frame number (0-66 for v3).

## Reading Data

### Install postgkyl

```bash
# Clone postgkyl
git clone https://github.com/ammarhakim/postgkyl.git
cd postgkyl

# Install with pip
pip install -e .
```

### Extract Anisotropy

```python
import numpy as np
import postgkyl as pg

# Load distribution function
data = pg.data.GData('gkeyll_papers_3_5_PRODUCTION_v3-elc_0.gkyl')

# Get grid info
bounds = data.get_bounds()
cells = data.get_num_cells()

# Extract velocity moments
# ... (see analysis scripts for full extraction)

# Compute anisotropy
Delta = (P_perp - P_par) / (2 * P_par)
```

See `../analysis/test_v3_velocity_evolution.py` for complete analysis pipeline.

## Data Structure

Each frame contains:

```
Frame N (t = N × Δt):
├── elc_N.gkyl           # Distribution f(x,y,z,vx,vy,vz)
├── elc_M0_N.gkyl        # Density n(x,y,z)
├── elc_M1i_N.gkyl       # Momentum density (x,y,z components)
└── elc_M2ij_N.gkyl      # Pressure tensor (6 components)
```

### Pressure Tensor Components

From M2ij files:
- `M2xx`, `M2yy`: Perpendicular pressure components
- `M2zz`: Parallel pressure (B field in ẑ direction)
- `M2xy`, `M2xz`, `M2yz`: Off-diagonal components

### Computing Anisotropy

```python
# From pressure tensor
P_perp = (M2xx + M2yy) / 2  # Average perpendicular
P_par = M2zz                 # Parallel to B
Delta = (P_perp - P_par) / (2 * P_par)

# Expected values:
# Initial: Delta ≈ +0.5 (T_perp/T_par = 2.0)
# Final: Delta ≈ -0.5 (Lynden-Bell equilibrium for β=1)
```

## Quick Start Example

```python
#!/usr/bin/env python3
"""
Extract anisotropy time series from v3 production run
"""
import numpy as np
import postgkyl as pg
import glob

# Find all frames
frames = sorted(glob.glob('v3_production/gkeyll_*_v3-elc_M2ij_*.gkyl'))

times = []
deltas = []

for frame_file in frames:
    # Load pressure tensor
    data = pg.data.GData(frame_file)
    time = data.ctx['time']

    # Extract pressure components
    values = data.get_values()
    P_xx = values[:,:,:,0,0]  # M2xx
    P_yy = values[:,:,:,1,0]  # M2yy
    P_zz = values[:,:,:,2,0]  # M2zz

    # Spatially average
    P_perp = np.mean((P_xx + P_yy) / 2)
    P_par = np.mean(P_zz)

    # Compute anisotropy
    Delta = (P_perp - P_par) / (2 * P_par)

    times.append(time)
    deltas.append(Delta)

    print(f"t={time:.1f}: Δ={Delta:.4f}")

# Save results
np.savez('v3_relaxation.npz', times=times, deltas=deltas)
```

## Data Citations

If you use this data, please cite:

```bibtex
@misc{finberg2025data,
  author = {Finberg, Joseph},
  title = {Vlasov-Maxwell Simulation Data: Anisotropy Relaxation with Collision Operator},
  year = {2025},
  publisher = {Google Cloud Storage},
  url = {gs://gkeyll-simulations-20251215/v3_production/}
}
```

## Storage Information

- **Provider**: Google Cloud Storage
- **Region**: us-central1
- **Access**: Public (read-only)
- **Retention**: Permanent (part of published research)

## Contact

For data access issues:
- Joseph Finberg: jsf2178@columbia.edu
- Create issue: https://github.com/laurelin-inc/prl-turbulent-relaxation-2025/issues
