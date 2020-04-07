'''
cimt_main.py
Climate Impact Metrics Tool 'main' file
'''

import cimt_settings
import cimt_metrics

ImpactMetric = getattr( cimt_metrics , cimt_settings.impact_metric )

for period_index in cimt_settings.period_list:
    BaseMetric = ImpactMetric()
    BaseMetric.load_modify_cubes( base_run = True , period = period_index  )
    BaseMetric.temporal_mean()
    BaseMetric.ensemble_mean()
    if cimt_settings.comparison_type == 'base_only':  
        BaseMetric.save_outputs() # Program terminates here if base-only
    else: 
        for instance_index in range( cimt_settings.number_of_future_jobsets ):
            FutureMetric = ImpactMetric()
            FutureMetric.load_modify_cubes( base_run = False , period = period_index , instance = instance_index )
            FutureMetric.temporal_mean()
            FutureMetric.ensemble_mean()
            FutureMetric.subtract_cubes( BaseMetric )
            FutureMetric.save_outputs( BaseMetric )