import pandas as pd
import matplotlib.pyplot as plt

# Load the data
soil_moisture_data = pd.read_csv('SENTHYMED_MEDOAK_soil_moisture_data.txt', delimiter='\t')
pai_data = pd.read_csv('SENTHYMED_MEDOAK_canopy_plant_area_index_data.txt', delimiter='\t')

# Data cleaning and type conversion
soil_moisture_data['Volumetric soil moisture'] = soil_moisture_data['Volumetric soil moisture'].str.replace(',', '.').astype(float)
soil_moisture_data['MEAS_DATE'] = pd.to_datetime(soil_moisture_data['MEAS_DATE'], format='%Y%m%d')
pai_data['MEAS_DATE'] = pd.to_datetime(pai_data['MEAS_DATE'], format='%Y%m%d')


# -----------  Set up the plots  --------------

# Plot Soil Moisture with Rolling Mean
plt.figure(figsize=(12, 6))
plt.scatter(soil_moisture_data['MEAS_DATE'], soil_moisture_data['Volumetric soil moisture'], s=10, label='Raw Data')
rolling_mean_soil_moisture = soil_moisture_data['Volumetric soil moisture'].rolling(window=7, center=True).mean()
plt.plot(soil_moisture_data['MEAS_DATE'], rolling_mean_soil_moisture, color='red', label='7-Day Rolling Mean')
plt.title('Soil Moisture Over Time', fontsize=20)
plt.xlabel('Date', fontsize=15)
plt.ylabel('Volumetric Soil Moisture', fontsize=15)
plt.legend()
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.show()

# Plot PAI Over Time with Rolling Mean
plt.figure(figsize=(12, 6))
plt.scatter(pai_data['MEAS_DATE'], pai_data['PAI'], s=10, label='Raw Data')
rolling_mean_pai = pai_data['PAI'].rolling(window=7, center=True).mean()
plt.plot(pai_data['MEAS_DATE'], rolling_mean_pai, color='red', label='7-Day Rolling Mean')
plt.title('PAI Over Time', fontsize = 20)
plt.xlabel('Date',  fontsize=15)
plt.ylabel('PAI', fontsize=15)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend()
plt.tight_layout()
plt.show()

# -------------   Descriptive statistics  ------------

print("Soil Moisture Descriptive Statistics:\n", soil_moisture_data['Volumetric soil moisture'].describe())
print("PAI Descriptive Statistics:\n", pai_data['PAI'].describe())

