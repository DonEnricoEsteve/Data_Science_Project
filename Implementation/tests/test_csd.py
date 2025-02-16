# compares the csds created for a sample subject in the replication part with newly created csds for the same subject using 
# the implementation functionL compute_csd in the analyses.compute_csd module

try:
    # importations
    import mne, os, sys, glob
    from mne.time_frequency import read_csd, pick_channels_csd
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import numpy as np
    import traceback

    # change package_path according to the project's directory on your machine
    package_path = "C:/Projects/food_meg_analyses"

    # setting package path in system path for internal module importations
    if os.path.exists(package_path):
        if package_path not in sys.path:
            sys.path.insert(0, package_path)
    else:
        raise FileNotFoundError(f"The path {package_path} doesn't exist")


    from src import config
    from analyses.compute_csd import compute_csd


    def prepare_subplot(fig):
        """
        Recieves: a matplotlib figure

        Function: 
            * turns the figure into an image that can be plotted in a subplot
            * appends the images into a list


        Returns: None
        """
        global images
        canvas = FigureCanvasAgg(fig)
        canvas.draw ()
        img = np.asarray(canvas.buffer_rgba())
        images.append(img)

    # set an empty images list which later we'll append to:
    images = []

    # replication parameters:
    freq_bands = [
        (3, 7),  # theta
        (7, 13),  # alpha
        (13, 17),  # low beta
        (17, 25),  # high beta 1
        (25, 31),  # high beta 2
        (31, 40),  # low gamma
    ]
    baseline_time = (-0.2, 0.0)
    post_stim_time = (0.0, 0.4)
    conditions = ["face", "scrambled"]

    # create a new mne.Report instance
    report = mne.Report(title="CSDs created by Implementation Function VS Replication Results")

    # path to the -epo.fif of the sample_subject
    path_pattern_epo_sample = os.path.join(config.subs_directory, "sample_subject/*epo.fif")
    path_epo_sample = glob.glob(path_pattern_epo_sample)[0]

    # path pattern to the csds of the sample_subject
    path_csds_replication = os.path.join(config.subs_directory, "sample_subject/*csd*")

    # path to save final test report:
    path_report = os.path.join(config.subs_directory, "sample_subject/report.html")

    # read -epo.fif, extract info and create a list of the gradiometers in info
    epochs = mne.read_epochs(path_epo_sample)
    info = epochs.info
    grads = [info["ch_names"][ch] for ch in mne.pick_types(info, meg="grad")]


    for condition in conditions:
        # compute csd per condition (with mean over desired frequency bands) and pick only gradiometers to display
        _, csd_mean = compute_csd(epochs, condition, freq_bands, post_stim_time, save=False)
        csd_mean = pick_channels_csd(csd_mean, grads)
        figures = csd_mean.plot(info=epochs.info, n_cols=3, show=False)
        fig = figures[0] # need the first and only element because mne.CrossSpectralDensity.plot() returns a list of figures
        fig.suptitle(f"Implementation CSD for {condition.capitalize()} Condition")
        prepare_subplot(fig)
        plt.close('all')

    # compute mean csd for baseline
    _, csd_baseline_mean =  compute_csd(epochs, condition, freq_bands, baseline_time, is_baseline=True, save=False)
    csd_baseline_mean = pick_channels_csd(csd_mean, grads)
    figures = csd_baseline_mean.plot(info=epochs.info, n_cols=3, show=False)
    fig = figures[0]
    fig.suptitle("Implementation CSD for Baseline")
    prepare_subplot(fig)
    plt.close('all')

    # read the csd files created in replication part, average across the desired frequency band and prepare the figures to plot in a subplot
    for file in glob.glob(path_csds_replication):
        print(f"processing {file}")
        condition = file.split(f"{config.subs_directory}\\sample_subject\\sub001-")[1].split("-csd")[0]
        csd_replication = read_csd(file)
        csd_mean = csd_replication.mean([f[0] for f in freq_bands], [f[1] for f in freq_bands])
        csd_mean = pick_channels_csd(csd_mean, grads)
        figures = csd_mean.plot(info=epochs.info, n_cols=3, show=False)
        fig = figures[0]
        fig.suptitle(f"Replication CSD for {condition.capitalize()}")
        prepare_subplot(fig)
        plt.close('all')
        
    # itterate over conditions and create a figure for each condition such that top image would be the implementation 
    # and bottom image the replication:
    for i, condition in enumerate(conditions + ["baseline"]):
        fig = plt.figure(figsize=(10,10))
        ax1 = fig.add_subplot(2,1,1)
        ax2 = fig.add_subplot(2,1,2)
        ax1.imshow(images[i])
        ax2.imshow(images[i+3])
        report.add_figure(fig=fig, title=condition.capitalize()) # add the current figure to report

    report.save(path_report)

except Exception as e:
    print("An error occured: ", e)
    traceback.print_exc()
