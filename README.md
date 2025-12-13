# GPU-Accelerated 3D Vlasov Simulation: Turbulent Relaxation and Lynden-Bell Theory

**Paper:** "Turbulent Relaxation and the Lynden-Bell Distribution in Collisionless Plasmas"

**Authors:** Joseph Finberg, et al.

**Journal:** Physical Review Letters (submitted 2025)

---

## Overview

This repository contains the GPU-accelerated 3D Vlasov-Maxwell simulation code used to validate the Lynden-Bell prediction for turbulent relaxation in collisionless plasmas. The simulation demonstrates that an initially anisotropic plasma distribution relaxes to an equilibrium state with anisotropy parameter Δ = -1/(2β) through violent relaxation driven by 3D turbulent fluctuations.

## Key Results

- **Full 6D phase space simulation**: 8³ spatial × 6³ velocity cells (110,592 total)
- **GPU acceleration**: 15.5 minutes on NVIDIA A100 (>1000× speedup vs CPU)
- **Validation**: Confirms Lynden-Bell prediction Δ = -1/(2β) for plasma beta β = 1
- **Physical regime**: Firehose-unstable initial condition (T_perp/T_par = 2.0)

## Simulation Code

The main simulation file is `gkeyll_3d_relaxation.lua`, which runs on the [Gkeyll](https://gkeyll.readthedocs.io/) plasma physics framework.

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
