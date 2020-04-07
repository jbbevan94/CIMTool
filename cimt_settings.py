'''
cimt_settings.py
Climate Impact Metrics Tool 'settings' file
'''

import ConfigParser
import ast

# ----------------------------------------------------------------------------------------------------
# Functions used in "cimt_settings.py" ---------------------------------------------------------------

def without_keys(d, keys):
    """
    Returns a copy of the input dictionary excluding keys specified in a list
    see: https://stackoverflow.com/questions/31433989/return-copy-of-dictionary-excluding-specified-keys 
    
    Parameters
    ----------
    d : original dictionary
    keys : a list of keys to exclude
    
    Returns
    -------
    dictionary: a subset of the original dictionary, without the specified keys 
    """
    return {k: v for k, v in d.items() if k not in keys} # NB- if this flags up with the error "Expected:}" in Eclipse you can ignore

def check_years(begin, end):
    """
    Checks if the input end year is greater than the input start year, if not then an error is raised
    
    Parameters
    ----------
    begin : an integer start year
    end : an integer end year
    """
    if int( begin ) >= int ( end ):
        raise StandardError("Make sure the end year is later than the start year!")
    
def check_period(period):
    """
    Checks if the input period is a valid option, and then allocates the period_type variable based
    on the user input. Common-sense User Warnings are also included to help user with debugging.
    """
    if 'ann' in period:
        if len(period) != 1:
            raise StandardError("In order to choose annual the period list must ONLY contain the string 'ann'" )
        period_type = 'annual'
        
    elif any(x in period for x in seasons) & any(x in period for x in months):
        raise StandardError("You have chosen both seasonal and monthly periods")
            
    elif any(x in period for x in seasons):
        for element in period:
            if element not in seasons:
                raise StandardError("You may have a typo when entering the seasons")
        period_type = 'seasonal'
        
    elif any(x in period for x in months):
        for element in period:
            if element not in months:
                raise StandardError("You may have a typo when entering the months")
        period_type = 'monthly'
            
    else:
        raise StandardError("Choose a correct list of string(s) for the period variable")
    
    return period_type

# Config Parser, for reference see the online documentation
# https://docs.python.org/2/library/configparser.html
Config = ConfigParser.ConfigParser()
Config.optionxform = str # Keeps as string, i.e. upper case is preserved

# Read in interface file
Config.read( "cimt_interface.ini" )

# Extract directories for loading and saving files
DATADIR = Config.get( 'environment' , 'DATADIR' ) # Directory of files
SAVEDIR = Config.get( 'environment' , 'SAVEDIR' ) # Output for saving

# ----------------------------------------------------------------------------------------------------
# Convert interface file to a settings_dict ----------------------------------------------------------
settings_dict = {}
for section in Config.sections():
    settings_dict[section] = {}
    for option in Config.options( section ):
        settings_dict[section][option] = Config.get( section , option )
        
# ----------------------------------------------------------------------------------------------------
# Extract general settings from settings_dict --------------------------------------------------------
impact_metric = settings_dict['settings']['impact_metric']
comparison_type = settings_dict['settings']['comparison_type']
map_type = settings_dict['settings']['map_type']
subtraction_type = settings_dict['settings']['subtraction_type']
output_type = settings_dict['settings']['output_type']

# ----------------------------------------------------------------------------------------------------
# Extract period list and apply appropriate checks ---------------------------------------------------
seasons = ['djf','mam','jja','son']
months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
period_list = ast.literal_eval( Config.get( "settings" , "period" ) )
period_type = check_period( period_list )

# ----------------------------------------------------------------------------------------------------
# Extract settings of the base job -------------------------------------------------------------------
base_description = settings_dict['base_jobs']['base_description'] 
base_start = settings_dict['base_jobs']['base_start']
base_end = settings_dict['base_jobs']['base_end']
check_years( base_start , base_end )

# Create a subset of 'setting_dict' which includes only the jobs names 
base_jobs_dict = without_keys( settings_dict['base_jobs'] , [ 'base_description' , 'base_start' , 'base_end' ] )

# ----------------------------------------------------------------------------------------------------
# Extract settings of the future jobs ----------------------------------------------------------------
future_description = []
future_start = []
future_end = []
future_jobs_dict = []

# Get the number of future jobsets defined by the user
number_of_future_jobsets = 0 ; mystr = 'future_jobs'

for key in settings_dict.keys():
    if key.startswith(mystr):
        number_of_future_jobsets += 1

# Loop over the number of future jobsets
for future_joblist in range( number_of_future_jobsets ): 
    future_description.append( settings_dict['future_jobs_' + str( future_joblist + 1 ) ]['future_description'] )
    future_start.append( int( settings_dict['future_jobs_' + str( future_joblist + 1 ) ]['future_start'] ) )
    future_end.append( int( settings_dict['future_jobs_' + str( future_joblist + 1 ) ]['future_end'] ) )
    check_years( future_start[future_joblist] , future_end[future_joblist] )
    future_jobs_dict.append( without_keys( settings_dict['future_jobs_' + str( future_joblist + 1 ) ] , [ 'future_description' , 'future_start' , 'future_end' ] ) )