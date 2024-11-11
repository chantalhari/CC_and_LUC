#!/usr/bin/env python3
#pip install  rioxarray==0.3.1
import pandas as pd
import xarray as xr
import os
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import matplotlib.colors
scriptsdir = os.getcwd()
from scipy.interpolate import griddata
from functools import reduce
import itertools
import argparse
import pickle

ap = argparse.ArgumentParser()

# collect the function arguments

ap.add_argument('-m', '--scenario', type=str, help="scenario, string", nargs="+", required=True)
ap.add_argument('-a', '--time', type=str, help="time, string", nargs="+", required=True)

# parse the arguments to the args object
args = ap.parse_args()

# *************************************************
# Get arguments
# *************************************************
print(args)

scenario = args.scenario
time = args.time


sdms = ["GAM", "GBM"]
gcms = ['GFDL-ESM2M', 'IPSL-CM5A-LR', 'HadGEM2-ES', 'MIROC5']
taxas = ["Mammals","Amphibians","Bird"]  # Add the second taxa here
#scenario = "rcp26"
#time=35
historical_time=1146

years = ['1845', '1990', '1995', '2009', '2010', '2020', '2026', '2032', '2048', '2050',
         '2052', '2056', '2080', '2100', '2150', '2200', '2250']


# Create the dictionaries
newvalue_hist_sum = {}
newvalue_future_sum = {}
sumbin_hist_sum = {}
sumbin_future_sum = {}

# Initialize the dictionaries with SDM, GCM, and taxa keys
mean_newvalue_change = {}
mean_sum_bin_change = {}
mean_land_use_change = {}

for sdm in sdms:
    newvalue_hist_sum[sdm] = {}
    newvalue_future_sum[sdm] = {}
    sumbin_hist_sum[sdm] = {}
    sumbin_future_sum[sdm] = {}
    mean_newvalue_change[sdm] = {}
    mean_sum_bin_change[sdm] = {}
    mean_land_use_change[sdm] = {}

    for gcm in gcms:
        newvalue_hist_sum[sdm][gcm] = {}
        newvalue_future_sum[sdm][gcm] = {}
        sumbin_hist_sum[sdm][gcm] = {}
        sumbin_future_sum[sdm][gcm] = {}
        mean_newvalue_change[sdm][gcm] = {}
        mean_sum_bin_change[sdm][gcm] = {}
        mean_land_use_change[sdm][gcm] = {}

        for taxa in taxas:
            newvalue_hist_sum[sdm][gcm][taxa] = []
            newvalue_future_sum[sdm][gcm][taxa] = []
            sumbin_hist_sum[sdm][gcm][taxa] = []
            sumbin_future_sum[sdm][gcm][taxa] = []

# Loop over all taxa
for taxa in taxas:
    for sdm in sdms:
        dir_species = "/storage/scratch/users/ch21o450/data/LandClim_Output/Sensitivity_Analysis/" + sdm + "/" + taxa + "/EWEMBI/"
        available_file = os.listdir(dir_species)
        available_names = [x.split("_[1146].nc")[0] for x in available_file]

        species_names = available_names
        # Define the netCDF file path
        netcdf_path_format_future = "/storage/scratch/users/ch21o450/data/LandClim_Output/Sensitivity_Analysis_newbase/{}/{}/{}/{}/{}_[{}].nc"
        netcdf_path_format_hist = "/storage/scratch/users/ch21o450/data/LandClim_Output/Sensitivity_Analysis/{}/{}/EWEMBI/{}_[{}].nc"

        # Loop over all species
        for species_name in species_names:
            # Loop over all models
            for gcm in gcms:
                try:
                    # Open the netCDF files
                    ds_newvalue_fut = xr.open_dataset(
                        netcdf_path_format_future.format(sdm, taxa, gcm, scenario[0], species_name, time[0]),
                        decode_times=False
                    )
                    ds_newvalue_hist = xr.open_dataset(
                        netcdf_path_format_hist.format(sdm, taxa, species_name, historical_time),
                        decode_times=False
                    )
                    
                    # Get the newvalue and sum_bin
                    newvalue_hist = ds_newvalue_hist["newvalue"]
                    newvalue_future = ds_newvalue_fut["newvalue"]
                    sum_bin_hist = ds_newvalue_hist["sum_bin"].isel(time=0)
                    sum_bin_future = ds_newvalue_fut["sum_bin"].isel(time=0)

                    # Append the newvalue to the dictionaries
                    newvalue_hist_sum[sdm][gcm][taxa].append(newvalue_hist)
                    newvalue_future_sum[sdm][gcm][taxa].append(newvalue_future)
                    sumbin_hist_sum[sdm][gcm][taxa].append(sum_bin_hist)
                    sumbin_future_sum[sdm][gcm][taxa].append(sum_bin_future)

                    # Your existing code to process the files goes here

                except FileNotFoundError:
                    # Handle the case where the file is not found
                    print(f"File not found for species {species_name}. Continuing to the next species.")
                    continue
                except Exception as e:
                    # Handle other exceptions if needed
                    print(f"An error occurred for species {species_name}: {e}")
                    continue



# Output directory for pickles

#output_dir = "/storage/scratch/users/ch21o450/data/intermediate_results/"
output_dir = "/storage/scratch/users/ch21o450/data/intermediate_results/"
os.makedirs(output_dir, exist_ok=True)

# Loop over all taxa
for taxa in taxas:
    for sdm in sdms:
        for gcm in gcms:
            # Concatenate and sum values
            newvalue_hist_sum_taxa = xr.concat(newvalue_hist_sum[sdm][gcm][taxa], dim="species").sum(dim="species")
            newvalue_future_sum_taxa = xr.concat(newvalue_future_sum[sdm][gcm][taxa], dim="species").sum(dim="species")
            sum_bin_hist_sum_taxa = xr.concat(sumbin_hist_sum[sdm][gcm][taxa], dim="species").sum(dim="species")
            sum_bin_future_sum_taxa = xr.concat(sumbin_future_sum[sdm][gcm][taxa], dim="species").sum(dim="species")

            # Output file paths
            newvalue_hist_sum_path = os.path.join(output_dir, f"newvalue_hist_sum_{sdm}_{gcm}_{taxa}_{scenario}_{time}_SA_newbase.pkl")
            newvalue_future_sum_path = os.path.join(output_dir, f"newvalue_future_sum_{sdm}_{gcm}_{taxa}_{scenario}_{time}_SA_newbase.pkl")
            sum_bin_hist_sum_path = os.path.join(output_dir, f"sum_bin_hist_sum_{sdm}_{gcm}_{taxa}_{scenario}_{time}_SA_newbase.pkl")
            sum_bin_future_sum_path = os.path.join(output_dir, f"sum_bin_future_sum_{sdm}_{gcm}_{taxa}_{scenario}_{time}_SA_newbase.pkl")

            # Write to pickle files
            with open(newvalue_hist_sum_path, "wb") as f:
                pickle.dump(newvalue_hist_sum_taxa, f)

            with open(newvalue_future_sum_path, "wb") as f:
                pickle.dump(newvalue_future_sum_taxa, f)

            with open(sum_bin_hist_sum_path, "wb") as f:
                pickle.dump(sum_bin_hist_sum_taxa, f)

            with open(sum_bin_future_sum_path, "wb") as f:
                pickle.dump(sum_bin_future_sum_taxa, f)




# Assume you already have the necessary data loaded into these dictionaries
# mean_newvalue_change, mean_sum_bin_change, mean_land_use_change, uncertainties_sdm_taxa, uncertainties_gcm_taxa

# Calculate uncertainties for SDM and GCM
#sdm_uncertainties = {}
#gcm_uncertainties = {}

#for taxa in taxas:
  #  sdm_uncertainties[taxa] = np.std([mean_newvalue_change[sdm][gcm][taxa].mean().item() for sdm in sdms for gcm in gcms])
 #   gcm_uncertainties[taxa] = np.std([mean_newvalue_change[sdm][gcm][taxa].mean().item() for gcm in gcms for sdm in sdms])

# File paths for pickle files
#sdm_uncertainties_path = os.path.join(output_dir, f"sdm_uncertainties_{scenario}_{time}.pkl")
#gcm_uncertainties_path = os.path.join(output_dir, f"gcm_uncertainties_{scenario}_{time}.pkl")

