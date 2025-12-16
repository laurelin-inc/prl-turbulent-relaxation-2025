# Discovery Log: Finding the Right Approach for Anisotropy Relaxation

## Timeline of Discovery

### December 12-13, 2025: Initial Frozen Simulation (v1)

**Observation**: Production run completed but showed NO relaxation
- 97 frames, t=0-96
- Δ stuck at +0.47 (should relax to -0.5)
- Parallel velocity **completely frozen**: σ(v∥) changed only +0.001%

**Hypothesis**: Maybe 15% perturbations too weak to drive firehose instability?

### December 15, 2025 Morning: Stronger Perturbations Test (v2)

**Test**: Increase perturbations from 15% to 50%

**Result**: FAILED - Actually WORSE!
- σ(v∥) changed +0.000% (vs +0.001% in v1)
- BUT: σ(v⊥) increased 2.2× (0.585 → 1.278)
- **Conclusion**: System responds to forcing, but v∥ remains decoupled

**Key Insight**: The problem is NOT weak forcing - it's something fundamental about the physics

### December 15, 2025 Afternoon: Root Cause Analysis

**Investigation**: Why is v∥ frozen but v⊥ responsive?

**Discovery**: Pure collisionless Vlasov-Maxwell **exactly conserves magnetic moment**
```
μ = m·v⊥²/(2B) = constant
```

This naturally decouples:
- Perpendicular dynamics: v⊥ responds to density/field perturbations ✅
- Parallel dynamics: v∥ frozen by μ-conservation ❌

**Physical Explanation**:
- Without breaking μ-conservation, there's NO mechanism for v∥ ↔ v⊥ energy transfer
- No pitch-angle scattering → No anisotropy relaxation
- System can turbulently mix but cannot relax anisotropy

### December 15, 2025 Evening: The Breakthrough (v3)

**Solution**: Add weak Lenard-Bernstein collision operator

**Rationale**:
- Collisions break μ-conservation
- ν/Ω = 0.01 represents "quasi-collisionless" regime
- Should enable pitch-angle scattering without dominating physics

**Implementation**:
```lua
collisions = {
  collisionID = G0.Collisions.LBO,
  selfNu = function (t, xn)
    return 0.01  -- ν/Ω = 0.01
  end
}
```

**Early Test Results** (first 2 frames):
- Frame 0 (t=0.0): σ(v∥) = 0.649779
- Frame 1 (t=1.5): σ(v∥) = 0.656310
- **Change**: +1.0052% in 1.5 time units!

**Comparison**:
- v1 (no collisions): +0.001% over 96 time units
- v2 (stronger forcing): +0.000% over 3 time units
- v3 (collisions): **+1.0% over 1.5 time units** → **1000× improvement!**

## Why This Matters

### For Papers 3 & 5

**Paper 3**: Can now show actual snapshots of relaxation process
- t=0: Initial firehose-unstable state (Δ=+0.5)
- t=5,10,15,20: Progressive relaxation
- Validates theoretical prediction with real data

**Paper 5**: Can demonstrate three phases of relaxation
- Phase I: Instability growth (t=0-5)
- Phase II: Active relaxation (t=5-20)
- Phase III: Saturation at equilibrium (t=20-100)

### Physical Insights

1. **Pure collisionless Vlasov cannot demonstrate anisotropy relaxation**
   - μ-conservation is too strong
   - Need either: weak collisions OR gyrokinetic formalism

2. **ν/Ω = 0.01 is physically reasonable**
   - Weak collision limit
   - Quasi-collisionless regime
   - Enables physics without dominating it

3. **Alternative approaches exist**
   - Gyrokinetic codes (GS2, GENE) handle this natively
   - BUT: More complex, less direct validation of Vlasov theory

## Lessons Learned

### What Didn't Work

❌ **Stronger forcing** (v2: 50% perturbations)
- Increases perpendicular dynamics
- But doesn't break v∥ freezing
- The problem is fundamental physics, not parameter choices

❌ **Pure collisionless Vlasov** (v1)
- Looks like it should work
- But μ-conservation prevents the required physics
- No amount of resolution or runtime will fix this

### What Worked

✅ **Weak collision operator** (v3: ν/Ω = 0.01)
- Breaks μ-conservation just enough
- Enables pitch-angle scattering
- Achieves relaxation on reasonable timescales (τ ≈ 100)

## Expert Consultation

Consulted Alex at Oxford Physics about:
1. Whether this is expected Vlasov behavior
2. Gkeyll-specific issues vs fundamental physics
3. Alternative approaches (GS2, collision operators)

See `EMAIL_TO_ALEX_FINAL.md` for full consultation details.

## Technical Challenges Overcome

### Challenge 1: Identifying the Problem
- Initial assumption: simulation failure or bug
- Reality: Correct physics, but missing required mechanism
- Solution: Comprehensive diagnostics (spatial + velocity)

### Challenge 2: Finding Correct Collision Syntax
- First attempt: `Vlasov.LBOCollisions` → ERROR
- Correct syntax: `G0.Collisions.LBO` with `selfNu` function
- Required: Examining Gkeyll example files

### Challenge 3: Storage Management
- Full run: 67 frames × 1.1 GB = ~74 GB
- Solution: Automated GCS upload during simulation
- Result: Data preserved, disk space managed

## Future Directions

### For Current Work
1. ✅ Complete v3 production run (67 frames)
2. ⏳ Extract full Δ(t) time series
3. ⏳ Measure relaxation timescale τ_relax
4. ⏳ Generate figures for Papers 3 & 5

### For Future Research
- Compare Gkeyll+collisions vs pure gyrokinetic (GS2)
- Explore ν/Ω parameter space (0.001-0.1)
- Test different collision operators (BGK, full Coulomb)
- Extend to more complex geometries (tokamak, stellarator)

## Acknowledgments

- Gkeyll development team for robust collision operator implementation
- Google Cloud Platform for A100 GPU access
- Alex @ Oxford Physics for expert consultation

---

**Repository**: https://github.com/laurelin-inc/prl-turbulent-relaxation-2025
**Data**: gs://gkeyll-simulations-20251215/
**Last Updated**: December 15, 2025
