import mne
from mne.time_frequency import read_csd, read_spectrum, read_tfrs
import glob
from src import config
import numpy as np
import matplotlib.pyplot as plt
from beartype import beartype

@beartype
def add_to_report(report: mne.Report, subject_num: str):


    epochs_combined = mne.read_epochs(glob.glob("*combined_epo.fif")[0])
    
    evoked  = mne.read_evokeds(glob.glob("*evo.fif")[0])[0]
    
    #plot power spectral density (computed for evoked - average of all conditions): 
    psd = read_spectrum(config.psd_path)

    report.add_figure(psd.plot(), title=config.get_report_titles()['psd'], section=config.get_report_sections(subject_num=subject_num)['psd'], replace=True)

    #plot csds (computed for epochs_combined[condition]):
    for condition in list(epochs_combined.event_id.keys())+ ['baseline']:    
        csd = read_csd(config.get_csd_path(condition))

        csd_mean = read_csd(config.get_csd_mean_path(condition))

        # for csd per frequency
        report.add_figure(csd.plot(show=False), title= config.get_report_titles(condition=condition)['csd'], section=config.get_report_sections(subject_num=subject_num)['csd'], replace=True)

        # for csd mean over frequency bands
        report.add_figure(csd_mean.plot(show=False), title= config.get_report_titles(condition=condition)['csd_mean'], section=config.get_report_sections(subject_num=subject_num)['csd'], replace=True)

        # in coherence mode
        report.add_figure(csd_mean.plot(mode='coh', show=False), title= config.get_report_titles(condition=condition)['coherence'], section=config.get_report_sections(subject_num=subject_num)['coherence'], replace=True)

        plt.close('all')

    #plot global field power for evoked instance (for all conditions):
    report.add_figure(evoked.plot_image(titles=f"Global Field Power for a single subject", show=False),title=config.get_report_titles()['gfp'], 
    section=config.get_report_sections(subject_num=subject_num)['gfp'], replace=True)
    plt.close('all')

   #plot tfr contrast computed per contrast (evoked[condition_1] - evoked[condition_2]):
    for file in glob.glob("*tfr*.h5"):
        
        tfr_contrast = read_tfrs(file)
        contrast = file.split('evoked_tfr_')[1].split('.h5')[0] # get the name of the contrast for the specific tfr computed

        # plot the tfr contrast for all frequencies in the tfr computation
        report.add_figure(tfr_contrast.plot(combine='mean', baseline=config.baseline_time, title=f"Contrast ({contrast})"),
        title= config.get_report_titles(contrast=contrast)['tfr_contrast'], section=config.get_report_sections(subject_num=subject_num)['tfr_contrast'], replace=True)
        plt.close('all')

        freqs = tfr_contrast.freqs #extract the frequencies the tfr was computed for

        freq_bands = np.arange(freqs[0], freqs[-1]+1, 4) # create an np.ndarry of the frequency ranges we'd like to see the topo-plot for

        
        #plot topo-plots of tfr specific contrast per time range and frequency band:
        for time_range in config.time_frames:

            for i,freq in enumerate(freq_bands):
                
                # if reached to last frequency in numpy array -> no more fmin-fmax pairs to go over 
                if i == len(freq_bands)-1:
                    break

                fmin, fmax = freq, freq_bands[i+1] # the frequency range to plot topo-plot

                tmin, tmax = time_range[0], time_range[1] # the time range for tipo-plot plotting

                print(f"Creating a topoplot for the parameters: contrat - {contrast}, frequency range - {fmin}-{fmax}, \n time range - {tmin}-{tmax}")

                #plotting topo plot
                report.add_figure(tfr_contrast.plot_topomap(size=8, mode='mean', fmin=fmin, fmax=fmax, tmin=tmin, tmax=tmax, baseline=config.baseline_time), 
                title=config.get_report_titles(contrast=contrast, fmin=fmin, fmax=fmax, tmin=tmin, tmax=tmax)['tfr_contrast_topoplots'], section=config.get_report_sections(subject_num=subject_num)['tfr_contrast_topoplots'], replace=True)
                plt.close('all')

