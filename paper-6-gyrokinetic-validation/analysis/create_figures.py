#!/usr/bin/env python3
"""
Generate publication-quality figures for PRL Paper 6
Comparing Maxwellian vs Lynden-Bell gyrokinetic simulations
"""

import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
from pathlib import Path

# Set publication style
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (7, 5),
    'lines.linewidth': 1.5,
})

def plot_heat_flux_comparison(max_file, lb_file, output='fig1_heat_flux.pdf'):
    """Figure 1: Heat flux time series comparison"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    
    # Load data
    with nc.Dataset(max_file, 'r') as f:
        t_max = f.variables['t'][:]
        # Find heat flux variable
        qflux_max = None
        for var in ['qflux', 'es_heat_flux', 'heat_flux']:
            if var in f.variables:
                qflux_max = f.variables[var][:]
                break
    
    with nc.Dataset(lb_file, 'r') as f:
        t_lb = f.variables['t'][:]
        qflux_lb = None
        for var in ['qflux', 'es_heat_flux', 'heat_flux']:
            if var in f.variables:
                qflux_lb = f.variables[var][:]
                break
    
    if qflux_max is not None:
        # Sum over kx, ky if needed
        if qflux_max.ndim > 1:
            q_max_total = np.sum(np.abs(qflux_max), axis=tuple(range(1, qflux_max.ndim)))
        else:
            q_max_total = np.abs(qflux_max)
        
        ax1.plot(t_max, q_max_total, 'b-', label='Maxwellian', alpha=0.7)
        ax1.set_ylabel(r'$Q_i$ (Maxwellian)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    if qflux_lb is not None:
        if qflux_lb.ndim > 1:
            q_lb_total = np.sum(np.abs(qflux_lb), axis=tuple(range(1, qflux_lb.ndim)))
        else:
            q_lb_total = np.abs(qflux_lb)
        
        ax2.plot(t_lb, q_lb_total, 'r-', label='Lynden-Bell', alpha=0.7)
        ax2.set_ylabel(r'$Q_i$ (Lynden-Bell)')
        ax2.set_xlabel(r'Time $(R/v_{thi})$')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output}")
    plt.close()

def plot_ratio_vs_time(max_file, lb_file, output='fig2_ratio.pdf'):
    """Figure 2: Q_LB/Q_Max ratio vs time"""
    fig, ax = plt.subplots(figsize=(7, 4))
    
    with nc.Dataset(max_file, 'r') as f:
        t = f.variables['t'][:]
        qflux_max = None
        for var in ['qflux', 'es_heat_flux']:
            if var in f.variables:
                qflux_max = f.variables[var][:]
                break
    
    with nc.Dataset(lb_file, 'r') as f:
        qflux_lb = None
        for var in ['qflux', 'es_heat_flux']:
            if var in f.variables:
                qflux_lb = f.variables[var][:]
                break
    
    if qflux_max is not None and qflux_lb is not None:
        # Total heat flux
        q_max = np.sum(np.abs(qflux_max), axis=tuple(range(1, qflux_max.ndim))) if qflux_max.ndim > 1 else np.abs(qflux_max)
        q_lb = np.sum(np.abs(qflux_lb), axis=tuple(range(1, qflux_lb.ndim))) if qflux_lb.ndim > 1 else np.abs(qflux_lb)
        
        ratio = q_lb / q_max
        
        ax.plot(t, ratio, 'k-', alpha=0.7, label=r'$Q_i^{LB}/Q_i^{Max}$')
        ax.axhline(0.8, color='g', linestyle='--', alpha=0.5, label='Expected (0.75-0.85)')
        ax.axhline(0.75, color='g', linestyle='--', alpha=0.5)
        
        # Average ratio (steady state)
        ntime = len(t)
        ratio_avg = np.mean(ratio[ntime//2:])
        ax.axhline(ratio_avg, color='r', linestyle=':', alpha=0.7, 
                  label=f'Avg = {ratio_avg:.3f}')
        
        ax.set_xlabel(r'Time $(R/v_{thi})$')
        ax.set_ylabel(r'$Q_i^{LB}/Q_i^{Max}$')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0.5, 1.2])
    
    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    print(f"✓ Saved {output}")
    plt.close()

if __name__ == '__main__':
    results_dir = Path('results')
    max_file = results_dir / 'maxwellian.nc'
    lb_file = results_dir / 'lyndenbell.nc'
    
    if not max_file.exists() or not lb_file.exists():
        print("ERROR: Result files not found!")
        print("Run download_results.sh first!")
        exit(1)
    
    print("Generating figures for PRL Paper 6...")
    print("-" * 60)
    
    plot_heat_flux_comparison(max_file, lb_file)
    plot_ratio_vs_time(max_file, lb_file)
    
    print("-" * 60)
    print("✓ All figures generated!")
    print("\nFigures:")
    print("  fig1_heat_flux.pdf - Heat flux time series")
    print("  fig2_ratio.pdf     - Q_LB/Q_Max ratio")
