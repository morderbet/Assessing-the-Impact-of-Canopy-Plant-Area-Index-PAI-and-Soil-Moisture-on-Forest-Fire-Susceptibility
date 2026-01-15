import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# ---------------  Load and set up the data  ------------
# Load the PAI data
pai_data_path = 'SENTHYMED_MEDOAK_canopy_plant_area_index_data.txt'
pai_df = pd.read_csv(pai_data_path, delimiter='\t')  # Adjust delimiter if necessary

# Filter out bad readings (assuming 'BAD_READINGS' column indicates them)
pai_df = pai_df[pai_df['BAD_READINGS'] != 'ERROR']

# Convert MEAS_DATE to datetime format for easier handling of dates
pai_df['MEAS_DATE'] = pd.to_datetime(pai_df['MEAS_DATE'], format='%Y%m%d')

# Remove bad readings
pai_df = pai_df[pai_df['BAD_READINGS'].isnull()]

# Create a new column to differentiate plots in PSL and PUE
pai_df['PLOT'] = pai_df['SITE'] + '_' + pai_df['SITE_PLOT']


# --------- Preliminary data processing -------------

# Group by new plot identifier and date, then calculate mean PAI, excluding repetitions
grouped_pai = pai_df.groupby(['PLOT', pai_df['MEAS_DATE'].dt.to_period('M')])['PAI'].mean().reset_index()

# Convert MEAS_DATE from Period to datetime for plotting
grouped_pai['MEAS_DATE'] = grouped_pai['MEAS_DATE'].dt.to_timestamp()

# Plotting the Mean of Pai 
fig, ax = plt.subplots(figsize=(12, 6))
for plot, group in grouped_pai.groupby('PLOT'):
    ax.plot(group['MEAS_DATE'], group['PAI'], '-o', label=plot)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)


# -------------   Descriptive statistics for PAI ------------
    
# Summary Statistics of PAI Values:
print("Summary Statistics of PAI Values:")
print(pai_df['PAI'].describe())


# -----------  Set up the plot  --------------
    
# Formatting the date on the x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
ax.set_title('Mean Plot Effective PAI over 2021',fontsize = 20)
ax.set_xlabel('Date (dd/mm/yyyy)', fontsize = 12)
ax.set_ylabel('Mean Plot Effective PAI (m²/m²)', fontsize = 12)
plt.legend(title='Plot', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()


# Ensure grouping by 'PLOT' and then resampling monthly on 'MEAS_DATE'
# This avoids setting 'MEAS_DATE' as an index before resampling
pai_df.set_index('MEAS_DATE', inplace=True)
grouped_pai = pai_df.groupby('PLOT').resample('M')['PAI'].mean().reset_index()
grouped_pai['MEAS_DATE'] = pd.to_datetime(grouped_pai['MEAS_DATE'])

# Extract month numbers and map them to month names
grouped_pai['month'] = grouped_pai['MEAS_DATE'].dt.month
month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 
             7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
grouped_pai['month_name'] = grouped_pai['month'].map(month_map)


# -------------   Descriptive statistics for PAI ------------


# Comparison of Plots:
plot_averages = grouped_pai.groupby('PLOT')['PAI'].mean().sort_values(ascending=False)
print("\nAverage PAI by Plot (Descending Order):")
print(plot_averages)


# -----------  Set up the plot  --------------


# Plotting the monthly PAI distribution with month names
fig, ax = plt.subplots(figsize=(12, 6))

# Create a dot plot using 'month_name' instead of 'month_str'
sns.stripplot(x='month_name', y='PAI', hue='PLOT', data=grouped_pai, ax=ax, jitter=True,
              dodge=True,  # Separate points for each 'PLOT' by dodging
              marker='o',  
              palette='Set1',  # Use a predefined color palette
              alpha=0.7)   # Set transparency to make overlapping points more visible

plt.xticks(rotation=45, ha="right", fontsize=12)
plt.yticks(fontsize=12)
ax.set_title('Monthly PAI Distribution by Plot', fontsize=20)
ax.set_xlabel('Month', fontsize=14)
ax.set_ylabel('PAI (m²/m²)', fontsize=14)
plt.legend(title='Plot', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
plt.tight_layout()
plt.show()

