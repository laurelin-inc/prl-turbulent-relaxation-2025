#!/usr/bin/env python3
"""
Compare Maxwellian vs Lynden-Bell Stella simulations
Extract: heat flux, pressure anisotropy, growth rates
"""

import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_stella_output(filename, label):
    """Analyze a Stella output file"""
    print(f"\n{'='*60}")
    print(f"Analyzing {label}: {filename}")
    print(f"{'='*60}")
    
    with nc.Dataset(filename, 'r') as f:
        # List all variables
        print("\nAvailable variables:")
        for var in sorted(f.variables.keys()):
            shape = f.variables[var].shape
            print(f"  {var:30s} {str(shape):20s}")
        
        # Extract time
        t = f.variables['t'][:] if 't' in f.variables else None
        
        # Try to extract heat flux
        qflux_vars = ['qflux', 'pflux', 'heat_flux', 'es_heat_flux', 
                      'qflux_vs_kxky', 'es_heat_flux_vs_kxky']
        qflux = None
        for var in qflux_vars:
            if var in f.variables:
                qflux = f.variables[var][:]
                print(f"\n✓ Found heat flux variable: {var}")
                print(f"  Shape: {qflux.shape}")
                break
        
        # Extract phi for amplitude
        phi = None
        if 'phi_vs_t' in f.variables:
            phi = f.variables['phi_vs_t'][:]
            print(f"\n✓ Found phi_vs_t")
            print(f"  Shape: {phi.shape}")
        elif 'phi' in f.variables:
            phi = f.variables['phi'][:]
            print(f"\n✓ Found phi")  
            print(f"  Shape: {phi.shape}")
        
        results = {
            'time': t,
            'qflux': qflux,
            'phi': phi,
            'label': label
        }
        
        return results

def compute_time_averaged_flux(qflux, time=None, start_frac=0.5):
    """Compute time-averaged flux from steady-state portion"""
    if qflux is None:
        return None
    
    ntime = qflux.shape[0]
    start_idx = int(ntime * start_frac)
    
    # Average over time
    qflux_avg = np.mean(np.abs(qflux[start_idx:]), axis=0)
    
    # Sum over kx, ky if needed
    if qflux_avg.ndim > 0:
        qflux_total = np.sum(qflux_avg)
    else:
        qflux_total = qflux_avg
    
    return qflux_total

if __name__ == '__main__':
    # Check if result files exist
    results_dir = Path('results')
    max_file = results_dir / 'maxwellian.nc'
    lb_file = results_dir / 'lyndenbell.nc'
    
    if not max_file.exists() or not lb_file.exists():
        print("ERROR: Result files not found!")
        print(f"  Looking for: {max_file}")
        print(f"  Looking for: {lb_file}")
        print("\nRun download_results.sh first!")
        exit(1)
    
    # Analyze both simulations
    max_results = analyze_stella_output(max_file, "Maxwellian")
    lb_results = analyze_stella_output(lb_file, "Lynden-Bell")
    
    # Compute heat fluxes
    print(f"\n{'='*60}")
    print("HEAT FLUX COMPARISON")
    print(f"{'='*60}")
    
    q_max = compute_time_averaged_flux(max_results['qflux'])
    q_lb = compute_time_averaged_flux(lb_results['qflux'])
    
    if q_max is not None and q_lb is not None:
        ratio = q_lb / q_max
        reduction = (1 - ratio) * 100
        
        print(f"\nQ_i (Maxwellian):   {q_max:.6e}")
        print(f"Q_i (Lynden-Bell):  {q_lb:.6e}")
        print(f"\nRatio Q_LB/Q_Max:   {ratio:.3f}")
        print(f"Reduction:          {reduction:.1f}%")
        print(f"\nExpected: 15-25% reduction")
        
        if 15 <= reduction <= 25:
            print("✓✓✓ VALIDATES LYNDEN-BELL PREDICTION! ✓✓✓")
        else:
            print(f"⚠ Outside expected range")
    else:
        print("\n⚠ Could not compute heat flux - check variable names")
    
    print(f"\n{'='*60}\n")
