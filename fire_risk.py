import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



# Load PAI data
pai_data_path = 'SENTHYMED_MEDOAK_canopy_plant_area_index_data.txt'
pai_df = pd.read_csv(pai_data_path, delimiter='\t')
pai_df['MEAS_DATETIME'] = pd.to_datetime(pai_df['MEAS_DATE'].astype(str) + ' ' + pai_df['MEAS_TIME'].astype(str), format='%Y%m%d %H:%M:%S')
pai_df = pai_df[pai_df['BAD_READINGS'] != 'ERROR'].copy() # Filter out bad readings
pai_df['PLOT'] = pai_df['SITE'] + '_' + pai_df['SITE_PLOT'] # Add plot identifier

# Extract date for daily aggregation
pai_df['Date'] = pai_df['MEAS_DATETIME'].dt.to_period('D')

# Load soil moisture data
soil_moisture_path = 'SENTHYMED_MEDOAK_soil_moisture_data.txt'
soil_moisture_df = pd.read_csv(soil_moisture_path, delimiter='\t')
soil_moisture_df['MEAS_DATETIME'] = pd.to_datetime(soil_moisture_df['MEAS_DATE'].astype(str) + ' ' + soil_moisture_df['MEAS_TIME'].astype(str), format='%Y%m%d %H:%M:%S')

# Convert 'Volumetric soil moisture' to numeric, handling errors
soil_moisture_df['Volumetric soil moisture'] = pd.to_numeric(soil_moisture_df['Volumetric soil moisture'], errors='coerce')
soil_moisture_df['PLOT'] = soil_moisture_df['SITE'] + '_' + soil_moisture_df['SITE_PLOT'] # Add plot identifier
soil_moisture_df['Date'] = soil_moisture_df['MEAS_DATETIME'].dt.to_period('D') # Extract date for daily aggregation


# Merging aggregated data on 'Date'
pai_daily = pai_df.groupby('Date')['PAI'].mean().reset_index() # Aggregate PAI data by Date
soil_moisture_daily = soil_moisture_df.groupby('Date')['Volumetric soil moisture'].mean().reset_index() # Aggregate Soil Moisture data by Date

# Convert 'Date' from Period to datetime for plotting
pai_daily['Date'] = pai_daily['Date'].dt.to_timestamp()
soil_moisture_daily['Date'] = soil_moisture_daily['Date'].dt.to_timestamp()


# ----------

# Plotting the relationship or trend between PAI and Volumetric Soil Moisture on the days where both data points are available.
fig, ax1 = plt.subplots()
color = 'tab:green'
ax1.set_xlabel('Date', fontsize = 15)
ax1.set_ylabel('PAI', color=color, fontsize = 15)

# Make sure 'Date' is in datetime format
ax1.plot(pd.to_datetime(pai_daily['Date']), pai_daily['PAI'])
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:brown'
ax2.set_ylabel('Volumetric Soil Moisture', color=color, fontsize = 15)
ax2.plot(pd.to_datetime(soil_moisture_daily['Date']), soil_moisture_daily['Volumetric soil moisture'], color=color)
ax2.tick_params(axis='y', labelcolor=color)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=15))  # Adjust interval as needed
plt.title('Relationship Between Volumetric Soil Moisture and PAI', fontsize = 16)
fig.autofmt_xdate()  # Auto format the x-axis labels to fit them better
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()

#-----
# Categorize risk level based on PAI

# Load PAI data
pai_df = pd.read_csv('SENTHYMED_MEDOAK_canopy_plant_area_index_data.txt', delimiter='\t')
pai_df = pai_df[pai_df['BAD_READINGS'] != 'ERROR']

# Categorize risk level based on PAI
pai_threshold_high = pai_df['PAI'].quantile(0.75)
pai_threshold_low = pai_df['PAI'].quantile(0.25)
pai_df['Risk_Level'] = pd.cut(pai_df['PAI'], bins=[0, pai_threshold_low, pai_threshold_high, pai_df['PAI'].max()], 
                              labels=['Low', 'Medium', 'High'])

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
pai_df[pai_df['Risk_Level'] == 'High']['PAI'].hist(alpha=0.5, color='red', label='High Risk PAI')
pai_df[pai_df['Risk_Level'] == 'Low']['PAI'].hist(alpha=0.5, color='green', label='Low Risk PAI')
plt.title('Distribution of PAI by Risk Level', fontsize = 20)
plt.xlabel('PAI', fontsize = 15)
plt.ylabel('Frequency', fontsize = 15)
plt.legend(fontsize = 15)
plt.show()

# --------------  Categorize risk level based on moisture in soil  -------------

# Define arbitrary thresholds for demonstration
pai_high_risk_threshold = pai_df['PAI'].quantile(0.75)
soil_moisture_low_risk_threshold = 5.0  # Placeholder, adjust based on your data

# Function to categorize risk based on PAI and soil moisture
def determine_fire_risk(pai, soil_moisture, pai_threshold, moisture_threshold):
    if pai >= pai_threshold and soil_moisture <= moisture_threshold:
        return 'High Risk'
    elif pai < pai_threshold and soil_moisture > moisture_threshold:
        return 'Low Risk'
    else:
        return 'Moderate Risk'

# Apply the function (assuming direct comparison is possible; adjust as needed)
risk_assessment = pai_df.apply(lambda row: determine_fire_risk(row['PAI'], 
                                                               soil_moisture_df['Volumetric soil moisture'].mean(),  # Example; adjust as needed
                                                               pai_high_risk_threshold, 
                                                               soil_moisture_low_risk_threshold), axis=1)

# Visualizing the distribution of risk levels
risk_levels = pd.Series(risk_assessment).value_counts()
risk_levels.plot(kind='bar', color=['orange', 'red', 'green'])
plt.title('Fire Risk Levels Based on PAI and Average Soil Moisture', fontsize = 15)
plt.xlabel('Risk Level', fontsize = 12)
plt.ylabel('Count', fontsize = 12)
plt.xticks(rotation=45, ha='right', fontsize = 15) 
plt.tight_layout()
plt.show()

# -------------   Descriptive statistics for analysis ------------

# Risk Level Categorization Based on Combined Factors:
risk_distribution = risk_assessment.value_counts(normalize=True) * 100
print("Distribution of Fire Risk Levels (%):\n")
print(risk_distribution)
print('\n')


# Temporal Trends and Seasonal Analysis:
pai_daily = pai_daily.groupby(pai_daily['Date'].dt.day).mean()
print("Average PAI changes per date:\n")
print(pai_daily)

