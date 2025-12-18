#!/usr/bin/env python3
"""
Extract ion heat flux from Stella output files
Compare Maxwellian vs Lynden-Bell cases
"""

import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt

def extract_heat_flux(filename):
    """Extract time-averaged ion heat flux from Stella output"""
    with nc.Dataset(filename, 'r') as f:
        # Print available variables
        print(f"Variables in {filename}:")
        print([v for v in f.variables.keys() if 'flux' in v.lower() or 'qflux' in v.lower()])
        
        # Try different possible variable names
        qflux_names = ['qflux', 'pflux', 'heat_flux', 'es_heat_flux']
        
        for name in qflux_names:
            if name in f.variables:
                qflux = f.variables[name][:]
                print(f"\nFound variable: {name}")
                print(f"Shape: {qflux.shape}")
                
                # Average over time (last half for steady state)
                ntime = qflux.shape[0]
                qflux_avg = np.mean(qflux[ntime//2:], axis=0)
                
                return qflux, qflux_avg
        
        # If specific names not found, list all variables
        print("\nAll variables:")
        for var in f.variables.keys():
            print(f"  {var}: {f.variables[var].shape}")
        
        return None, None

if __name__ == '__main__':
    # This will be run after downloading the files
    print("Heat flux extraction script ready")
    print("Usage: python extract_heat_flux.py")
