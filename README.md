# HeatPumpDualHose
3D printing to convert cheap single hose heat pump to dual hose (heating/cooling). Photos show arrangment that has been operating since January 2024.  
**Under construction**

# Why?
Single-hose units expel conditioned indoor air outside, creating a vacuum which pulls outside air back into the house through cracks and gaps. Dual-hose systems draw outdoor air strictly through the second hose to exhaust heat, keeping indoor air pressure balanced. 

# Measurements
Following parameters measured:
- **Electricity Power In [kW]**: Using plug in power meter
- **Source Temperature [C]**: Using DHT 11 Temperature/Humidity Sensor attached to ESP8266 Wemos D1 Mini (in source location).
- **Room In Temperature [C]**: Using DHT 11 Temperature/Humidity Sensor attached to ESP8266 Wemos D1 Mini (in room location).
- **Room Out Temperature [C]**: Using DHT 11 Temperature/Humidity Sensor attached to ESP8266 Wemos D1 Mini (attached to heat pump out).
- **Air velocity [m/s]**: Using hand held anemometer.
- **Humidity [%]**: Using DHT 11 Temperature/Humidity Sensor attached to ESP8266 Wemos D1 Mini (attached to heat pump out).

Following parameters assumed:
- **Air volume [m^3/hour]**: From heat pump specifications.
- **Air density [kg/m^3]**: Assumed as 1.2 kg/m^3.

Calculated values:
- **Air heat capacity [KJ/K/kg]**: From lookup table vs air humidity
- **Massflow [kg/s]**: From air volume in m^3/second * air density. This was checked against anemometer calculated value.
- **Est thermal power out [kW]**: From heatpump massflow * air heat capacity * (Room out - Room in tempeatures)
- **COP [kW/kW]**: From thermal power out/electrical power in

# Heating Performance

Heat performance is measured in the dual hose mode only. Although no single hose comparison have been taken, for comparison the manufacturer data states a 1.8 kW output and a COP of 2.4.
Performance measurements are made with no other sources of heating running e.g. boiler/fan heater.
![Source Room Temperatures](res/data/temperatures_vs_source_temp.png)
*Figure 1: Temperature in/out of heat pump vs. heat pump source temperature.*

![Power Temperatures](res/data/power_vs_source_temp.png)
*Figure 2: Input/output electricity power vs. heat pump source temperature.*

![COP Temperatures](res/data/cop_vs_source_temp.png)
*Figure 3: COP (Heating) vs. heat pump source temperature.*


# Photos
![Internal view of heat pump arrangement](res/photos/internal.jpg)
*Figure 4: Internal view of heat pump arrangement.*

![External view of heat pump arrangement](res/photos/external.jpg)
*Figure 5: External view of heat pump arrangement. Set up for cooling mode.*

# Disclaimer

This project is an independent hobbyist modification involving exclusively external 3D-printed plastic ducting, adapters, and window panels. It is not affiliated with, endorsed by, or sponsored by Costway.

Structural, Safety and Security: Ensure all components are securely fitted to prevent accidental drops or compromised home security. In particular, the heat pump itself contains propane as the refrigerant so ensure this is securely fastened against accidental dropage to ensure no release of flammable materials. Make sure you are happy with the risks and any associated implications of using these instructions in any way.

No Warranty: All 3D printing files and project designs are provided "as is" without warranty of any kind. Replication and use of these designs are entirely at your own risk.
