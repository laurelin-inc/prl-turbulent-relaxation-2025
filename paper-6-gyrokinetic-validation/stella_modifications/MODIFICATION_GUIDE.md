# Stella Modification Guide: Anisotropic Temperature Support

**For:** Stella v0.8
**Purpose:** Enable anisotropic background distributions with separate parallel and perpendicular temperatures
**Use Case:** Testing Lynden-Bell pressure anisotropy predictions in gyrokinetic turbulence

---

## Overview

Standard Stella initializes with isotropic Maxwellian distributions:
```
F₀ ∝ exp(-E/T)  where E = mv∥²/2 + μB
```

These modifications enable anisotropic distributions:
```
F₀ ∝ exp(-mv∥²/(2T∥)) exp(-μB/T⊥)
```

This allows testing pressure anisotropy Δ = (T⊥ - T∥)/(2T∥).

---

## Files Modified

Three files in the Stella source tree require modification:

### 1. `grids/common_types.f90`

**Purpose:** Add anisotropic temperature fields to species data structure

**Location:** Line 69, in `type spec_type` definition

**Changes:**
```fortran
type spec_type
   integer :: nspec
   real :: z
   real :: mass
   real :: dens, temp
   !> Anisotropic temperature parameters for Lynden-Bell validation
   real :: tpar, tperp
   logical :: use_anisotropic_temp
   real :: tprim, fprim
   ...
end type spec_type
```

**What was added:**
- `tpar`: Parallel temperature (T∥)
- `tperp`: Perpendicular temperature (T⊥)
- `use_anisotropic_temp`: Flag to enable anisotropic initialization

---

### 2. `grids/species.f90`

**Purpose:** Read anisotropic parameters from input namelist

**Location:** Line ~50-60, in namelist definition

**Changes:**
```fortran
namelist /species_parameters/ z, mass, dens, &
         temp, tpar, tperp, use_anisotropic_temp, &
         tprim, fprim, vnew_ref, &
         type, bess_fac, &
         d2ndr2, d2Tdr2
```

**Location:** Line ~100-120, in initialization logic

**Changes:**
```fortran
! Initialize anisotropic temperature parameters
if (use_anisotropic_temp) then
   spec(is)%tpar = tpar
   spec(is)%tperp = tperp
   spec(is)%use_anisotropic_temp = .true.
else
   ! Default: isotropic
   spec(is)%tpar = temp
   spec(is)%tperp = temp
   spec(is)%use_anisotropic_temp = .false.
end if
```

**What was added:**
- Namelist parameters for `tpar`, `tperp`, `use_anisotropic_temp`
- Initialization logic with fallback to isotropic when flag is false

---

### 3. `grids/vpamu_grids.f90`

**Purpose:** Use separate T∥ and T⊥ in velocity-space distribution initialization

**Location:** Line ~830-845, in `maxwell_vpa` and `maxwell_mu` initialization

**Original code:**
```fortran
! Parallel Maxwell distribution
maxwell_vpa(ivpa, is) = exp(-vpa(ivpa)**2 * spec(is)%temp)

! Perpendicular Maxwell distribution
maxwell_mu(imu, is) = exp(-2.0 * mu(imu) * bmag(ia, iz) * spec(is)%temp)
```

**Modified code:**
```fortran
! Parallel Maxwell distribution
if (spec(is)%use_anisotropic_temp) then
   maxwell_vpa(ivpa, is) = exp(-vpa(ivpa)**2 * spec(is)%temp / spec(is)%tpar)
else
   maxwell_vpa(ivpa, is) = exp(-vpa(ivpa)**2 * spec(is)%temp)
end if

! Perpendicular Maxwell distribution
if (spec(is)%use_anisotropic_temp) then
   maxwell_mu(imu, is) = exp(-2.0 * mu(imu) * bmag(ia, iz) * spec(is)%temp / spec(is)%tperp)
else
   maxwell_mu(imu, is) = exp(-2.0 * mu(imu) * bmag(ia, iz) * spec(is)%temp)
end if
```

**What was changed:**
- Added conditional logic to use `tpar` for parallel direction
- Added conditional logic to use `tperp` for perpendicular direction
- Preserved backward compatibility when `use_anisotropic_temp = .false.`

---

## Installation Instructions

### Step 1: Obtain Stella Source Code

```bash
git clone https://github.com/stellaGK/stella.git
cd stella
git checkout v0.8  # Ensure you're on version 0.8
```

### Step 2: Apply Modifications

Copy the three modified files from this repository:

```bash
cp path/to/this/repo/stella_modifications/common_types.f90 ~/stella/grids/
cp path/to/this/repo/stella_modifications/species.f90 ~/stella/grids/
cp path/to/this/repo/stella_modifications/vpamu_grids.f90 ~/stella/grids/
```

**Alternative:** Manually edit the three files following the changes documented above.

### Step 3: Compile Stella

```bash
export STELLA_SYSTEM=gnu_ubuntu  # or your system type (gnu_osx, intel_linux, etc.)
export MAKEFLAGS=-IMakefiles
make clean
make -j$(nproc)
```

Successful compilation produces `~/stella/stella` executable.

---

## Usage in Input Files

To use anisotropic temperatures in your Stella input file:

```fortran
&species_parameters
  nspec = 2
  spec(1)%z = 1.0              ! Ion charge
  spec(1)%mass = 1.0           ! Ion mass
  spec(1)%dens = 1.0           ! Density
  spec(1)%temp = 1.0           ! Reference temperature

  ! Anisotropic temperature parameters
  spec(1)%use_anisotropic_temp = .true.
  spec(1)%tpar = 1.0           ! Parallel temperature T∥
  spec(1)%tperp = 0.90         ! Perpendicular temperature T⊥

  spec(1)%tprim = 6.92         ! Temperature gradient
  spec(1)%fprim = 2.22         ! Density gradient
/
```

**Key parameters:**
- `use_anisotropic_temp = .true.`: Enable anisotropic initialization
- `tpar`: Sets T∥ (typically normalized to 1.0)
- `tperp`: Sets T⊥ (varies to control Δ)

**Pressure anisotropy:**
```
Δ = (T⊥ - T∥) / (2T∥)
```

**Example values:**
- `tpar = 1.0, tperp = 1.0` → Δ = 0 (isotropic Maxwellian)
- `tpar = 1.0, tperp = 0.90` → Δ = -0.05 (mild anisotropy)
- `tpar = 1.0, tperp = 0.50` → Δ = -0.25 (strong anisotropy)

---

## Verification

To verify modifications were applied correctly:

1. **Check compilation:** Ensure no errors during `make`
2. **Test isotropic case:** Run with `use_anisotropic_temp = .false.` and verify results match unmodified Stella
3. **Test anisotropic case:** Run with `tpar = 1.0, tperp = 0.90` and check:
   - Simulation runs without crashing
   - Heat flux is reduced compared to isotropic case
   - NetCDF output includes species temperature data

---

## Compatibility Notes

- **Stella version:** v0.8 (modifications may require adjustment for other versions)
- **Backward compatibility:** When `use_anisotropic_temp = .false.`, code behaves identically to unmodified Stella
- **Multi-species:** Modifications support multiple species; set parameters independently for each

---

## Known Limitations

1. **Strong anisotropy instability:** Values |Δ| > 0.25 may trigger kinetic instabilities (mirror mode, gyrokinetic ordering violation)
2. **Electromagnetic:** Modifications tested for electrostatic simulations; electromagnetic cases may require additional adjustments
3. **Normalization:** Temperature normalization follows Stella conventions; ensure consistency with `temp` parameter

---

## Troubleshooting

**Problem:** Compilation fails with "tpar not found"
**Solution:** Ensure `common_types.f90` was modified correctly; check that `tpar`, `tperp`, and `use_anisotropic_temp` are added to `spec_type`

**Problem:** Simulation crashes with NaN at early timesteps
**Solution:** Reduce anisotropy magnitude; try |Δ| < 0.10 first

**Problem:** No difference between isotropic and anisotropic runs
**Solution:** Verify `use_anisotropic_temp = .true.` in input file; check that `tpar ≠ tperp`

---

## References

For scientific context and validation results, see:

- **Paper:** "Gyrokinetic Validation of Lynden-Bell Pressure Anisotropy" (Finberg 2025)
- **Repository:** https://github.com/laurelininc/gyrokinetic-lynden-bell-2025
- **Stella documentation:** https://github.com/stellaGK/stella

---

**Contact:**
Joseph S. Finberg
Laurelin Technologies Inc.
Email: joe@laurelin-inc.com

**Last Updated:** December 2025
**Version:** 1.0
