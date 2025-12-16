#!/usr/bin/env python3
"""
Test: Do collisions (ν/Ω = 0.01) enable pitch-angle scattering?

Compare velocity evolution between:
- v2 (50% perturbations, NO collisions): σ(v∥) frozen at 0.6498
- v3 (15% perturbations + collisions): σ(v∥) should evolve if collisions work
"""

import numpy as np
import sys
sys.path.insert(0, '/root/postgkyl')
import postgkyl as pg

def compute_velocity_widths(f_data):
    """Compute σ(v∥) and σ(v⊥) from distribution function"""
    bounds = f_data.get_bounds()
    cells = f_data.get_num_cells()

    lower = bounds[0]
    upper = bounds[1]

    # Spatial grid
    Nx, Ny, Nz = cells[0], cells[1], cells[2]
    dx = (upper[0] - lower[0]) / Nx
    dy = (upper[1] - lower[1]) / Ny
    dz = (upper[2] - lower[2]) / Nz
    dV_spatial = dx * dy * dz

    # Velocity grid
    Nvx, Nvy, Nvz = cells[3], cells[4], cells[5]
    vx_min, vy_min, vz_min = lower[3], lower[4], lower[5]
    vx_max, vy_max, vz_max = upper[3], upper[4], upper[5]

    dvx = (vx_max - vx_min) / Nvx
    dvy = (vy_max - vy_min) / Nvy
    dvz = (vz_max - vz_min) / Nvz
    dv = dvx * dvy * dvz

    # Create velocity meshgrids
    vx = np.linspace(vx_min + dvx/2, vx_max - dvx/2, Nvx)
    vy = np.linspace(vy_min + dvy/2, vy_max - dvy/2, Nvy)
    vz = np.linspace(vz_min + dvz/2, vz_max - dvz/2, Nvz)

    VX, VY, VZ = np.meshgrid(vx, vy, vz, indexing='ij')

    # Get distribution
    values = f_data.get_values()
    if len(values.shape) == 7:
        f = values[:, :, :, :, :, :, 0]
    else:
        f = values

    # Compute velocity moments
    v_par_mean = np.sum(VZ * f, axis=(3,4,5)) * dv / (np.sum(f, axis=(3,4,5)) * dv + 1e-30)
    v_par_sq = np.sum(VZ**2 * f, axis=(3,4,5)) * dv / (np.sum(f, axis=(3,4,5)) * dv + 1e-30)
    v_par_std = np.sqrt(np.maximum(0, v_par_sq - v_par_mean**2))

    v_perp_sq = np.sum((VX**2 + VY**2) * f, axis=(3,4,5)) * dv / (np.sum(f, axis=(3,4,5)) * dv + 1e-30)
    v_perp_std = np.sqrt(v_perp_sq)

    # Spatially average
    total_volume = (upper[0]-lower[0])*(upper[1]-lower[1])*(upper[2]-lower[2])

    v_par_std_avg = np.sum(v_par_std) * dV_spatial / total_volume
    v_perp_std_avg = np.sum(v_perp_std) * dV_spatial / total_volume

    return v_par_std_avg, v_perp_std_avg

def main():
    print("="*80)
    print("  COLLISION OPERATOR TEST: v3 (ν/Ω = 0.01)")
    print("="*80)
    print()

    # Find available frames
    import glob
    frames = sorted(glob.glob('gkeyll_papers_3_5_PRODUCTION_v3-elc_[0-9]*.gkyl'))
    frame_numbers = [int(f.split('_')[-1].replace('.gkyl', '')) for f in frames]

    print(f"Found {len(frames)} frames: {frame_numbers}")
    print()

    if len(frames) < 2:
        print("ERROR: Need at least 2 frames for comparison")
        return

    results = {}

    for frame_file in frames[:10]:  # Analyze first 10 frames max
        frame_num = int(frame_file.split('_')[-1].replace('.gkyl', ''))
        print(f"Loading frame {frame_num}...")

        data = pg.data.GData(frame_file)
        time = data.ctx['time']

        v_par_std, v_perp_std = compute_velocity_widths(data)

        results[frame_num] = {
            'time': time,
            'v_par_std': v_par_std,
            'v_perp_std': v_perp_std
        }

        print(f"  Frame {frame_num} (t={time:.2f}): σ(v∥)={v_par_std:.6f}, σ(v⊥)={v_perp_std:.6f}")

    print()
    print("="*80)
    print("  CRITICAL TEST: Do collisions enable pitch-angle scattering?")
    print("="*80)
    print()

    # Compare first and last available frames
    first_frame = min(results.keys())
    last_frame = max(results.keys())

    v_par_0 = results[first_frame]['v_par_std']
    v_par_N = results[last_frame]['v_par_std']

    delta_v_par = v_par_N - v_par_0
    percent_change = 100 * delta_v_par / v_par_0

    print(f"Frame {first_frame} (t={results[first_frame]['time']:.1f}): σ(v∥) = {v_par_0:.6f}")
    print(f"Frame {last_frame} (t={results[last_frame]['time']:.1f}): σ(v∥) = {v_par_N:.6f}")
    print(f"Change: Δσ(v∥) = {delta_v_par:.6e} ({percent_change:+.3f}%)")
    print()

    # Compare with previous attempts
    print("Comparison with previous attempts:")
    print("  v1 (15%, no collisions): σ(v∥) changed +0.001% over 96 time units (FROZEN)")
    print("  v2 (50%, no collisions): σ(v∥) changed +0.000% over 3 time units (FROZEN)")
    print(f"  v3 (15% + collisions):  σ(v∥) changed {percent_change:+.3f}% over {results[last_frame]['time']:.1f} time units")
    print()

    print("="*80)
    print("  VERDICT")
    print("="*80)
    print()

    threshold = 0.1  # 0.1% change is significant

    if abs(percent_change) > threshold:
        print("✅ SUCCESS: Collisions enable pitch-angle scattering!")
        print()
        print(f"The {abs(percent_change):.3f}% change is {abs(percent_change/0.001):.0f}x larger than v1.")
        print("This indicates that ν/Ω = 0.01 successfully breaks μ-conservation.")
        print()
        print("CONCLUSION: Collision operator approach WORKS!")
        print("Continue to full 100 time unit production run.")
        print()
        print("Expected relaxation timescale: τ ~ 1/ν ~ 100 time units")
        print("Full run should show Δ(t) relaxing from +0.5 toward -0.5")
    else:
        print("❌ STILL FROZEN: Collisions did not enable scattering")
        print()
        print(f"The {abs(percent_change):.3f}% change is too small (threshold: {threshold}%).")
        print("Pitch-angle scattering is still absent.")
        print()
        print("DIAGNOSIS:")
        print("  - ν/Ω = 0.01 may be too weak")
        print("  - Try increasing to ν/Ω = 0.05")
        print("  - Or switch to different approach (PIC code, hybrid method)")
        print()
        print("NEXT STEPS:")
        print("  - Modify collision_freq from 0.01 to 0.05")
        print("  - Re-run test")
        print("  - If still fails, consider PIC or accept theoretical curves")

    print()
    print("="*80)

    # Save results to file for easy reference
    with open('v3_test_results.txt', 'w') as f:
        f.write(f"v3 Collision Test Results\n")
        f.write(f"========================\n\n")
        f.write(f"Collision frequency: ν/Ω = 0.01\n")
        f.write(f"Frames analyzed: {first_frame} to {last_frame}\n")
        f.write(f"Time range: {results[first_frame]['time']:.1f} to {results[last_frame]['time']:.1f}\n\n")
        f.write(f"σ(v∥) evolution:\n")
        f.write(f"  Initial:  {v_par_0:.6f}\n")
        f.write(f"  Final:    {v_par_N:.6f}\n")
        f.write(f"  Change:   {percent_change:+.3f}%\n\n")
        if abs(percent_change) > threshold:
            f.write(f"VERDICT: SUCCESS - Collisions enable pitch-angle scattering\n")
        else:
            f.write(f"VERDICT: FAILED - Still no scattering, need stronger collisions or different approach\n")

    print(f"Results saved to: v3_test_results.txt")

if __name__ == '__main__':
    main()
