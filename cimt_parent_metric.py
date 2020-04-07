'''
cimt_parent_metric.py
Climate Impact Metrics Tool 'parent-metric' file
'''

import abc
import iris
import iris.coord_categorisation as cat
from iris import analysis
from collections import OrderedDict

import cimt_utilities
import cimt_settings


# ----------------------------------------------------------------------------------------------------
# Parent-class for an Impact Metric ------------------------------------------------------------------

class ImpactMetric( object ):
    __metaclass__ = abc.ABCMeta # For setting up an abstract method (used later)
    """
    This is the parent class impact metric, general methods are defined here and will be inherited for every
    new metric added. A general constructor is set up to declare attributes such as the metrics full name, 
    stash number and units. These are then defined in the constructor of each new metric.
    
    To create a new metric, one can initiate a class (in the "cimt_metrics.py" file ) following the skeleton
    provided, in addition there will already be some examples of some current metrics installed.
    ----------------------------------------------------------------------------------------------------
    
    Some notes regarding how to specify attributes when defining a new class:
    
    Attributes
    ----------
    full_name_of_metric : string
        Use capitalized words separated by an underscore.
        Default setting: full_name_of_metric = None.
        
    stash_number : string OR a list of strings
        Use the UM stash number, following this format: 'm01s08i235'. If more than one stash is used,
        enter them as a list.
        Default setting: stash_number = None.
        
    units : string
        Defines the desirable units.
        Default setting: units = None.
        
    unit_factor : int / float
        A multiplication factor to convert the model output units into the desired units specified above. 
        Default setting: unit_factor = 1.
        
    cell_number : int OR a list of ints   #NB- need to check if works also with lbproc (max. min. temp) / veg types ...
        Apply specific constraints on cubes, for example: number of soil layers, land cover types,
        or max. and min. temperatures.  
        Default setting: cell_number = None.
    """
    # Constructor for parent class metric
    def __init__( self , full_name = None , stash = None , units = None , unit_factor = 1 , cell_number = None ):
        self.full_name = full_name
        self.stash = stash
        self.units = units
        self.unit_factor = unit_factor
        self.cell_number = cell_number
    
    # ----------------------------------------------------------------------------------------------------
    
    @classmethod # Class method to return list of available metrics in the tool (used for tutorial)
    def available_metrics( cls ):
        """
        Prints the currently available metrics for use with the tool.
        
        Returns
        -------
        A list of metrics in the form: <class 'cimt_metrics.MetricName'>
        
        Example
        -------
        list_metrics = cimt_metrics.ImpactMetric.available_metrics()
               
        """
        print cls.__subclasses__()
        
    # ----------------------------------------------------------------------------------------------------
    
    @abc.abstractmethod # Abstract method to load a cube, method will be different for each metric
    def load_cube( self , job ):
        """
        Method for loading a cube which makes use of iris.load_cube under certain constraints. These constraints
        are defined as attributes for the class, such as its stash number or cell number. 
        
        This method will be overwritten for each metric because there are varying levels of manipulation
        that may need to be done before (or after) loading a cube. A variety of operations can be considered
        such as using multiple stash numbers, accessing particular cell levels or addition/subraction of cubes.
        
        The final result should always be a cube. This is an abstract method and so returns nothing, see the 
        "cimt_metrics.py" file to see where to define load_cube() for a specific metric.
        
        Parameters
        ----------
        job: int
            An iterator indicating the current job

        Returns
        -------
        iris cube
            A cube which feeds into load_modify_cubes() and is iterated over the number of jobs in the joblist.
        """        
        return
        
    # ----------------------------------------------------------------------------------------------------
    
    # Method which is used for demonstration in the tutorial
    def print_info( self ):
        """
        Prints some information to the user about the current metric
        
        Returns
        -------
        A print statement of the metrics name, stash number and units.
               
        """
        print 'Metric name: ' + self.full_name
        print 'Stash number: ' + self.stash
        print 'Metric units: ' + self.units
        
        return
    
    # ----------------------------------------------------------------------------------------------------
    
    # Private method called within load_modify_cubes()
    def __get_files( self , jobs_dict , period ):
        """
        Loads directories to files requested in order to complete extraction.
        
        Parameters
        ----------            
        jobs_dict: dictionary
            Dictionary of UM job names, extracted by "cimt_settings.py" from the user
            defined jobnames in 'cimt_interface.ini'
            
        period : string
            String input from the user indicating the types of files, e.g. 'ann' for annual
        
        Returns
        -------
        job_files_dict : dictionary
            Dictionary of full pathname for each input file.
        """
        self.job_files_dict = {}
        
        for job , jobname in jobs_dict.iteritems():
            
            if cimt_settings.period_type == 'annual':
                self.job_files_dict[job] = cimt_utilities.get_apy_files( cimt_settings.DATADIR , jobs_dict[job] )
                
            elif cimt_settings.period_type == 'seasonal':
                season = period
                self.job_files_dict[job] = cimt_utilities.get_aps_files( cimt_settings.DATADIR , jobs_dict[job] , season )
                
            elif cimt_settings.period_type == 'monthly':
                raise StandardError("Monthly files available soon!")
                
            else:
                raise StandardError("Select a valid period type!")
            
        return self.job_files_dict
    
    # ----------------------------------------------------------------------------------------------------
            
    def load_modify_cubes( self , base_run = None , period = None , instance = None ):
        """
        Method to load data from UM output files for job into an IRIS cube according to the constraints defined
        in the metric class, and period defined in the user configuration file.
        
        Then modify the cube by changing its name and units, adding a 'year' coordinate
        and update attributes.

        Parameters
        ----------
        base_run : boolean
            This is used as an identifier for the metric, when we flag this as true it tells the program
            that the metric is defined to be a base run. The default setting is False.
            
        period : string
            String input from the user indicating the types of files, e.g. 'ann' for annual
            
        instance : integer
            This is used as an iterator when looping over a number of future joblists so that the program 
            can extract information from 'cimt_settings.py' correctly

        Returns
        -------
        metric.cubes
            A list of cubes loaded for a specific metric.
        
        Example
        -------
        Load and modify cubes: 
            BaseMetric.load_modify_cubes( base_run = True )
        
        Print list of cubes:
            BaseMetric.cubes     
        
        """
        self.base_run = base_run
        self.period = period
        self.instance = instance
        
        # Set the self parameters
        if self.base_run == True: # Case for the base metric
            self.jobs_dict = cimt_settings.base_jobs_dict
            self.job_description = cimt_settings.base_description
            self.start_year = int( cimt_settings.base_start )
            self.end_year = int( cimt_settings.base_end )
            self.year_difference = self.end_year - self.start_year # Not used at the moment
            print 'Preparing to load cubes for Base Metric: ' + self.job_description
            
        elif self.base_run == False: # Case for a future metric
            self.jobs_dict = cimt_settings.future_jobs_dict[instance]
            self.job_description = cimt_settings.future_description[instance]
            self.start_year = int( cimt_settings.future_start[instance] )
            self.end_year = int( cimt_settings.future_end[instance] )
            self.year_difference = self.end_year - self.start_year # Not used at the moment
            print 'Preparing to load cubes for Future Metric: ' + self.job_description

        # Rename the class instance according to input start and end year 
        self.name = self.__class__.__name__ + '_(' + str( self.start_year ) + '-' + str( self.end_year ) + ')_'
            
        # Initialise some lists for storing loaded cubes, desired output cubes and jobnames (for internal naming)
        self.cubes = [] ; self.cubes_to_output = [] ; self.list_jobnames = []
        
        # Get files for loading cubes, sort into numeric order with OrderedDict
        self.job_files_dict = OrderedDict( sorted( self.__get_files( self.jobs_dict , period ).items() , key = lambda x: x[1] ) )
        
        # Loop over number of jobs in the joblist
        for job , path in self.job_files_dict.iteritems():
            
            # Check for mis-match between period and location of files
            if len( self.job_files_dict[job] ) == 0:
                raise StandardError("There is a problem loading the files requested, check that the period type matches the type of files requested in the string DATADIR")
                
             # Calls the abstract method load_cube() which is DIFFERENT depending on metric
            cube = self.load_cube( job )           
                    
            print 'Loading Cube: ' + self.name + str( self.jobs_dict[job] ) + '_' + self.period
            
            self.list_jobnames.append( str( self.jobs_dict[job] ) )
            
            # Apply this to all cubes no matter the metric type
            cat.add_year( cube , 'time' , name = 'year' ) # NB- Specific to annual, update attributes for cubes with other period types
        
            cube = cube * self.unit_factor
            cube.units = self.units
            cube.rename( self.name + str( self.jobs_dict[job] ) + '_' + self.period )
            
            # Update cube.attributes for all cubes
            cube.attributes.update({'Source': 'Data from Met Office Unified Model',
                                    'Created by': 'Climate Impacts Metrics Tool',
                                    'Stash Number': self.stash
                                    })

            # Extract all yearly files within given range
            if self.start_year != None:
                cube = cube.extract( iris.Constraint( year = lambda cell: self.start_year <= cell <= self.end_year ) )
                
            # NB- Should use self.year_difference to check for requested files between those years
                
            # Append this cube to cubes
            self.cubes.append( cube )
                        
        return self.cubes
    
    # ----------------------------------------------------------------------------------------------------
    
    def temporal_mean( self , input_cubes = None ):
        """
        TemporalMean reduces the cubes dimensions to produce a 2D map. It is taking a mean over the time
        dimension.
        
        Parameters
        ----------
        input_cubes : list of iris cubes
            Choice for user to input desired input cubes, if left empty program will use self.cubes
            Default setting: input_cubes = None.

        Returns
        -------
        metric.maps
            A list of cubes with a flattened (collapsed) time-dimension.
            can be called by typing metric.maps
        """
        self.maps = []

        if input_cubes == None: # If user doesn't specify input cubes set them to be equal to self.cubes
            input_cubes = self.cubes
        
        for job in range( len( input_cubes ) ):
            self.maps.append( input_cubes[job].collapsed( 'time' , iris.analysis.MEAN ) )
            
            # Append cubes to output list based on interface choices
            if cimt_settings.map_type == 'pre_subtraction' or cimt_settings.map_type == 'both':
                if cimt_settings.subtraction_type == 'each_member' or cimt_settings.subtraction_type == 'both':
                    self.cubes_to_output.append( input_cubes[job].collapsed( 'time' , iris.analysis.MEAN ) )
         
        return self.maps
    
    # ----------------------------------------------------------------------------------------------------
    
    def spatial_mean( self , input_cubes = None ):
        """
        SpatialMean reduces the cubes dimensions to produce a mean value over the entire domain
        (if the time dimension = 1), or a time-series (if the time dimension > 1).
        It is taking a area-weighted mean over the latitude/longitude dimensions.
        
        At the moment the program is assuming that the user is not interested in storing multiple plots
        of spatial means and associated plots, this can be changed if needed refer to TemporalMean().
        
        Parameters
        ----------
        input_cubes : list of iris cubes
            Choice for user to input desired input cubes, if left empty program will use self.cubes
            Default setting: input_cubes = None.

        Returns
        -------
        metric.time_series
            A list of cubes with flattened (collapsed)  lat/long dimension can be called by typing metric.time_series
        """
        self.time_series = []
        
        if input_cubes == None: # If user doesn't specify input cubes set them to be equal to self.cubes
            input_cubes = self.cubes
        
        for job in range( 0 , len( input_cubes ) ):
            
            if input_cubes[job].coord( 'latitude' ).has_bounds() == False:
                input_cubes[job].coord( 'latitude' ).guess_bounds()
                
            if input_cubes[job].coord( 'longitude' ).has_bounds() == False:
                input_cubes[job].coord( 'longitude' ).guess_bounds()
            
            grid_areas = iris.analysis.cartography.area_weights( input_cubes[job] )
            self.time_series.append( input_cubes[job].collapsed( ['longitude', 'latitude'] , iris.analysis.MEAN , weights = grid_areas ) )
                
        return self.time_series

    # ----------------------------------------------------------------------------------------------------
    
    def ensemble_mean( self , input_cubes = None ):
        """
        Calculates a simple ensemble mean for any number of jobs (simulations) in a joblist and writes them into a
        "self.ens_mean" object. 
        If there is only one job, the "self.ens_mean" is still created with the data of the individual cube.
        
        Parameters
        ----------
        input_cubes : list of iris cubes
            Choice for user to input desired input cubes, if left empty program will use either self.maps
            or self.time_series.
            Default setting: input_cubes = None.

        Returns
        -------
        metric.ens_mean
            A cube which is either an ensemble mean of a number of jobs or a single job's data
        """
        if input_cubes == None:
            input_cubes = self.maps

        if len( input_cubes ) == 1: # Don't need to compute ensemble mean if only one job
            self.ens_mean = input_cubes[0]
            
        elif len( input_cubes ) > 1: # Compute ensemble mean
            self.ens_mean = ( sum( input_cubes ) / len( input_cubes ) )
            self.ens_mean.units = self.units
            self.ens_mean.rename( self.name + 'Ensemble_Mean_' + self.job_description + '_' + self.period  )
            
        # Append cubes to output list based on interface choices
        if cimt_settings.map_type == 'pre_subtraction' or cimt_settings.map_type == 'both':
            if cimt_settings.subtraction_type == 'ensemble_mean' or cimt_settings.subtraction_type == 'both':
                self.cubes_to_output.append( self.ens_mean )
        
        return self.ens_mean
    
    # ----------------------------------------------------------------------------------------------------
    
    def subtract_cubes( self , other ):
        """
        SubtractCubes will subtract two cubes from each other to obtain an anomaly map.
        
        By convention the future metric is the cube we call the method on and the argument is the
        base (reference) metric.
        For example: "FutureMetric.subtract_cubes( BaseMetric )" means: "FutureMetric - BaseMetric"
        
        At the moment there is no option for the user to define their own cube arguments and subtract, if this
        was required one could implement by adding the argument "input_cubes" and follow similar structure in
        previous methods.
    
        Parameters
        ----------
        other : metric
            A metric which is defined to be the base run, i.e. Metric.base_run == True

        Example
        -------
        FutureMetric[instance].subtract_cubes( BaseMetric )
        
        Returns
        -------
        self.subtracted_cube
            A subtracted cube of the self.metric - other.metric
        """        
        self.subtracted_cubes = []
        
        if cimt_settings.subtraction_type == 'each_member' or cimt_settings.subtraction_type == 'both':
            
            future_cubes = self.maps
            base_cubes = other.maps
                
            if len( future_cubes ) != len( base_cubes ):
                raise StandardError( "Number of jobs in base and future metrics don't match" )
            for member in range( len( future_cubes ) ):
                subtracted_cube = future_cubes[member] - base_cubes[member]
                subtracted_cube.units = self.units
                subtracted_cube.rename( self.name + '[' + self.list_jobnames[member] + '-' + other.list_jobnames[member] + ']_(' + str( other.start_year ) + '-' + str( other.end_year ) + ')' + '_' + self.period )
                self.subtracted_cubes.append( subtracted_cube )
                
                if cimt_settings.map_type == 'anomaly_map' or cimt_settings.map_type == 'both':
                    self.cubes_to_output.append( subtracted_cube )
            
        if cimt_settings.subtraction_type == 'ensemble_mean' or cimt_settings.subtraction_type == 'both':
            
            subtracted_cube = self.ens_mean - other.ens_mean
            subtracted_cube.units = self.units
            subtracted_cube.rename( self.name + '[' + self.job_description + '-' + other.job_description + ']_(' + str( other.start_year ) + '-' + str( other.end_year ) + ')' + '_' + self.period )
            self.subtracted_cubes.append( subtracted_cube )
            
            if cimt_settings.map_type == 'anomaly_map' or cimt_settings.map_type == 'both':
                self.cubes_to_output.append( subtracted_cube )
        
        return  self.subtracted_cubes
    
    # ----------------------------------------------------------------------------------------------------
    
    def save_outputs( self , other = None ):
        """
        Saves maps and netcdf files according to the 'output_type' choice in the interface file.
        
        Parameters
        ----------
        other : metric
            A metric which is usually the base metric
            Default setting: other = None
        """
        if cimt_settings.output_type == 'map' or cimt_settings.output_type == 'both': # For saving data as a .png file
            for map in range( len( self.cubes_to_output ) ):
                cimt_utilities.save_map_png( cimt_settings.SAVEDIR , self.cubes_to_output[map].long_name , self.cubes_to_output[map] )
            if other != None:
                for map in range( len( other.cubes_to_output ) ):
                    cimt_utilities.save_map_png( cimt_settings.SAVEDIR , other.cubes_to_output[map].long_name , other.cubes_to_output[map] )
        
        if cimt_settings.output_type == 'map_data' or cimt_settings.output_type == 'both': # For saving data as a .nc file
            for map in range( len( self.cubes_to_output ) ):
                cimt_utilities.write_netcdf_file( cimt_settings.SAVEDIR , self.cubes_to_output[map].long_name , self.cubes_to_output[map] )
            if other != None:
                for map in range( len( other.cubes_to_output ) ):
                    cimt_utilities.write_netcdf_file( cimt_settings.SAVEDIR , other.cubes_to_output[map].long_name , other.cubes_to_output[map] )