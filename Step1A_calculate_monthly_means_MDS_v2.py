"""Contains the first of many preprocessing functions to prepare GCM data for synthetic TC generation"""
import numpy as np
import pandas as pd
import xarray as xr
import os
import matplotlib.pyplot as plt

__location__='__PATH_TO_DATA__'


def env_monthly_mean(
    model: list,
    version: list,
    grid: list,
) -> xr.DataArray:

    """Reads in GCM data and saves monthly mean SST and MSLP for CMIP6 HighResMIP models for 3 warming sceanarios.
    Output as .txt files used in preprocessing for synthetic TC 

    Args:
        model: CMIP6 HighResMIP GCM.
        version: GCM model variation
        grid: GCM grid label

    Returns:
        xr.DataArray containing monthly mean values for given variable for each month in warming scenario 
    References:
        * https://github.com/NBloemendaal/STORM-climate-change
        * https://help.ceda.ac.uk/article/4801-cmip6-data
        * https://ukesm.ac.uk/cmip6/variant-id/
    """

    for variable,variablename in zip(['psl','ts'],['MSLP','SST']):
        for warminglevel,year0list,year1list in zip(['1C','1.5C','2C'],[[1993,1994,1999,2004],[2012,2009,2015,2016],[2024,2020,2026,2025]],[[2012,2013,2018,2023],[2031,2028,2034,2035],[2043,2039,2045,2044]]):
            
            data = xr.open_mfdataset(os.path.join(__location__,'{}_Amon_{}_*_{}_{}_*.nc'.format(variable,model,version,grid)))
            print(model,warminglevel)
            df=data.sel(time=slice(str(year0list[mcount])+'-01-01', str(year1list[mcount])+'-12-31'))
                            
            for month in range(1,13):
                average=df.isel(time=(df.time.dt.month==month))[variable].mean('time')

                if variable=='psl' and np.nanmean(average)>3000: #then it's in Pa:
                    average/=100. #convert to hPa
                    
                np.savetxt(os.path.join(__location__,'Monthly_mean_{}_{}_{}_{}.txt'.format(variablename,model,month,warminglevel)),average)
            

    return data

def extract_lonlat(
    model: list,
    data: xr.DataArray,
) -> np.array:


    """Reads in GCM data, saves and returns lonlat grid to be used later in preprocessing
    Output as .txt files used in preprocessing for synthetic TC 

    Args:
        model: CMIP6 HighResMIP GCM.
        data: GCM model data at montly resolution

    Returns:
        array of lon/lat coordinates for a given GCM
    References:
        * https://github.com/NBloemendaal/STORM-climate-change
    """

    lonlat_data={i:[] for i in ['lat','lon']}
    lonlat_data['lon']=data['lon'].values
    lonlat_data['lat']=data['lat'].values 
    np.save(os.path.join(__location__,'latlon_background_converted_{}.npy'.format(model)),lonlat_data)
    return lonlat_data


"""Lines below execute first steps of preprocessing """

mcount=-1
for model,version,grid in zip(['CMCC-CM2-VHR4','CNRM-CM6-1-HR','EC-Earth3P-HR','HadGEM3-GC31-HM'],['r1i1p1f1','r1i1p1f2','r1i1p2f1','r1i3p1f'],['gn','gr','gr','gn']):
    mcount+=1

    data=env_monthly_mean(model,version,grid)
    lldata=extract_lonlat(model,data)


