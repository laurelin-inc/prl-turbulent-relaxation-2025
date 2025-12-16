-- PRODUCTION SIMULATION v3 for Papers 3 & 5
-- FIX: Add collision operator to enable pitch-angle scattering
-- Anisotropy Relaxation: Δ from +0.5 to -0.5
--
-- CRITICAL CHANGE from v2: Add Lenard-Bernstein collision operator
-- ν/Ω ~ 0.01 (weak collision limit) to break μ-conservation
--
-- Resolution: 8³ × 12³ = 884,736 phase-space cells
-- Time: t=0-100, 67 frames (dt=1.5)
-- Expected runtime: 8-10 hours on A100 GPU
-- Output: ~74 GB (67 frames × 1.1 GB/frame)

local Vlasov = G0.Vlasov
pi = math.pi

-- Physical parameters (normalized units)
epsilon0, mu0 = 1.0, 1.0
mass_elc, charge_elc = 1.0, -1.0
n0, B0, beta = 1.0, 1.0, 1.0

-- Initial temperature anisotropy: T_perp/T_par = 2.0 (firehose unstable)
anisotropy_ratio = 2.0
T_par_init = 2.0 / (2.0 * anisotropy_ratio + 1.0)  -- 0.4
T_perp_init = anisotropy_ratio * T_par_init         -- 0.8

vth_par = math.sqrt(T_par_init)
vth_perp = math.sqrt(T_perp_init)

-- COLLISION FREQUENCY
-- Normalized cyclotron frequency Ω = qB/m = 1.0 (from B0=1, q=1, m=1)
-- Set collision frequency ν = 0.01 * Ω = 0.01
collision_freq = 0.01

print('================================================================')
print('PRODUCTION RUN v3: Papers 3 & 5 Anisotropy Relaxation')
print('FIX: Collision operator (ν/Ω = 0.01) to enable pitch-angle scattering')
print('================================================================')
print(string.format('Physical parameters:'))
print(string.format('  B0 = %.2f, beta = %.2f', B0, beta))
print(string.format('  T_par = %.4f, T_perp = %.4f', T_par_init, T_perp_init))
print(string.format('  Anisotropy ratio: T_perp/T_par = %.2f', anisotropy_ratio))
print(string.format(''))
print(string.format('Collision parameters:'))
print(string.format('  Cyclotron frequency Ω = %.2f', B0))
print(string.format('  Collision frequency ν = %.4f', collision_freq))
print(string.format('  ν/Ω = %.4f (weak collision limit)', collision_freq/B0))
print(string.format(''))
print(string.format('Initial state:'))
print(string.format('  Delta_init = (T_perp - T_par)/(2*T_par) = %.4f', (T_perp_init-T_par_init)/(2*T_par_init)))
print(string.format(''))
print(string.format('Expected equilibrium:'))
print(string.format('  Delta_eq = -1/(2*beta) = %.4f', -1.0/(2*beta)))
print('================================================================')

-- Turbulent perturbation amplitude (15% for v3, reduced from v2's 50%)
perturb_amplitude = 0.15

-- Grid resolution
Nx, Ny, Nz = 8, 8, 8        -- Spatial: 512 cells
Nvx, Nvy, Nvz = 12, 12, 12  -- Velocity: 1,728 cells
total_cells = Nx * Ny * Nz * Nvx * Nvy * Nvz

print(string.format('Grid resolution:'))
print(string.format('  Spatial: %d³ = %d cells', Nx, Nx*Ny*Nz))
print(string.format('  Velocity: %d³ = %d cells', Nvx, Nvx*Nvy*Nvz))
print(string.format('  TOTAL: %d phase-space cells', total_cells))
print('================================================================')

-- Velocity space extent
vmax = 4.0 * math.sqrt((T_par_init + T_perp_init)/2)

-- Time evolution
tEnd = 100.0    -- Extended time for full relaxation
nFrame = 66     -- 67 total frames (t=0,1.5,3,...,99,100)

print(string.format('Time evolution:'))
print(string.format('  t = 0 to %.0f', tEnd))
print(string.format('  Output frames: %d (dt ≈ %.2f)', nFrame+1, tEnd/nFrame))
print(string.format('  Expected runtime: 8-10 hours on A100'))
print('================================================================')

-- Generate turbulent modes (Kolmogorov spectrum k^(-5/3))
math.randomseed(42)  -- Reproducibility
local k_modes = {}
local phases = {}
local mode_count = 0

for ix = 0, 2 do
  for iy = 0, 2 do
    for iz = 0, 2 do
      if ix + iy + iz > 0 then
        mode_count = mode_count + 1
        k_modes[mode_count] = {1+ix, 1+iy, 1+iz}
        phases[mode_count] = 2*pi*math.random()
      end
    end
  end
end

print(string.format('Turbulent perturbations:'))
print(string.format('  Modes: %d (k ∈ [1,4])', mode_count))
print(string.format('  Spectrum: k^(-5/3) (Kolmogorov)'))
print(string.format('  Amplitude: %.0f%%', perturb_amplitude*100))
print('================================================================')

function turbulent_perturbation(x, y, z)
  local delta_n = 0.0
  for i = 1, mode_count do
    local kx, ky, kz = k_modes[i][1], k_modes[i][2], k_modes[i][3]
    local k_mag = math.sqrt(kx*kx + ky*ky + kz*kz)
    delta_n = delta_n + k_mag^(-5/3) * math.cos(kx*x + ky*y + kz*z + phases[i])
  end
  return perturb_amplitude * delta_n / mode_count
end

-- Vlasov-Maxwell Application
vlasovApp = Vlasov.App.new {
  tEnd = tEnd,
  nFrame = nFrame,
  lower = {0, 0, 0},
  upper = {2*pi, 2*pi, 2*pi},
  cells = {Nx, Ny, Nz},
  basis = "serendipity",
  polyOrder = 1,
  timeStepper = "rk3",
  cflFrac = 0.3,
  periodicDirs = {1, 2, 3},

  -- Electron species WITH COLLISION OPERATOR
  elc = Vlasov.Species.new {
    modelID = G0.Model.Default,
    charge = charge_elc,
    mass = mass_elc,
    lower = {-vmax, -vmax, -vmax},
    upper = {vmax, vmax, vmax},
    cells = {Nvx, Nvy, Nvz},
    numInit = 1,

    -- Initial condition: Anisotropic bi-Maxwellian + density perturbations
    projections = {{
      projectionID = G0.Projection.Func,
      init = function(t, xn)
        local x, y, z = xn[1], xn[2], xn[3]
        local vx, vy, vz = xn[4], xn[5], xn[6]

        -- Density with turbulent perturbations
        local n = n0 * (1.0 + turbulent_perturbation(x, y, z))

        -- Anisotropic Maxwellian: different T_perp, T_par
        local v_perp_sq = vx*vx + vy*vy
        local v_par_sq = vz*vz
        local norm = n / ((2*pi)^1.5 * vth_perp * vth_perp * vth_par)
        local exp_arg = -(v_perp_sq/(2*vth_perp*vth_perp) + v_par_sq/(2*vth_par*vth_par))

        return norm * math.exp(exp_arg)
      end
    }},

    evolve = true,

    -- CRITICAL FIX: Add Lenard-Bernstein collision operator
    -- This enables pitch-angle scattering by breaking μ-conservation
    collisions = {
      collisionID = G0.Collisions.LBO,
      selfNu = function (t, xn)
        return collision_freq  -- ν = 0.01
      end
    },

    diagnostics = {G0.Moment.M0, G0.Moment.M1i, G0.Moment.M2ij}
  },

  -- Electromagnetic field
  field = Vlasov.Field.new {
    epsilon0 = epsilon0,
    mu0 = mu0,
    init = function(t, xn)
      local x, y, z = xn[1], xn[2], xn[3]

      -- Small EM perturbations to seed instabilities
      local E_pert = 0.01 * perturb_amplitude
      local B_pert = 0.05 * perturb_amplitude

      local Ex = E_pert * turbulent_perturbation(x, y, z)
      local Ey = E_pert * turbulent_perturbation(x + pi/3, y, z)
      local Ez = E_pert * turbulent_perturbation(x, y + pi/3, z)
      local Bx = B_pert * turbulent_perturbation(x, y, z + pi/4)
      local By = B_pert * turbulent_perturbation(x + pi/4, y, z)
      local Bz = B0 * (1.0 + B_pert * turbulent_perturbation(x, y + pi/4, z))

      return Ex, Ey, Ez, Bx, By, Bz, 0.0, 0.0
    end,
    evolve = true,
    elcErrorSpeedFactor = 0.0,
    mgnErrorSpeedFactor = 0.0
  }
}

print('STARTING PRODUCTION RUN v3 WITH COLLISIONS...')
print('Output will be: gkeyll_papers_3_5_PRODUCTION_v3-elc_N.gkyl')
print('================================================================')
print('EXPECTED RESULT:')
print('  With ν/Ω = 0.01, collisions will enable pitch-angle scattering')
print('  σ(v∥) should evolve > 1% over full run')
print('  Δ(t) should relax from +0.5 toward -0.5')
print('  Relaxation timescale τ ~ 1/ν ~ 100 time units')
print('================================================================')
print('MONITORING:')
print('  Use test_v3_velocity_evolution.py to check first 5 frames')
print('  Expected: σ(v∥) changes > 0.1% in first few frames')
print('================================================================')

vlasovApp:run()

print('================================================================')
print('PRODUCTION RUN v3 COMPLETE!')
print('================================================================')
print('Next steps:')
print('  1. Run test_v3_velocity_evolution.py on first 5 frames')
print('  2. Verify σ(v∥) is evolving (>0.1% change)')
print('  3. If successful, analyze all frames for full relaxation curve')
print('  4. Extract Δ(t) and measure relaxation timescale')
print('================================================================')
