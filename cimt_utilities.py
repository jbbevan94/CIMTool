'''
cimt_utilities.py
Climate Impact Metrics Tool 'utilities' file
'''

import os
import glob
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------------------------------
# Functions for loading directories ------------------------------------------------------------------

def get_apy_files( data_dir , runid ):
    """
    Creates a list of annual .pp files from a given directory, sorted chronologically.

    Parameters
    ----------
    datadir : string
        Full path to input .pp files. e.g: '/scratch/rkahana/1p5deg_srm/model_output/apy/hydrol_npp/'

    runid : string
        UM model job name (e.g. 'ajnjm')

    Returns
    -------
    python list
        A list of annual file names, chronologically sorted.
    """
    annual_files = glob.glob( data_dir + '/' + runid + '/*a.py*.pp' )
    annual_files.sort()

    return annual_files

# ----------------------------------------------------------------------------------------------------

def get_aps_files( datadir , runid , season ): 
    """
    Creates a list of seasonal .pp files from a given directory, sorted chronologically.

    Parameters
    ----------
    datadir : string
        Full path to input .pp files. e.g: '/scratch/rkahana/1p5deg_srm/model_output/aps/'

    runid : string
        UM model job name (e.g. 'ajnjm')

    Returns
    -------
    python list
        A list of seasonal file names, chronologically sorted.
    """
    seasonal_files = glob.glob( datadir + '/' + runid + '/*a.ps*' + season + '.pp' ) 
    seasonal_files.sort()
    
    return seasonal_files

# ----------------------------------------------------------------------------------------------------

def get_apm_files( datadir , runid , month ): 
    """
    Creates a list of monthly .pp files from a given directory, sorted chronologically.

    Parameters
    ----------
    datadir : string
        Full path to input .pp files. e.g: '/scratch/rkahana/1p5deg_srm/model_output/apm/'

    runid : string
        UM model job name (e.g. 'ajnjm')

    Returns
    -------
    python list
        A list of seasonal file names, chronologically sorted.
    """
    monthly_files = glob.glob( datadir + '/' + runid + '/*a.pm*' + season + '.pp' ) 
    monthly_files.sort()
    
    return monthly_files

# ----------------------------------------------------------------------------------------------------
# Functions for netCDF files -------------------------------------------------------------------------

def write_netcdf_file( data_dir , file_name , cube_out ):
    """
    Writes a netcdf file to the output location indicated

    Parameters
    ----------
    data_dir : string
        A full path to output files location

    file_name : string
        A meaningful output file name. for example: cube.long_name
    
    cube_out : cube
        The output cube to save
    """
    outfile = data_dir + '/' + file_name + '.nc'
    if not os.path.exists( outfile ):
        print 'Saving netCDF: ' , outfile
        iris.fileformats.netcdf.save( cube_out , outfile )
    else:
        print outfile , ' already exists. Please delete existing file first.'
    return

# ----------------------------------------------------------------------------------------------------

def read_netcdf_file( data_dir , file_name ):
    """
    Reads in a netcdf file from the input location indicated

    Parameters
    ----------
    data_dir : string
        A full pathname for nc files
    
    file_name : string
        nc filename
    """
    infile = data_dir + file_name
    print infile

    if os.path.exists( infile ):
        print 'Reading netCDF: ', infile
        iris.FUTURE.netcdf_promote = True
        cube_in = iris.load_cube( infile )
    else:
        print infile , 'Does not exist'
    return cube_in

# ----------------------------------------------------------------------------------------------------
# Functions for plots --------------------------------------------------------------------------------

def save_map_png( data_dir , file_name , cube_out ):
    """
    Saves a map plot as a .png file to the output location indicated

    Parameters
    ----------
    data_dir : string
        A full path to output .png location

    file_name : string
        A meaningful m file name. for example: cube.long_name
    
    cube_out : cube
        The output cube to save
    """
    outfile = data_dir + '/' + file_name + '.png'
    if not os.path.exists( outfile ):
        print 'Saving Plot: ' , outfile
        qplt.pcolormesh( cube_out ) # NB- Need more robust plot
        plt.savefig( outfile )
        plt.close()
    else:
        print outfile , ' already exists. Please delete existing file first.'
    return