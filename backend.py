import pandas as pd
import pvlib
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

def calculate_avg_power(latitude, longitude, system_capacity_kw, tilt_deg, azimuth_deg, mountingplace):
    
    dataH,_,_ = pvlib.iotools.get_pvgis_hourly(
        latitude, longitude,
        raddatabase='PVGIS-SARAH2',
        start=2017, end=2019,
        components=False,
        surface_tilt=tilt_deg, surface_azimuth=azimuth_deg,
        pvcalculation=True,
        peakpower=system_capacity_kw, 
        mountingplace=mountingplace,
        loss=14,
        url='https://re.jrc.ec.europa.eu/api/v5_2/' # url for using the version 5.2
    )
    
    power_data = dataH['P'].values
    power_matrix = np.empty((3,8760))
    power_matrix[0] = power_data[:len(power_data)//3]
    power_matrix[1] = power_data[len(power_data)//3:2*len(power_data)//3]
    power_matrix[2] = power_data[2*len(power_data)//3:]
    
    avg_power = np.mean(power_matrix, axis=0)
    std_power = np.std(power_matrix, axis=0)
    
    yearly_power_production = np.sum(power_matrix, axis=1) / 1000
    avg_yearly = np.mean(yearly_power_production)
    error_yearly = np.std(yearly_power_production) / np.sqrt(2)
    
    return avg_power, std_power, avg_yearly, error_yearly, dataH



if __name__ == '__main__':
    # Example usage
    latitude = 46.0 
    longitude = 14.0
    system_capacity_kw = 1  # System capacity in kW
    tilt_deg = 30  # Tilt angle in degrees
    azimuth_deg = 0  # Azimuth angle in degrees
    mountingplace = 'building'

    avg_power, std_power, avg_yearly, error_yearly, data = calculate_avg_power(latitude, longitude, system_capacity_kw, 
                                                                               tilt_deg, azimuth_deg, mountingplace)
    print("Expected Yearly Energy Production:", avg_yearly, f" $\pm$ ", error_yearly, ' kWh.')
    plt.plot(avg_power)
    plt.show()
