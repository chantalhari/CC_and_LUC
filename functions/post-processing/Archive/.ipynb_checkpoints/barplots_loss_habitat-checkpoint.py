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
habitats = ["forest", "pasture", "cropland", "natural_land"]
taxas = ["Mammals","Amphibians","Bird"]
#scenario = "rcp26"
#time=35
historical_time=1146

years = ['1845', '1990', '1995', '2009', '2010', '2020', '2026', '2032', '2048', '2050',
         '2052', '2056', '2080', '2100', '2150', '2200', '2250']

# Create the dictionaries
newvalue_dict_fut = {}
newvalue_dict_hist = {}
sumbin_dict_future = {}
sumbin_dict_hist = {}

# Initialize the dictionaries with SDM, GCM, and habitat keys
mean_newvalue_change = {}
mean_sum_bin_change = {}
mean_land_use_change = {}

for sdm in sdms:
    newvalue_dict_fut[sdm] = {}
    newvalue_dict_hist[sdm] = {}
    sumbin_dict_future[sdm] = {}
    sumbin_dict_hist[sdm] = {}
    mean_newvalue_change[sdm] = {}
    mean_sum_bin_change[sdm] = {}
    mean_land_use_change[sdm] = {}

    for gcm in gcms:
        newvalue_dict_fut[sdm][gcm] = {}
        newvalue_dict_hist[sdm][gcm] = {}
        sumbin_dict_future[sdm][gcm] = {}
        sumbin_dict_hist[sdm][gcm] = {}
        mean_newvalue_change[sdm][gcm] = {}
        mean_sum_bin_change[sdm][gcm] = {}
        mean_land_use_change[sdm][gcm] = {}

        for habitat in habitats:
            newvalue_dict_fut[sdm][gcm][habitat] = []
            newvalue_dict_hist[sdm][gcm][habitat] = []
            sumbin_dict_future[sdm][gcm][habitat] = []
            sumbin_dict_hist[sdm][gcm][habitat] = []

# Loop over all habitats
for habitat in habitats:
    for sdm in sdms:
        for gcm in gcms: 
            for taxa in taxas:# Use the variable name 'taxa' for simplicity; it represents habitats in this context
                dir_species = "/storage/scratch/users/ch21o450/data/LandClim_Output/" + sdm + "/" + taxa + "/EWEMBI/"
                available_file = os.listdir(dir_species)
                available_names = [x.split("_[1146].nc")[0] for x in available_file]

                species_names = available_names
                # Define the netCDF file path
                netcdf_path_format_future = "/storage/scratch/users/ch21o450/data/LandClim_Output/{}/{}/{}/{}/{}_[{}].nc"
                netcdf_path_format_hist = "/storage/scratch/users/ch21o450/data/LandClim_Output/{}/{}/EWEMBI/{}_[{}].nc"

            # Loop over all species
            for species_name in species_names:
                # Loop over all models
                for gcm in gcms:
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
                    newvalue_fut = ds_newvalue_fut["newvalue"]
                    newvalue_hist = ds_newvalue_hist["newvalue"]
                    sum_bin_future = ds_newvalue_fut["sum_bin"].isel(time=0)
                    sum_bin_hist = ds_newvalue_hist["sum_bin"].isel(time=0)

                    # Append the newvalue to the dictionaries
                    newvalue_dict_fut[sdm][gcm][habitat].append(newvalue_fut)
                    newvalue_dict_hist[sdm][gcm][habitat].append(newvalue_hist)
                    sumbin_dict_future[sdm][gcm][habitat].append(sum_bin_future)
                    sumbin_dict_hist[sdm][gcm][habitat].append(sum_bin_hist)

# Calculate the mean change from historical to future per sdm, per gcm, per habitat
for sdm in newvalue_dict_fut:
    for gcm in newvalue_dict_fut[sdm]:
        for habitat in newvalue_dict_fut[sdm][gcm]:
            if len(newvalue_dict_hist[sdm][gcm][habitat]) > 0 and len(newvalue_dict_fut[sdm][gcm][habitat]) > 0:
                newvalue_hist = xr.concat(newvalue_dict_hist[sdm][gcm][habitat], dim="species").sum(dim="species")
                newvalue_future = xr.concat(newvalue_dict_fut[sdm][gcm][habitat], dim="species").sum(dim="species")
                sum_bin_hist = xr.concat(sumbin_dict_hist[sdm][gcm][habitat], dim="species").sum(dim="species")
                sum_bin_future = xr.concat(sumbin_dict_future[sdm][gcm][habitat], dim="species").sum(dim="species")

                climate_change = (newvalue_future - newvalue_hist) / newvalue_hist  # Calculate change as percentage
                climate_land_change = (sum_bin_future - sum_bin_hist) / sum_bin_hist
                land_use_change = (climate_land_change - climate_change)

                climate_land_change_loss = climate_land_change.where(climate_land_change<0)
                climate_change_loss = climate_change.where((climate_land_change < 0) & (climate_change < 0))
                
                mean_newvalue_change[sdm][gcm][habitat] = climate_change_loss
                mean_sum_bin_change[sdm][gcm][habitat] = climate_land_change_loss
                mean_land_use_change[sdm][gcm][habitat] = land_use_change

# Calculate the mean change and uncertainties for each habitat
mean_values = {}
mean_sum_bin_change_habitat = {}  # Rename this to avoid conflicts
uncertainties_sdm_habitat = {}     # Rename this to avoid conflicts
uncertainties_gcm_habitat = {}     # Rename this to avoid conflicts

for habitat in habitats:
    mean_values[habitat] = []
    mean_sum_bin_change_habitat[habitat] = []  # Update the dictionary name
    uncertainties_sdm_habitat[habitat] = []     # Update the dictionary name
    uncertainties_gcm_habitat[habitat] = []     # Update the dictionary name

    for sdm in sdms:
        sdm_values = []
        sdm_land_use_values = []
        for gcm in gcms:
            sdm_values.append(mean_newvalue_change[sdm][gcm][habitat].mean().item())
            sdm_land_use_values.append(mean_sum_bin_change[sdm][gcm][habitat].mean().item())
        mean_values[habitat].append(np.mean(sdm_values))
        mean_sum_bin_change_habitat[habitat].append(np.mean(sdm_land_use_values))
        uncertainties_sdm_habitat[habitat].append(np.std(sdm_values))
    for gcm in gcms:
        gcm_values = []  # Moved this block inside the 'habitat' loop
        gcm_land_use_values = []  # Moved this block inside the 'habitat' loop
        for sdm in sdms:
            gcm_values.append(mean_newvalue_change[sdm][gcm][habitat].mean().item())
            gcm_land_use_values.append(mean_sum_bin_change[sdm][gcm][habitat].mean().item())
        uncertainties_gcm_habitat[habitat].append(np.std(gcm_values))

# Save the results
output_dir = "/storage/scratch/users/ch21o450/data/intermediate_results/"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, f"mean_newvalue_change_habitat_{scenario}_{time}_loss.pkl"), "wb") as f:
    pickle.dump(mean_newvalue_change, f)

with open(os.path.join(output_dir, f"mean_sum_bin_change_habitat_{scenario}_{time}_loss.pkl"), "wb") as f:
    pickle.dump(mean_sum_bin_change, f)

with open(os.path.join(output_dir, f"mean_land_use_change_habitat{scenario}_{time}_loss.pkl"), "wb") as f:
    pickle.dump(mean_land_use_change, f)

with open(os.path.join(output_dir, f"mean_values_habitat{scenario}_{time}_loss.pkl"), "wb") as f:
    pickle.dump(mean_values, f)

with open(os.path.join(output_dir, f"mean_sum_bin_change_habitat_{scenario}_{time}_loss.pkl"), "wb") as f:
    pickle.dump(mean_sum_bin_change_habitat, f)

with open(os.path.join(output_dir, f"uncertainties_sdm_habitat_{scenario}_{time}_loss.pkl"), "wb") as f:
    pickle.dump(uncertainties_sdm_habitat, f)

with open(os.path.join(output_dir, f"uncertainties_gcm_habitat_{scenario}_{time}_loss.pkl"), "wb") as f:
    pickle.dump(uncertainties_gcm_habitat, f)
