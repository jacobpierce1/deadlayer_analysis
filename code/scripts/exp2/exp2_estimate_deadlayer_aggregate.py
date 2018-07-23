import sys
import numpy as np

import os 

# from .. import deadlayer_estimator as dl_estimator 
sys.path.append('../')
import deadlayer_estimator as dl_estimator

# import exp1_geometry as geom 

import jspectroscopy as spec
import jutils 
import jutils.meas as meas 

import scipy.interpolate
import exp2_geometry

# CONFIG 

filter_above_channel_delta = 2.0

filter_above_sectheta = 1.2




db_names = [ 'full_bkgd_tot' ]

storage_path = '../../../storage/'


# strip_coords = 'all'

strip_coords = None



num_dets = 4 
num_sources = 2






# np.set_printoptions(threshold=np.nan)
# print( det_sectheta[0][0] )
# sys.exit(0)





    
# actual_energies = [ np.array( [ 3182.690 ] ),
#                     np.array( [ 5762.64, 5804.77 ] ) ]

    
actual_energies = [  [ 3182.690 ] ,
                     [ 0.231 * 5762.64  + 0.769 * 5804.77 ] ]

num_peaks_per_source = [ len( actual_energies[i] ) for i in range( num_sources ) ]


density_si = 2.328 # g / cm^3








# interpolate stopping power of alphas in Si using data
# in the range emin, emax. data is from astar program of NIST.
# uses scipy.interpolate.interp1d. if from_0_keV is 1, then
# interpolate over a lot of data to obtain large interpolation
# and set the 

def construct_si_stopping_power_interpolation( plot = 0 ) :

    # data = np.loadtxt( '../../data/stopping_power_data/alpha_stopping_power_si.txt',
    #                   skiprows = 10, unpack = 1 )

    energy, stopping_power = np.loadtxt(
        '../../../data/stopping_power_data/alpha_stopping_power_si.txt',
        usecols = [0,3], unpack = 1 )

    # tmp = np.loadtxt(
    #     '../../../data/stopping_power_data/alpha_stopping_power_si.txt',
    #     usecols = [0,3], unpack = 1 )

    
    # energy = data[0] * 1000
    
    # energy = energy[ energy <= emax ] 
    
    # stopping_power = data[3][ 0 : len( energy ) ]
    energy *= 1000 
    stopping_power *= density_si * 1000 * 100 / 1e9

    print( 'stopping power interp data:' )
    print( 'energy: ', energy )
    print( 'stopping: ', stopping_power )

    # add particular data points of interest to the interpolation
    
    interp = scipy.interpolate.interp1d( energy, stopping_power, kind = 'cubic' )

    
    if plot :

        ax = plt.axes()

        interp_axis = np.linspace( min( energy ), max( energy ), 100 )
        
        ax.scatter( energy, stopping_power, color='r' )

        ax.plot( interp_axis,
                 interp( interp_axis ),
                 color = 'b' )
        
        plt.show()

        return 1
        

    return interp
    


det_stopping_power_interp = construct_si_stopping_power_interpolation()

# print( det_stopping_power_interp( 5.5 ) )
# print( det_stopping_power_interp( 3.2 ) )
# sys.exit(0) 






model_params = dl_estimator.deadlayer_model_params( disable_sources = 0,
                                                    vary_det_deadlayer = 1,
                                                    interp_det_stopping_power = 1,
                                                    interp_source_stopping_powers = 0,
                                                    fstrips_requested = np.arange(1,30),
                                                    bstrips = np.arange( 1, 30 ),
                                                    fix_source_deadlayers = None,
                                                    one_source_constant = 0,
                                                    det_thickness = 0,
                                                    vary_source_thickness = 0,
                                                    constant_energy_offset = 0 )


db = spec.spectrum_db( 'full_bkgd_tot', storage_path )

# channels = db.load_dill( 'peaks' )
# peak_indices = [ [1], [0,1] ]
# num_peaks_per_source = [ len( x ) for x in peak_indices ]


channels = db.load_dill( 'means' )[1:]

peak_indices = [ [0], [0] ]

det_sectheta = exp2_geometry.get_secant_matrices()[1:]

source_sectheta = det_sectheta



# print( 'channels dimensions:')
# print( len( channels ) )
# print( len( channels[0] ) )
# print( len( channels[0][0] ) )
# print( len( channels[0][0][0] ) )



print( 'det_sectheta dimensions:' )
print( len( det_sectheta ) )
print( len( det_sectheta[0] ) )
print( len( det_sectheta[0][0] ) )
# print( len( channels[0][0][0] ) )


                    
if peak_indices is not None :
    for i in range( num_sources ) :
        channels[i] = [ channels[i][j]
                        for j in peak_indices[i] ]
                    
                

num_peaks_per_source = [ len( peak_indices[i] ) for i in range( num_sources ) ]    
print( 'num_peaks_per_source', num_peaks_per_source )

for d in range( num_dets ) : 
    for i in range( num_sources ) :
        
        mask = np.isnan( det_sectheta[i][d] )

        for j in range( num_peaks_per_source[i] ) :
            channels[i][j][ d ][ mask ] = meas.nan
    

        

# if filter_above_channel_delta > 0 :
    
#     for det in range( num_dets ) :
#         for i in range( num_sources ) :
#             for j in range( len( num_peaks_per_source ) ) :
#                 mask = ( channels[i][j][ det ].dx > filter_above_channel_delta )
#                 channels[i][j][ det ][ mask ] = meas.nan



if filter_above_sectheta > 0 :
    
    for det in range( num_dets ) :
        for i in range( num_sources ) :
            for j in range( num_peaks_per_source[i] ) :
                mask = ( det_sectheta[i][ det ] > filter_above_sectheta )
                channels[i][j][ det ][ mask ] = meas.nan

                    
        




# INITIAL FIT PARAMETERS 

# source_deadlayer_guesses = [ [ 6., 6.], [3.,3.], [15.,15.,15.,15.] ] 
source_stopping_power_interps = [ None ] * 3 
det_deadlayer_guess = 100.0
calibration_coefs_guess = [ 2.0, 0.0 ]
source_deadlayer_guesses = [ [25.0], [25.0] ] 


# print( len( channels ) )
# print( len( channels[0] ) ) 
# tmp = channels[ 0 ][1]
# print( len( tmp ) )
# print( len( tmp[0] ) )
# print( len( tmp[0][0] ) ) 


# strip_coords = 'all' 
# strip_coords = [0,2]

for detnum in  range(4) :

    # det_sectheta_tmp = [ det_sectheta[ detnum ] ]
    # source_sectheta_tmp = [ source_sectheta[ detnum ] ]
    # channels_tmp = [ channels[ 0 ][ detnum ] ]

    det_sectheta_tmp = [ [ det_sectheta[i][ detnum ]
                           for i in range( num_sources ) ] ]

    source_sectheta_tmp = det_sectheta_tmp 

    channels_tmp = [ [ [ channels[i][j][ detnum ]
                         for j in range( num_peaks_per_source[i] ) ] 
                       for i in range( num_sources ) ] ]


    print()
    print( len( channels_tmp ) ) 
    print( len( channels_tmp[0] ) )
    print( len( channels_tmp[0][0] ) )
    print( len( channels_tmp[0][0][0] ) )
    print() 
    
    dl_estimator.estimate_deadlayers( model_params,
                                      channels_tmp,
                                      actual_energies,
                                      det_sectheta_tmp,
                                      source_sectheta_tmp,
                                      source_stopping_power_interps,
                                      source_deadlayer_guesses,
                                      det_stopping_power_interp, det_deadlayer_guess,
                                      calibration_coefs_guess,
                                      names = db_names,
                                      strip_coords = strip_coords,
                                      figpath = '../../../storage/current_peaks_vs_sectheta/exp2_aggregate/det_%d/'
                                      % detnum ) 





# dl_estimator.estimate_deadlayers( dbs, source_indices,
#                                   model_params,
#                                   cut_high_sectheta = 0,
#                                   annotate = 0,
#                                   # view_pixel = [ dbmgr.moved, 5 ],
#                                   subtitle = 'Det 1: Absolute Calibration of Entire Detector\n',
#                                   reset_angles = None,
#                                   residual_scatter_plot = 0,
#                                   plot_3d = 1,
#                                   savefig_dir = '../../../deadlayer_analysis_paper/images/det1_calibration.eps' )













