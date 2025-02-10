import mne
from mne.time_frequency import read_csd, read_spectrum, read_tfrs
import glob
from config import *
import numpy as np


def add_to_report(report: mne.Report, subject_num: str):

    epochs_combined = mne.read_epochs(glob.glob("*combined_epo.fif"))
    evoked  = mne.read_evokeds(glob.glob("*evo.fif"))
    
    #plot psd (computed for evoked): 
    psd = read_spectrum(psd_path)
    report.add_figure(psd.plot(), title=report_titles['psd'], section=report_sections['psd'], replace=True)


    #plot csds (computed for epochs_combined[condition]):
    for condition in [list(epochs_combined.event_id.keys()), 'baseline']:    
        csd = read_csd(csd_path)

        csd_mean = read_csd(csd_mean_path)

        report.add_figure(csd.plot(show=False), title= report_titles['csd'], section=report_sections.csd, replace=True)

        report.add_figure(csd_mean.plot(show=False), title= report_titles['csd_mean'], section=report_sections['csd'], replace=True)

        report.add_figure(csd_mean.plot(mode='coh', show=False), title= report_titles['coherence'], section=report_sections['coherence'], replace=True)



    #plot gfp for evoked:
    report.add_figure(evoked.plot_image(titles=f"Global Field Power for a single subject", show=False),title=report_titles['gfp'], 
    section=report_sections['gfp'], replace=True)


   #plot tfr contrast computed per contrast (evoked[condition_1] - evoked[condition_2]):
    for file in glob.glob("*tfr*.h5"):
            
        tfr_contrast = read_tfrs(file)
        contrast = file.split(['evoked_tfr_','.h5'])[1]

        report.add_figure(tfr_contrast.plot(combine='mean', baseline=baseline_time, title=f"Contrast ({contrast})"),
        title= report_titles['tfr_contrast'], section=report_sections['tfr_contrast'], replace=True)

        freqs = tfr_contrast.freqs
        freq_bands = np.arrange(freqs[0], freqs[-1]+1, 4) # np.ndarray

        #plot topo-plots of tfr specific contrast per time range and frequency band:
        for time_range in time_frames:
            for i,freq in enumerate(freq_bands):
                        
                # if reached to last frequency in numpy array -> no more fmin-fmax pairs to go over 
                if i == len(freq_bands)-1:
                    break

                fmin, fmax = freq, freq_bands[i+1]

                tmin, tmax = time_range[0], time_range[1]

            report.add_figure(tfr_contrast.plot_topomap(size=8, mode='mean', fmin=fmin, fmax=fmax, tmin=tmin, tmax=tmax, baseline=baseline_time), 
            title=report_titles['tfr_contrast_topoplots'], section=report_sections['tfr_contrast_topoplots'], replace=True)
