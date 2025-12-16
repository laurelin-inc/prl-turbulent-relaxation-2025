# Email to Alex at Oxford Physics - Final Report

**Subject:** Gkeyll Vlasov simulation: extensive testing shows persistent lack of pitch-angle scattering

Dear Alex,

I'm writing with an update on the Vlasov-Maxwell simulation issue I mentioned. After extensive testing, I've identified a fundamental problem that I'm hoping you can help me understand.

## The Problem

I'm simulating turbulent relaxation of pressure anisotropy in a collisionless plasma (firehose-unstable state with T⊥/T∥ = 2.0). The system should relax from Δ = +0.5 to Δ = -0.5 via pitch-angle scattering, but **parallel velocity remains completely frozen** regardless of perturbation amplitude.

## What I've Tested

### Test 1: Original Production Run (15% perturbations)
- **Setup**: 8³ × 12³ Vlasov-Maxwell, 97 frames to t=96
- **Result**: σ(v∥) changed +0.001% (essentially frozen)
- **Spatial evolution**: Working correctly (density correlation 0.89)
- **Conclusion**: Spatial solver works, but NO pitch-angle scattering

### Test 2: Stronger Perturbations (50% perturbations)
- **Hypothesis**: Maybe 15% too weak to drive firehose instability
- **Setup**: Same resolution, increased `perturb_amplitude` from 0.15 to 0.50
- **Result**: σ(v∥) changed +0.000% over first 3 frames
- **Actually WORSE** than 15% case
- **Perpendicular velocity**: σ(v⊥) = 1.278 (vs 0.585 in old run) - clearly responding to stronger perturbations
- **Conclusion**: Increasing perturbations makes no difference to parallel velocity freezing

## The Diagnostic Data

**Velocity evolution (50% perturbation run):**
```
Frame 0 (t=0.0): σ(v∥)=0.649779, σ(v⊥)=1.277861
Frame 1 (t=1.5): σ(v∥)=0.649778, σ(v⊥)=1.277979
Frame 2 (t=3.0): σ(v∥)=0.649779, σ(v⊥)=1.277899
Change: Δσ(v∥) = 0.0000% (vs expected ~1%)
```

**Spatial evolution (both runs):**
- Density patterns evolve normally
- Turbulent cascade and damping work correctly
- Correlation between t=0 and t=96: 0.89 (clearly different)
- Standard deviation drops 86% as expected

## The Puzzle

This creates a confusing picture:
- ✅ **Spatial dynamics**: Density evolves, turbulence cascades
- ✅ **Perpendicular velocities**: Respond to stronger perturbations (2.2x increase in σ(v⊥))
- ❌ **Parallel velocity**: Completely frozen, independent of perturbation strength
- ❌ **Anisotropy**: Δ stuck at +0.47 (no relaxation)

## Setup Details

```lua
-- Gkeyll 2, CUDA/GPU build on A100
-- 3D Vlasov-Maxwell, periodic box (2π)³
-- Resolution: 8³ spatial × 12³ velocity
-- β = 1.0, B₀ = 1.0 (normalized)

elc = Vlasov.Species.new {
  charge = -1.0, mass = 1.0,
  init = anisotropic_biMaxwellian,  -- T_perp=0.8, T_par=0.4
  evolve = true
}

field = Vlasov.Field.new {
  init = B0_in_z + turbulent_perturbations,
  evolve = true
}
```

**Perturbations**: 26 Kolmogorov modes (k^-5/3), k ∈ [1,4]

**Known bug**: Field outputs show Bz=0, Pzz=0 (Gkeyll z-component output bug), but I've verified particles DO gyrate by checking velocity anisotropy in distribution files.

## Questions

1. **Is this expected Vlasov behavior?** Should collisionless Vlasov-Maxwell show pitch-angle scattering, or is that inherently a collisional process?

2. **Could this be a Gkeyll-specific issue?** The fact that perpendicular velocities respond but parallel doesn't suggests something unusual.

3. **Resolution sufficient?** Is 12³ velocity cells enough to capture wave-particle resonance? Or do I need 20³+?

4. **Alternative approaches?**
   - Should I try GS2 instead of Gkeyll?
   - Add explicit collision operator (ν/Ω ~ 0.01)?
   - Different initial condition (seed instability directly)?
   - Different perturbation spectrum (resonant k modes)?

## Why This Matters

I'm working on papers demonstrating turbulent relaxation via Lynden-Bell statistical mechanics. The theory predicts Δ_eq = -1/(2β) = -0.5, but I cannot validate this numerically because the system won't relax.

I have:
- Two failed Gkeyll runs (15% and 50% perturbations)
- ~11 hours of A100 GPU time invested
- Clean diagnostic showing the specific failure mode

Before investing more time debugging Gkeyll, I want to understand if this is:
- A fundamental physics limitation of collisionless Vlasov
- A Gkeyll implementation issue
- A parameter/resolution problem (solvable)
- Expected behavior (need different approach)

## Files Available

I can share:
- Full Gkeyll input files for both runs
- Distribution function data (3 frames, 1.1GB each)
- Diagnostic analysis scripts
- Detailed velocity/pressure evolution data

Any guidance would be enormously valuable. Should I persist with Gkeyll, switch to GS2, or try a fundamentally different approach?

Thank you for your expertise,
Joe

---

**P.S.** One additional detail: when I increase perturbations from 15% to 50%, perpendicular velocity width increases from σ(v⊥)=0.585 to σ(v⊥)=1.278 (2.2x), showing the system IS responding to stronger forcing. But parallel velocity σ(v∥) stays frozen at 0.6498 in both cases, suggesting something specific is blocking parallel dynamics.
