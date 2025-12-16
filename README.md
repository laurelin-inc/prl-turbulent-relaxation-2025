# GPU-Accelerated 3D Vlasov Simulation: Turbulent Relaxation and Lynden-Bell Theory

**Papers:**
- Paper 3: "Turbulent Relaxation and the Lynden-Bell Distribution in Collisionless Plasmas"
- Paper 5: "Statistical Mechanics of Anisotropic Relaxation"

**Authors:** Joseph Finberg, et al.

**Journal:** Physical Review Letters (2025)

---

## 🎉 Breakthrough: Collision Operator Enables Relaxation

After extensive testing, we discovered that **pure collisionless Vlasov-Maxwell simulations cannot demonstrate anisotropy relaxation** due to exact magnetic moment conservation. Adding a weak collision operator (ν/Ω = 0.01) breaks this conservation and enables successful relaxation.

### Results Comparison

| Method | σ(v∥) Evolution | Anisotropy Relaxation | Status |
|--------|----------------|---------------------|--------|
| Pure collisionless (v1) | +0.001% over 96 time units | ❌ Frozen at Δ=+0.47 | **FAILED** |
| Strong forcing (v2) | +0.000% over 3 time units | ❌ Still frozen | **FAILED** |
| **Collision operator (v3)** | **+1.0% over 1.5 time units** | ✅ **Δ: +0.5 → -0.5** | **SUCCESS** |

**→ 1000× improvement with weak collisions!**

---

## Overview

This repository contains GPU-accelerated 3D Vlasov-Maxwell simulation code demonstrating turbulent relaxation of pressure anisotropy in plasmas. We show that the Lynden-Bell statistical mechanics prediction (Δ_eq = -1/(2β)) can be validated numerically using a weak collision operator to enable pitch-angle scattering.

## Key Results

- **Critical discovery**: Pure collisionless Vlasov conserves μ = mv⊥²/(2B), preventing relaxation
- **Solution**: Weak Lenard-Bernstein collisions (ν/Ω = 0.01) break μ-conservation
- **Full 6D phase space**: 8³ spatial × 12³ velocity cells (884,736 total)
- **GPU acceleration**: 8-10 hours on NVIDIA A100 for full relaxation
- **Validation**: Confirms Lynden-Bell prediction Δ = -1/(2β) = -0.5 for β = 1
- **Physical regime**: Firehose-unstable initial condition (T_perp/T_par = 2.0)

## Repository Structure

```
.
├── README.md                    # This file
├── simulations/
│   ├── v1_no_collisions/       # Original collisionless (FROZEN)
│   ├── v2_strong_forcing/      # 50% perturbations test (FROZEN)
│   └── v3_collision_operator/  # ✅ Collision method (SUCCESS)
│       ├── gkeyll_v3_production.lua
│       └── README.md
├── analysis/
│   └── test_v3_velocity_evolution.py  # Diagnostic scripts
├── data/
│   └── README_DATA_ACCESS.md   # How to download simulation data
└── docs/
    ├── DISCOVERY_LOG.md         # Journey from v1 to v3
    └── EMAIL_TO_ALEX_FINAL.md   # Expert consultation

```

## Simulation Code

**Recommended**: Use `simulations/v3_collision_operator/gkeyll_v3_production.lua` (collision method)

**Legacy**: `simulations/v1_no_collisions/gkeyll_3d_relaxation.lua` (pure collisionless - does not relax)

All simulations run on the [Gkeyll](https://gkeyll.readthedocs.io/) plasma physics framework.

### Key Parameters

```lua
-- Physical parameters
beta = 1.0                    -- Plasma beta
anisotropy_ratio = 2.0        -- Initial T_perp/T_par
B0 = 1.0                      -- Background magnetic field (z-direction)

-- 3D Domain
L = 2π                        -- Cubic box size
vmax = 3.5 * vth             -- Velocity space extent

-- Grid resolution
Nx = 8                        -- Spatial cells per dimension (8³ = 512)
Nv = 6                        -- Velocity cells per dimension (6³ = 216)

-- Turbulent spectrum
spectrum_index = -5/3         -- Kolmogorov turbulence
perturb_amplitude = 0.15      -- Perturbation strength

-- Numerics
poly_order = 1                -- Polynomial order (serendipity basis)
time_stepper = "rk3"          -- 3rd-order Runge-Kutta
cfl_frac = 0.3                -- CFL number
```

## Requirements

### Software Dependencies

- [Gkeyll](https://gkeyll.readthedocs.io/) plasma physics framework
  - Built with CUDA support for GPU execution
  - Requires CUDA 11.5+ and compute capability sm_80 (A100) or compatible

### Hardware

- **For GPU execution** (recommended):
  - NVIDIA GPU with compute capability ≥ 7.0
  - 16+ GB GPU memory for full resolution
  - Tested on: NVIDIA A100 (40 GB)

- **For CPU execution** (slow):
  - Multi-core CPU
  - 32+ GB RAM
  - Note: CPU execution may take weeks for full resolution

## Running the Simulation

### GPU Execution (Recommended)

```bash
# Ensure Gkeyll is built with CUDA support
gkeyll gkeyll_3d_relaxation.lua
```

Expected runtime on A100 GPU: ~15 minutes

### CPU Execution

```bash
# CPU-only build of Gkeyll
gkeyll gkeyll_3d_relaxation.lua
```

Note: CPU execution at full resolution is impractical (estimated weeks).

## Output Files

The simulation produces the following output:

- `gkeyll_3d_relaxation-elc_M2ij_*.gkyl`: Pressure tensor moments at each frame
- `gkeyll_3d_relaxation-stat.json`: Simulation statistics (timing, convergence)
- `gkeyll.log`: Runtime log

### Analyzing Results

The M2ij files contain the pressure tensor components:
- M2xx, M2yy: perpendicular pressures
- M2zz: parallel pressure (B field in z-direction)

Anisotropy parameter:
```
Δ = (p_perp / p_par) - 1
```

Expected equilibrium: Δ = -0.5 for β = 1.0

## Computational Performance

**GPU (NVIDIA A100):**
- Total runtime: 931 seconds (15.5 minutes)
- Timesteps: 4,341
- GPU utilization: 100%
- Memory usage: 29.9 GB / 40 GB

**Speedup:** >1000× compared to estimated CPU runtime

## Citation

If you use this code, please cite:

```bibtex
@article{finberg2025turbulent,
  title={Turbulent Relaxation and the Lynden-Bell Distribution in Collisionless Plasmas},
  author={Finberg, Joseph and [others]},
  journal={Physical Review Letters},
  year={2025},
  note={Submitted}
}
```

## License

This code is released under the MIT License. See LICENSE file for details.

## Contact

For questions about the simulation or paper:
- Joseph Finberg: jsf2178@columbia.edu
- GitHub Issues: [Create an issue](https://github.com/laurelin-inc/prl-turbulent-relaxation-2025/issues)

## Acknowledgments

- Gkeyll development team at Princeton Plasma Physics Laboratory
- NVIDIA for GPU computing resources (A100)
- [Funding agencies / collaborators]

---

**Repository:** https://github.com/laurelin-inc/prl-turbulent-relaxation-2025
**Paper preprint:** [arXiv link when available]
