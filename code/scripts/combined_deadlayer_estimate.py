import numpy as np
import scipy.optimize 
import scipy.interpolate 
import numdifftools




cf_energies = np.array( [  5704, 5759.5, 5783.3, 5813.3, 5849.3 ] )
cf_probs = np.array( [ 0.0003, 0.0469, 0.0026, 0.822, 0.01430  ] )
cf_probs /= np.sum( cf_probs )

pu_energies = np.array( [ 5123.68, 5168.17 ] ) 
pu_probs = np.array( [ 0.2710, 0.7280 ] )
pu_probs /= np.sum( pu_probs )



gd_energy =  3182.690

cm_energies = [ 5762.64,  5804.77 ] 
cm_probs = [ 0.231,  0.769 ]




data = np.array( [
    53.99,
    48.06,
    48.14,
    42.37,
    39.8281561,
    29.2330508,
    30.3482182,
    21.3137402,
    38.2670312,
    25.3025039
] )



errors = np.array( [
    1.5,
    0.96,
    1.6,
    1.5,
    0.474918, # gd det 2
    0.613169, # cm get 2 
    0.541718,
    0.830304,
    0.470542,
    0.632588
    ,0.361234,
    0.822255
] )




density_si = 2.328 # g / cm^3

def construct_si_stopping_power_interpolation( plot = 0 ) :

    # data = np.loadtxt( '../../data/stopping_power_data/alpha_stopping_power_si.txt',
    #                   skiprows = 10, unpack = 1 )

    energy, stopping_power = np.loadtxt(
        '../../data/stopping_power_data/alpha_stopping_power_si.txt',
        usecols = [0,3], unpack = 1 )

    energy *= 1000 
    stopping_power *= density_si * 1000 * 100 / 1e9

    print( 'stopping power interp data:' )
    print( 'energy: ', energy )
    print( 'stopping: ', stopping_power )
    
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
    




stop = construct_si_stopping_power_interpolation()


stopping_powers = {
    'gd' : stop( gd_energy ),
    'cm' : np.dot( cm_probs, stop( cm_energies ) ),
    'pu' :  np.dot( pu_probs, stop( pu_energies ) ),
    'cf' :  np.dot( cf_probs, stop( cf_energies ) )
}




def objective( params ) :
    det1_old_dl, det1_dl, det2_dl, det3_dl, det4_dl, pu, cf, gd, cm = params

    resid = np.array( [
        data[0] - pu - stopping_powers[ 'pu' ] * det1_old_dl,
        data[1] - cf - stopping_powers[ 'cf' ] * det1_old_dl,
        data[2] - pu - stopping_powers[ 'pu' ] * det3_dl,
        data[3] - cf - stopping_powers[ 'cf' ] * det3_dl,
        data[4] - gd - stopping_powers[ 'gd' ] * det2_dl,
        data[5] - cm - stopping_powers[ 'cm' ] * det2_dl,
        data[6] - gd - stopping_powers[ 'gd' ] * det3_dl,
        data[7] - cm - stopping_powers[ 'cm' ] * det3_dl,
        data[8] - gd - stopping_powers[ 'gd' ] * det4_dl,
        data[9] - cm - stopping_powers[ 'cm' ] * det4_dl,
        data[10] - gd - stopping_powers[ 'gd' ] * det1_dl,
        data[11] - cm - stopping_powers[ 'cm' ] * det1_dl,
    ] )

    resid #  /= errors 

    return np.sum(  resid ** 2 )
    # return resid


params_guess = np.array( [ 130.0, 130.0, 130.0, 130.0, 130.0, 50.0, 50.0, 10.0, 10.0 ] ) 



# ret = scipy.optimize.minimize( objective, params_guess, method = 'nelder-mead',
#                                       options = { 'maxiter' : 1e7, 'xatol' : 1e-12, 'fatol' : 1e-12 } ) 
# print( ret ) 

# hessian_func = numdifftools.Hessian( objective, full_output=True )
# hessian, info = hessian_func( ret.x ) 

# try: 
#     cov = np.linalg.inv( hessian ) 
# except( np.linalg.LinAlgError ) :
#     self.cov = None 
#     self.success = 0
    
            
# params_result = ret.x
# chisqr = ret.fun

# print( params_result )
# nfree = len( data ) - len( params_result ) 
# redchisqr = chisqr / nfree
# print( chisqr ) 
# print( redchisqr ) 

# params_result_errors = np.sqrt( np.diag( cov ) * redchisqr )
# print( params_result_errors ) 




# ret = scipy.optimize.leastsq( objective, params_guess,
#                               full_output = 1, ftol = 1e-12,
#                               xtol = 1e-12, maxfev = int(1e7) )

# params_result, cov, info, msg, status = ret

# chisqr = np.sum( info['fvec']**2 )
# nfree = len( data ) - len( params_guess ) 
# redchisqr = chisqr / nfree

# params_result_errors = np.sqrt( np.diag( cov ) * redchisqr )


# print( redchisqr ) 
# print( params_result )
# print( params_result_errors ) 




ret = scipy.optimize.basinhopping( objective, params_guess, disp = 1 ) 
print( ret ) 

# hessian_func = numdifftools.Hessian( objective, full_output=True )
# hessian, info = hessian_func( ret.x ) 

# print( dir( ret.lowest_optimization_result ) ) 

cov = ret.lowest_optimization_result.hess_inv
    
            
params_result = ret.x
chisqr = ret.fun

print( params_result )
nfree = len( data ) - len( params_result ) 
redchisqr = chisqr / nfree
print( chisqr ) 
print( redchisqr ) 

params_result_errors = np.sqrt( np.diag( cov ) * redchisqr )
print( params_result_errors ) 

