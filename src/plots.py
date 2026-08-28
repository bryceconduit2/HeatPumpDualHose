import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual style
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.autolayout': True})

# Load the exact sheet and skip metadata rows to capture the header
excel_path = '../res/data/heatpump_cop.xlsx'
df = pd.read_excel(excel_path, sheet_name='heat pump', skiprows=15)
df.columns = df.iloc[0]
df = df.drop(0).reset_index(drop=True)

# Convert all data columns to numeric types and sort by source temperature
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.sort_values('Source Temperature /C').reset_index(drop=True)

# Extract numpy arrays to ensure compatibility
x_temp = df['Source Temperature /C'].to_numpy()
cop = df['COP'].to_numpy()
power_out = df['Est Heating Power Out /kW'].to_numpy()
power_in = df['Electricity Power in /kW'].to_numpy()
room_out = df['Room Out Temperature /C'].to_numpy()
room_in = df['Room In Temperature /C'].to_numpy()

# --- Plot 1: COP vs Source Temperature ---
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=x_temp, 
    y=cop, 
    s=100, 
    color='crimson', 
    label='Measured COP'
)
sns.regplot(
    x=x_temp, 
    y=cop, 
    scatter=False, 
    color='darkred', 
    line_kws={'linestyle':'--'}
)
plt.title('Coefficient of Performance (COP) vs. Source Temperature', fontsize=14, fontweight='bold')
plt.xlabel('Source Temperature (°C)', fontsize=12)
plt.ylabel('COP', fontsize=12)
plt.legend()
plt.savefig('../res/data/cop_vs_source_temp.png', dpi=300)
plt.show()

# --- Plot 2: Heating Power Output & Electrical Input vs Source Temperature ---
plt.figure(figsize=(10, 6))
plt.scatter(x_temp, power_out, color='teal',s=100, label='Est Heating Power Out (kW)')
plt.scatter(x_temp, power_in, color='orange',s=100, label='Electricity Power In (kW)')
plt.title('Heating Power Output and Electrical Input vs. Source Temperature', fontsize=14, fontweight='bold')
plt.xlabel('Source Temperature (°C)', fontsize=12)
plt.ylabel('Power (kW)', fontsize=12)
plt.legend(fontsize=11)
plt.savefig('../res/data/power_vs_source_temp.png', dpi=300)
plt.show()

# --- Plot 3: Room Temperatures (In vs Out) vs Source Temperature ---
plt.figure(figsize=(10, 6))
plt.scatter(x_temp, room_out, color='purple', s=100, label='Room Out Temperature')
plt.scatter(x_temp, room_in, color='dodgerblue', s=100, label='Room In Temperature')
plt.title('Room Temperatures vs. Source Temperature', fontsize=14, fontweight='bold')
plt.xlabel('Source Temperature (°C)', fontsize=12)
plt.ylabel('Temperature (°C)', fontsize=12)
plt.legend(fontsize=11)
plt.savefig('../res/data/temperatures_vs_source_temp.png', dpi=300)
plt.show()