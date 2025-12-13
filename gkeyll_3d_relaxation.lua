-- 3D Turbulent Relaxation Simulation for Gkeyll Zero
-- Tests Lynden-Bell formula: Δ = -1/(2β)
-- 3D spatial + 3D velocity (full 6D phase space)

local Vlasov = G0.Vlasov

-- Mathematical constants
pi = math.pi

-- Physical parameters (normalized units)
epsilon0 = 1.0  -- Permittivity
mu0 = 1.0       -- Permeability
mass_elc = 1.0  -- Electron mass
charge_elc = -1.0  -- Electron charge

-- Plasma parameters
n0 = 1.0        -- Background density
T0 = 1.0        -- Initial temperature (average)
B0 = 1.0        -- Background magnetic field
beta = 1.0      -- Plasma beta = 8πnT/B²

-- Anisotropic initial condition (firehose unstable)
-- Start with p_perp/p_par = 2 (T_perp/T_par = 2)
-- Should relax to Lynden-Bell: Δ = -1/(2β) = -0.5
anisotropy_ratio = 2.0  -- T_perp / T_par
T_par_init = T0 * 2.0 / (2.0 * anisotropy_ratio + 1.0)  -- Maintain average T
T_perp_init = anisotropy_ratio * T_par_init

-- Derived quantities
vth = math.sqrt(T0 / mass_elc)  -- Average thermal velocity
vth_par_init = math.sqrt(T_par_init / mass_elc)
vth_perp_init = math.sqrt(T_perp_init / mass_elc)

-- 3D Turbulent spectrum parameters
k_min = 1
k_max = 4
n_modes_per_dim = 3  -- Modes per spatial dimension
spectrum_index = -5.0/3.0  -- Kolmogorov spectrum
perturb_amplitude = 0.15   -- Perturbation amplitude (slightly larger for 3D)

-- Simulation domain (cubic box)
L = 2.0 * pi  -- Box size
vmax = 3.5 * vth  -- Velocity extent (slightly reduced for 3D)

-- Grid resolution (optimized for CPU, full 6D)
Nx = 8   -- Spatial cells in each direction (8³ = 512 cells)
Nv = 6   -- Velocity cells in each direction (6³ = 216 cells)
-- Total phase space: 512 × 216 = 110,592 cells

-- Time parameters
t_end = 20.0    -- Final time (shorter for 3D)
num_frames = 20  -- Output frames
cfl_frac = 0.3  -- CFL number (conservative for 3D)

-- Polynomial order
poly_order = 1
basis_type = "serendipity"
time_stepper = "rk3"

-- Generate 3D turbulent spectrum
math.randomseed(42)  -- Reproducible results
local k_modes = {}
local phases = {}
local mode_count = 0

-- Generate k-vectors covering 3D k-space
for ix = 0, n_modes_per_dim-1 do
  for iy = 0, n_modes_per_dim-1 do
    for iz = 0, n_modes_per_dim-1 do
      if ix + iy + iz > 0 then  -- Skip k=0
        mode_count = mode_count + 1
        local kx = k_min + ix * (k_max - k_min) / (n_modes_per_dim - 1)
        local ky = k_min + iy * (k_max - k_min) / (n_modes_per_dim - 1)
        local kz = k_min + iz * (k_max - k_min) / (n_modes_per_dim - 1)

        k_modes[mode_count] = {kx, ky, kz}
        phases[mode_count] = 2.0 * pi * math.random()
      end
    end
  end
end

-- 3D Turbulent density perturbation
function turbulent_perturbation(x, y, z)
  local delta_n = 0.0

  for i = 1, mode_count do
    local kx, ky, kz = k_modes[i][1], k_modes[i][2], k_modes[i][3]
    local k_mag = math.sqrt(kx*kx + ky*ky + kz*kz)
    local amplitude = k_mag^spectrum_index

    delta_n = delta_n + amplitude * math.cos(kx * x + ky * y + kz * z + phases[i])
  end

  -- Normalize to desired total amplitude
  delta_n = perturb_amplitude * delta_n / mode_count
  return delta_n
end

-- Main application
vlasovApp = Vlasov.App.new {

  tEnd = t_end,
  nFrame = num_frames,

  -- 3D Configuration space
  lower = { 0.0, 0.0, 0.0 },
  upper = { L, L, L },
  cells = { Nx, Nx, Nx },
  cflFrac = cfl_frac,

  basis = basis_type,
  polyOrder = poly_order,
  timeStepper = time_stepper,

  -- Periodic boundary conditions in all directions
  periodicDirs = { 1, 2, 3 },

  -- Electron species
  elc = Vlasov.Species.new {
    modelID = G0.Model.Default,
    charge = charge_elc,
    mass = mass_elc,

    -- 3D Velocity space: Cartesian (vx, vy, vz)
    -- B field is in z-direction, so vz is parallel
    lower = { -vmax, -vmax, -vmax },
    upper = { vmax, vmax, vmax },
    cells = { Nv, Nv, Nv },

    -- Initial condition
    numInit = 1,
    projections = {
      {
        projectionID = G0.Projection.Func,

        init = function (t, xn)
          local x = xn[1]
          local y = xn[2]
          local z = xn[3]
          local vx = xn[4]
          local vy = xn[5]
          local vz = xn[6]

          -- 3D perturbed density
          local n = n0 * (1.0 + turbulent_perturbation(x, y, z))

          -- Anisotropic Maxwellian: different T_perp and T_par
          -- f(v) = n / ((2π)^(3/2) * vth_perp^2 * vth_par) * exp(-(vx^2+vy^2)/(2*vth_perp^2) - vz^2/(2*vth_par^2))
          local v_perp_sq = vx*vx + vy*vy
          local v_par_sq = vz*vz

          local norm = n / ((2.0*pi)^1.5 * vth_perp_init * vth_perp_init * vth_par_init)
          local exponent = -(v_perp_sq / (2.0 * vth_perp_init * vth_perp_init) + v_par_sq / (2.0 * vth_par_init * vth_par_init))
          local f = norm * math.exp(exponent)

          return f
        end
      }
    },

    evolve = true,

    -- Diagnostics: moments to output
    diagnostics = { G0.Moment.M0, G0.Moment.M1i, G0.Moment.M2ij }
  },

  -- Electromagnetic field
  field = Vlasov.Field.new {
    epsilon0 = epsilon0,
    mu0 = mu0,

    -- Initial electromagnetic field
    init = function (t, xn)
      local x = xn[1]
      local y = xn[2]
      local z = xn[3]

      -- Small turbulent electric field perturbations
      local E_pert = 0.01 * perturb_amplitude
      local Ex = E_pert * turbulent_perturbation(x, y, z)
      local Ey = E_pert * turbulent_perturbation(x + pi/3, y, z)
      local Ez = E_pert * turbulent_perturbation(x, y + pi/3, z)

      -- Background magnetic field in z-direction with small turbulent perturbations
      local B_pert = 0.05 * perturb_amplitude
      local Bx = B_pert * turbulent_perturbation(x, y, z + pi/4)
      local By = B_pert * turbulent_perturbation(x + pi/4, y, z)
      local Bz = B0 * (1.0 + B_pert * turbulent_perturbation(x, y + pi/4, z))

      -- Return: Ex, Ey, Ez, Bx, By, Bz, phi_E, phi_B (error potentials)
      return Ex, Ey, Ez, Bx, By, Bz, 0.0, 0.0
    end,

    evolve = true,
    elcErrorSpeedFactor = 0.0,
    mgnErrorSpeedFactor = 0.0
  }
}

-- Run the simulation
vlasovApp:run()
