import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# ---------------  Load and set up the data  ------------


# Load soil moisture data from shapefile
soil_moisture_shapefile = "SENTHYMED_MEDOAK_soil_moisture_coord_P.shp"
soil_moisture_data = gpd.read_file(soil_moisture_shapefile)

# Load soil moisture data from text file
soil_moisture_txtfile = "SENTHYMED_MEDOAK_soil_moisture_data.txt"
soil_moisture_txt_data = pd.read_csv(soil_moisture_txtfile, delimiter='\t')

# Handling missing data: Drop rows where any of the critical measurements are missing
soil_moisture_txt_data.dropna(subset=['Volumetric soil moisture', 'MEAS_DATE', 'MEAS_TIME'], inplace=True)

# Convert MEAS_DATE and MEAS_TIME to strings before concatenation and conversion to datetime
soil_moisture_txt_data['MEAS_DATE'] = soil_moisture_txt_data['MEAS_DATE'].astype(str)
soil_moisture_txt_data['MEAS_TIME'] = soil_moisture_txt_data['MEAS_TIME'].astype(str)
soil_moisture_txt_data['datetime'] = pd.to_datetime(soil_moisture_txt_data['MEAS_DATE'] + ' ' + soil_moisture_txt_data['MEAS_TIME'])

# Convert MEAS_DATE and MEAS_TIME to datetime
soil_moisture_txt_data['datetime'] = pd.to_datetime(soil_moisture_txt_data['MEAS_DATE'] + ' ' + soil_moisture_txt_data['MEAS_TIME'])


# --------- Preliminary data processing -------------


# Merge the data from shapefile and text file
soil_moisture_combined = soil_moisture_data.merge(soil_moisture_txt_data, on="ID_LOC")

# Convert 'Volumetric soil moisture' from string to float
soil_moisture_combined['Volumetric soil moisture'] = soil_moisture_combined['Volumetric soil moisture'].str.replace(',', '.').astype(float)

# Assuming soil_moisture_combined is your merged DataFrame with all necessary data
soil_moisture_for_scatter = soil_moisture_combined.copy()

## Convert 'datetime' into a numerical value for plotting (days since start)
soil_moisture_for_scatter['days_since_start'] = (soil_moisture_for_scatter['datetime'] - soil_moisture_for_scatter['datetime'].min()).dt.days


# -------------   Descriptive data for soil moisture ------------


# Print descriptive statistics for soil moisture
descriptive_stats = soil_moisture_combined['Volumetric soil moisture'].describe()
print("Descriptive Statistics for Soil Moisture:")
print(descriptive_stats)

# Identify any significant changes over time 
soil_moisture_combined['datetime'] = pd.to_datetime(soil_moisture_combined['MEAS_DATE'].astype(str) + ' ' + soil_moisture_combined['MEAS_TIME'].astype(str))
soil_moisture_combined['days_since_start'] = (soil_moisture_combined['datetime'] - soil_moisture_combined['datetime'].min()).dt.days
if 'days_since_start' in soil_moisture_combined.columns:
    mean_moisture_by_day = soil_moisture_combined.groupby('days_since_start')['Volumetric soil moisture'].mean()
    print("\nMean Soil Moisture by Day:")
    print(mean_moisture_by_day)
else:
    print("'days_since_start' column not found in DataFrame.")


# Highlight areas with high or low moisture levels
high_moisture = soil_moisture_combined[soil_moisture_combined['Volumetric soil moisture'] > soil_moisture_combined['Volumetric soil moisture'].quantile(0.9)]
low_moisture = soil_moisture_combined[soil_moisture_combined['Volumetric soil moisture'] < soil_moisture_combined['Volumetric soil moisture'].quantile(0.1)]
print(f"\nAreas with High Moisture (Top 10%): {high_moisture['SITE_PLOT'].unique()}")
print(f"Areas with Low Moisture (Bottom 10%): {low_moisture['SITE_PLOT'].unique()}")


#############################  Set up the plots ################################


# ----------------- Plot the moisture measurements for all plots ----------------


plt.figure(figsize=(15, 10))
plt.scatter(soil_moisture_for_scatter['days_since_start'], soil_moisture_for_scatter['Volumetric soil moisture'], 
            c=soil_moisture_for_scatter['SITE_PLOT'].astype('category').cat.codes, cmap='viridis')
# Create a colorbar with plot ID labels
plot_ids = soil_moisture_for_scatter['SITE_PLOT'].astype('category')
cbar = plt.colorbar(ticks=range(len(plot_ids.cat.categories)))
cbar.set_ticklabels(plot_ids.cat.categories)
cbar.set_label('Plot ID')
plt.title('Scatter Plot of Soil Moisture Measurements for All Plots', fontsize=20)
plt.xlabel('Days Since Start of Measurement', fontsize = 15)
plt.ylabel('Volumetric Soil Moisture (%)', fontsize = 15)
plt.xticks(rotation=45, fontsize = 12)
plt.yticks(fontsize=12)
plt.grid(True)
plt.tight_layout()


# ---------- Plot the spatial distribution ------------


soil_moisture_combined.crs = "EPSG:32633"
soil_moisture_combined = soil_moisture_combined.set_crs('EPSG:32633', allow_override=True)
soil_moisture_combined = soil_moisture_combined.to_crs('EPSG:4326') # Reprojecting to EPSG:4326
fig, ax = plt.subplots(figsize=(10, 6))
soil_moisture_combined.plot(column='Volumetric soil moisture', ax=ax, legend=True)
ax.set_title('Spatial Distribution of Soil Moisture Measurements', fontsize=18)
# Setting axis labels
ax.set_xlabel('Longitude', fontsize=15)
ax.set_ylabel('Latitude', fontsize=15)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()


# --------------  Plot the the volumetric soil moisture  ----------------


# Merge the data from shapefile and text file
soil_moisture_merge = soil_moisture_data.merge(soil_moisture_txt_data, on="ID_LOC")
soil_moisture_merge.sort_values('SITE_PLOT', inplace=True)

# Data Processing
soil_moisture_merge['Volumetric soil moisture'] = soil_moisture_merge['Volumetric soil moisture'].astype(str) # Ensure the entire 'Volumetric soil moisture' column is treated as strings
soil_moisture_merge['Volumetric soil moisture'] = soil_moisture_merge['Volumetric soil moisture'].str.replace(',', '.').astype(float) # Replace commas with dots and convert to float, coerce errors to NaN
soil_moisture_merge['SITE_PLOT_codes'] = soil_moisture_merge['SITE_PLOT'].astype('category').cat.codes # Convert 'SITE_PLOT' categories to numeric codes for plotting

# Mapping from SITE_PLOT_code to color
num_unique_plots = soil_moisture_merge['SITE_PLOT'].nunique() # Number of unique SITE_PLOT values
colors = plt.cm.viridis(np.linspace(0, 1, num_unique_plots)) # Generate a list of colors from a colormap
color_map = {code: colors[i] for i, code in enumerate(soil_moisture_merge['SITE_PLOT'].astype('category').cat.codes.unique())}

# Plotting
plt.figure(figsize=(12, 8))
scatter_colors = soil_moisture_merge['SITE_PLOT_codes'].map(color_map) # Apply the color map
plt.scatter(soil_moisture_merge['SITE_PLOT_codes'], soil_moisture_merge['Volumetric soil moisture'], color=scatter_colors)
plt.xticks(ticks=soil_moisture_merge['SITE_PLOT_codes'].unique(), labels=soil_moisture_merge['SITE_PLOT'].unique(), rotation=90)
plt.xlabel('Location (SITE PLOT)', fontsize = 15)
plt.ylabel('Volumetric Soil Moisture (%)', fontsize = 15)
plt.title('Volumetric Soil Moisture Measurements by Location',fontsize=20)
plt.grid(True)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.show()


# ------------ Plot relationship between volumetric soil moisture and temperature ----------------


# Data processing
soil_moisture_combined['Soil temperature'] = pd.to_numeric(soil_moisture_combined['Soil temperature'].str.replace(',', '.'), errors='coerce') # Convert 'Volumetric soil moisture' and 'Soil temperature' to float
soil_moisture_combined.dropna(subset=['Volumetric soil moisture', 'Soil temperature'], inplace=True) # Drop rows where conversion failed and resulted in NaNs

# Group by 'MEAS_DATE' and calculate mean for both 'Volumetric soil moisture' and 'Soil temperature'
daily_data = soil_moisture_combined.groupby('MEAS_DATE').agg({
    'Volumetric soil moisture': 'mean',
    'Soil temperature': 'mean'
}).reset_index()

# Convert 'MEAS_DATE' to datetime for plotting
daily_data['MEAS_DATE'] = pd.to_datetime(daily_data['MEAS_DATE'], format='%Y%m%d')

# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))
color = 'tab:red'
ax1.set_xlabel('Date', fontsize = 15)
ax1.set_ylabel('Volumetric Soil Moisture (%)', color=color, fontsize = 15)
ax1.plot(daily_data['MEAS_DATE'], daily_data['Volumetric soil moisture'], color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()   # Instantiate a second axes that shares the same x-axis
color = 'tab:blue'
ax2.set_ylabel('Soil Temperature (°C)', color=color, fontsize=15) 
ax2.plot(daily_data['MEAS_DATE'], daily_data['Soil temperature'], color=color)
ax2.tick_params(axis='y', labelcolor=color)
plt.subplots_adjust(top=0.85)
fig.tight_layout()  # to make sure there's no overlap
fig.suptitle('Daily Average Soil Moisture and Temperature', y=0.97, fontsize=16)  
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()
