'''
cimt_metrics.py
Climate Impact Metrics Tool 'metrics' file
'''

import iris

import cimt_parent_metric

# ----------------------------------------------------------------------------------------------------
# Define each metric here ( skeleton is given below ) ------------------------------------------------

#class New_Metric( cimt_parent_metric.ImpactMetric ):
#    """
#    Child class for the New Metric.
#    """
#    def __init__( self ):
#        super( New_Metric , self ).__init__( 'Full_name_of_metric' , 'stash_number' , 'units' , 'unit_factor', 'cell_number' )
#        
#    def load_cube( self , job ):
#        
#        # Cube manipulation goes here
#        
#        return cube

# ----------------------------------------------------------------------------------------------------
        
class NPP( cimt_parent_metric.ImpactMetric ):
    """
    Child class for the Net Primary Productivity metric.
    """
    def __init__( self ):
        super( NPP , self ).__init__( 'Net_Primary_Productivity' , 'm01s03i262' , 'kg m^2 yr' , 31536000 , None )
        
    def load_cube( self , job ):
        variable = iris.AttributeConstraint( STASH = self.stash )
        cube = iris.load_cube( self.job_files_dict[job] , variable )
        
        return cube
    
# ----------------------------------------------------------------------------------------------------

class T_ROFF( cimt_parent_metric.ImpactMetric ):
    """
    Child class for the Total Runoff metric.
    """
    def __init__( self ):
        super( T_ROFF , self ).__init__( 'Total_Runoff' , [ 'm01s08i235' , 'm01s08i234' ] , 'mm day^-1' , 86400.0 , None )
       
    def load_cube( self , job ):
        variables = [] ; cubes_to_sum = []
        for stash in range( 0 , len( self.stash ) ):
            variables.append( iris.AttributeConstraint( STASH = self.stash[ stash ] ) )
            cubes_to_sum.append( iris.load_cube( self.job_files_dict[job] , variables[ stash ] ) )
              
        cube = sum( cubes_to_sum )
      
        return cube
    
# ----------------------------------------------------------------------------------------------------
        
class SOILM_1m( cimt_parent_metric.ImpactMetric ):
    """
    Child class for the Soil Moisture (up to 1m) metric.
    """
    def __init__( self ):
        super( SOILM_1m , self ).__init__( 'Soil_Moisture_1m' , 'm01s08i223' , 'm^3 m^-3' , 1 , [ 1 , 2 , 3 ] )
  
    def load_cube( self , job ):
        variable = iris.AttributeConstraint( STASH = self.stash )
        cube = iris.load_cube( self.job_files_dict[job] , variable )
        cubes_to_sum = []
        for layer in range( 0 , len( self.cell_number ) ):
            cubes_to_sum.append( cube.extract( iris.Constraint( soil_model_level_number = lambda cell: cell == self.cell_number[ layer ] ) ) )

        cube = sum( cubes_to_sum )
        
        return cube
    
# ----------------------------------------------------------------------------------------------------
    
class T1p5m( cimt_parent_metric.ImpactMetric ):
    """
    Child class for Temperature at 1.5M metric.
    """
    def __init__( self ):
        super( T1p5m , self ).__init__( 'Air_Temp_1.5m' , 'm01s03i236' , 'K' , 1 , None )
       
    def load_cube( self , job ):
        variable = iris.AttributeConstraint( STASH = self.stash )
        cube = iris.load_cube( self.job_files_dict[job] , variable )
        
        return cube