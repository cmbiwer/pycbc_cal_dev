import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate

# TimeSeries, FrequencySeries
#import pycbc
#from pycbc import types
import pycbc.types

# set FFTW measure level to 0 so that time isn't wasted doing planning
from pycbc.fft.fftw import set_measure_level
set_measure_level(0)

def amp_to_dB(x):
    """Calculate the amplitude of the quantity x (could be complex) in decibels.
    """
    return 20.0*np.log10(np.abs(x))


def dB_to_amp(dB):
    """Convert decibels to amplitude.
    """
    return 10**(dB/20.0)


def zpk_file_to_array(filename):
    """Convert the contents of a zpk file with the columns [freq, real(H), imag(H)]
    to an array with columns [freq, real(H)+j*imag(H)].
    """
    data = np.loadtxt(filename)
    freq = data[:, 0]
    H = data[:, 1]+1.0j*data[:, 2]
    
    return np.array([freq, H]).T


def transfer_function_from_calibration_data(freqarray, Carray, Darray, Aarray, gamma=1.0):
    """Calculate the transfer function R(f) = (1+\gamma G(f)) / (\gamma C(f)) 
    where G(f) = C(f)D(f)A(f). \gamma is complex, but is 1.0 if there's no drift in the detector.
    """
    # Open loop gain
    Garray = Carray*Darray*Aarray
    Rarray = (1.0+gamma*Garray) / (gamma*Carray)
    return np.array([freqarray, Rarray]).T


def transfer_function_from_calibration_data_aligo(freqarray, Carray, Darray, Aarray, kappa_a=1.0, kappa_c=1.0, f_c=1.0):
    """Compute the transfer function R(f) from C, D, A, using the advanced LIGO convention
    for calibration errors.
    """
    # Open loop gain
    Garray = Carray*Darray*Aarray
    Rarray = (1.0+gamma*Garray) / (gamma*Carray)
    return np.array([freqarray, Rarray]).T


def transfer_function_error(Rtrue, Rmeasured):
    """Calculate the transfer function error K(f) = R_{measured}(f)/R_{true}(f) = (1+\delta A/A)e^{i\delta\phi}.
    Also calculate \delta A/A and \delta\phi.
    """
    
    K = Rmeasured/Rtrue
    dAbyA = np.abs(K)-1.0
    dphi = np.angle(K)
    return K, dAbyA, dphi


def adjust_strain_with_new_transfer_function(strain, freqarray, Carray, Darray, Aarray, gamma=1.0, plots=None):
    
    ############### Convert strain TimeSeries to FrequencySeries ##############
    strain_tilde = strain.to_frequencyseries()
    
    ############### Calculate the tranfer function error K(f) FrequencySeries #############
    
    # Just in case freqarray is complex128 but with 0 imaginary part:
    freq = np.real(freqarray)
    # Get the 'true' and 'measured' transfer functions
    Rtrue = transfer_function_from_calibration_data(freq, Carray, Darray, Aarray, gamma=1.0)[:, 1]
    Rmeasured = transfer_function_from_calibration_data(freq, Carray, Darray, Aarray, gamma=gamma)[:, 1]
    
    # Get the error function to apply to the strain in the frequency-domain
    K = Rmeasured/Rtrue
    
    # Decompose into amplitude and unwrapped phase
    Kamp = np.abs(K)
    Kphase = np.unwrap(np.angle(K))
    
    # Convert to a FrequencySeries by interpolating then resampling
    order = 1
    Kampoff = scipy.interpolate.UnivariateSpline(freq, Kamp, k=order, s=0)
    Kphaseoff = scipy.interpolate.UnivariateSpline(freq, Kphase, k=order, s=0)
    # Interpolation/vector operations are much faster if you convert FrequencySeries things to numpy arrays
    freq_even = strain_tilde.sample_frequencies.numpy()
    K_even_sample = Kampoff(freq_even)*np.exp(1.0j*Kphaseoff(freq_even))
    strain_tilde_adjusted = pycbc.types.FrequencySeries(strain_tilde.numpy()*K_even_sample, delta_f=strain_tilde.delta_f)
    
    ################### Convert back to TimeSeries ###################
    strain_adjusted = strain_tilde_adjusted.to_timeseries()
    # You have to manually set the start time again
    strain_adjusted.start_time = strain.start_time
    
    ################# make plots ################
    if plots:
        di = 10000
        
        # Make the amplitude error plot
        fig = plt.figure(figsize=(16, 8))
        axes = fig.add_subplot(211)
        axes.semilogx(freq_even[::di], np.abs(K_even_sample[::di]), ls='-', lw=2)
        axes.hlines(1.0, freq[0], freq[-1], linestyles=':')
        axes.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes.set_ylabel(r'$|K|$', fontsize=16)
        # Make the phase error plot
        axes = fig.add_subplot(212)
        axes.semilogx(freq_even[::di], np.unwrap(np.angle(K_even_sample[::di])), ls='-', lw=2)
        axes.hlines(0.0, freq[0], freq[-1], linestyles=':')
        axes.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes.set_ylabel(r'phase$(K)$', fontsize=16)
        
        fig = plt.figure(figsize=(16, 3))
        axes = fig.add_subplot(111)
        axes.loglog(strain_tilde.sample_frequencies.numpy()[::di], np.abs(strain_tilde.numpy()[::di]), ls='-', lw=2, label='true')
        axes.loglog(strain_tilde_adjusted.sample_frequencies.numpy()[::di], np.abs(strain_tilde_adjusted.numpy()[::di]), ls='-', lw=2, label='measured')
        axes.set_xlim([8.0, 10000.0])
        #axes.set_ylim([1e-24, 1e-22])
        axes.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes.set_ylabel(r'$|\tilde d|$', fontsize=16)
        axes.set_xticklabels(axes.get_xticks(), fontsize=14)
        axes.set_yticklabels(axes.get_yticks(), fontsize=14)
        axes.minorticks_on()
        axes.tick_params(which='major', width=2, length=8)
        axes.tick_params(which='minor', width=2, length=4)
        axes.legend(loc='best')
        
        fig = plt.figure(figsize=(16, 3))
        axes = fig.add_subplot(1, 1, 1)
        axes.plot(strain.sample_times.numpy()[::di], strain.numpy()[::di], ls='-', label='true')
        axes.plot(strain_adjusted.sample_times.numpy()[::di], strain_adjusted.numpy()[::di], ls='-', label='measured')
        axes.legend(loc='best')
    
    
    return strain_adjusted


###################################### Plots ###############################

def bode_plot(frequency_list, data_list, dB=False, degrees=False, unwrap=False, ylabel=None, labels=None):
    """Make a Bode plot (amplitude and phase as a function of frequency).
    
    Parameters
    ----------
    frequency_list : list of arrays
    data_list : list of complex arrays
    db : bool
        Plot the amplitude in decibels.
    degrees : bool
        Plot the phase in degrees (radians by default).
    unwrap : bool
        Unwrap the phase.
    """
    
    fig = plt.figure(figsize=(16, 6))
    axes1 = fig.add_subplot(121)
    axes2 = fig.add_subplot(122)
    
    for i in range(len(data_list)):
        freq = frequency_list[i]
        # Calculate amplitude and phase
        amplitude = np.abs(data_list[i])
        phase = np.angle(data_list[i])
        # Unwrap phase and convert from radians to degrees if desired
        if unwrap:
            phase = np.unwrap(phase)
        if degrees:
            phase = phase * 180.0/np.pi
        # Get legend label
        if labels:
            label=labels[i]
        else:
            label=str(i)
            
        # Make the amplitude plot
        if dB:
            dB_rescale = amp_to_dB(amplitude)
            axes1.semilogx(freq, dB_rescale, ls='-', lw=2, label=label)
        else:
            axes1.loglog(freq, amplitude, ls='-', lw=2, label=label)
        
        axes1.set_xlabel(r'$f$ (Hz)', fontsize=16)
        if ylabel: axes1.set_ylabel(ylabel, fontsize=16)
        axes1.set_xticklabels(axes1.get_xticks(), fontsize=14)
        axes1.set_yticklabels(axes1.get_yticks(), fontsize=14)
        axes1.minorticks_on()
        axes1.tick_params(which='major', width=2, length=8)
        axes1.tick_params(which='minor', width=2, length=4)
        #axes1.legend(loc='upper right')
        axes1.legend(loc='best')
        
        # Make the phase plot
        axes2.semilogx(freq, phase, ls='-', lw=2, label=label)
        axes2.set_xlabel(r'$f$ (Hz)', fontsize=16)
        if degrees:
            axes2.set_ylabel('Phase (degrees)', fontsize=16)
            pmin = np.floor(min(phase)/180.0)*180.0
            pmax = np.ceil(max(phase)/180.0)*180.0
            for p in np.arange(pmin, pmax, 180.0):
                axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
        else:
            axes2.set_ylabel('Phase (radians)', fontsize=16)
            pmin = np.floor(min(phase)/np.pi)*np.pi
            pmax = np.ceil(max(phase)/np.pi)*np.pi
            for p in np.arange(pmin, pmax, np.pi):
                axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
    
        axes2.set_xticklabels(axes2.get_xticks(), fontsize=14)
        axes2.set_yticklabels(axes2.get_yticks(), fontsize=14)
        axes2.minorticks_on()
        axes2.tick_params(which='major', width=2, length=8)
        axes2.tick_params(which='minor', width=2, length=4)
        #axes2.legend(loc='upper right')
        axes2.legend(loc='best')


def transfer_function_error_plot(frequency_list, Rtrue_list, Rmeasured_list, degrees=False, unwrap=False, labels=None):
    """Plot the fractional amplitude error and the absolute phase error for a list of transfer functions.
    
    Parameters
    ----------
    frequency_list : list of arrays
    Rtrue_list : list of complex arrays
        The true transfer functions.
    Rmeasured_list : list of complex arrays
        The measured transfer functions.
    degrees : bool
        Plot the phase in degrees (radians by default).
    unwrap : bool
        Unwrap the phase.
    """
    
    fig = plt.figure(figsize=(16, 6))
    axes1 = fig.add_subplot(121)
    axes2 = fig.add_subplot(122)
    
    for i in range(len(frequency_list)):
        freq = frequency_list[i]
        Rtrue = Rtrue_list[i]
        Rmeasured = Rmeasured_list[i]
        K, dAbyA, dphi = transfer_function_error(Rtrue, Rmeasured)
        # Unwrap phase and convert from radians to degrees if desired
        if unwrap:
            dphi = np.unwrap(dphi)
        if degrees:
            dphi = dphi * 180.0/np.pi
        # Get legend label
        if labels:
            label=labels[i]
        else:
            label=str(i)
            
        # Make the amplitude error plot
        axes1.semilogx(freq, dAbyA, ls='-', lw=2, label=label)
        axes1.hlines(0.0, freq[0], freq[-1], linestyles=':')
        axes1.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes1.set_ylabel(r'$\delta A/A$', fontsize=16)
        axes1.set_xticklabels(axes1.get_xticks(), fontsize=14)
        axes1.set_yticklabels(axes1.get_yticks(), fontsize=14)
        axes1.minorticks_on()
        axes1.tick_params(which='major', width=2, length=8)
        axes1.tick_params(which='minor', width=2, length=4)
        #axes1.legend(loc='upper right')
        axes1.legend(loc='best')
        
        # Make the phase plot
        axes2.semilogx(freq, dphi, ls='-', lw=2, label=label)
        axes2.set_xlabel(r'$f$ (Hz)', fontsize=16)
        if degrees:
            axes2.set_ylabel(r'$\delta\phi$ (degrees)', fontsize=16)
            #pmin = np.floor(min(dphi)/180.0)*180.0
            #pmax = np.ceil(max(dphi)/180.0)*180.0
            #for p in np.arange(pmin, pmax, 180.0):
            #    axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
        else:
            axes2.set_ylabel(r'$\delta\phi$ (radians)', fontsize=16)
            #pmin = np.floor(min(dphi)/np.pi)*np.pi
            #pmax = np.ceil(max(dphi)/np.pi)*np.pi
            #for p in np.arange(pmin, pmax, np.pi):
            #    axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
            
        axes2.hlines(0.0, freq[0], freq[-1], linestyles=':')
        axes2.set_xticklabels(axes2.get_xticks(), fontsize=14)
        axes2.set_yticklabels(axes2.get_yticks(), fontsize=14)
        axes2.minorticks_on()
        axes2.tick_params(which='major', width=2, length=8)
        axes2.tick_params(which='minor', width=2, length=4)
        #axes2.legend(loc='upper right')
        axes2.legend(loc='best')


############# old functions for messing with transfer function ###############

def transfer_function_fractional_amp_error(f):
    alpha = -0.2+0.2*f/1000.0
    return alpha
    
def transfer_function_phase_error(f):
    delta_phic = 0.0 # phase shift in radians
    delta_tc = 10.0 # time shift in seconds
    return delta_phic - 2*np.pi*f*delta_tc

def k_error(f):
    deltaabya = transfer_function_fractional_amp_error(f)
    deltaphi = transfer_function_phase_error(f)
    return (1.0+deltaabya)*np.exp(1.0j*deltaphi)
    #return 1.0+deltaabya


def adjust_frequency_series_with_new_transfer_function(strain_tilde):
    #k_array = k_error(strain_tilde.sample_frequencies)
    k_array = np.array([k_error(f) for f in strain_tilde.sample_frequencies])
    print k_array[0], k_array[-1]
    adjusted = strain_tilde * k_array
    return pycbc.types.FrequencySeries(adjusted, delta_f=strain_tilde.delta_f)


def adjust_strain_with_new_transfer_function_old(strain):
    
    epoch = strain.start_time
    
    # Fourier transform the time series, then return it as a FrequencySeries.
    # This does not set the epoch of the FrequencySeries. You have to do that manually.
    st = strain.to_frequencyseries()
    print epoch, st.epoch
    
    st_adjusted = adjust_frequency_series_with_new_transfer_function(st)
    s_adjusted = st_adjusted.to_timeseries()
    
    s_adjusted.start_time = epoch
    
    return s_adjusted







