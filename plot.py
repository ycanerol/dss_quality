import sys

import matplotlib as mpl
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

import folder_selector

mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

def load_data(maindir):
    maindir = Path(maindir)
    df = pd.read_csv(maindir / 'dss_plot' / 'dss_quality_data.csv')
    # Default sort is filename, but 9999 might be exceeded during acquisition
    # so explicitly set the sorting to date
    df.sort_values('datetime', inplace=True)
    return df


def rolling_mean(df, window):
    return df.rolling(window).mean()


def plot_quality(df):
    fig = plt.plot(df.datetime, rolling_mean(df, 10).quality)
    plt.xticks([])
    plt.show()
    return fig


def plot_panels(df, maindir):
    rolling = rolling_mean(df, 10)
    fig, axes = plt.subplots(3, 1, sharex=True)
    axes[0].plot(df.datetime, rolling.quality)
    axes[0].set_ylabel('Quality')
    axes[1].plot(df.datetime, rolling.nstars)
    axes[1].set_ylabel('#Stars')
    axes[2].plot(df.datetime, rolling.background*100) # Usually presented as percentage
    axes[2].set_ylabel('Sky background %')
    for ax in axes:
        ax.set_xticks([])
    axes[-1].set_xticks(df.datetime[::100], rotation=90)
    plt.setp(axes[-1].get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")
    fig.savefig(Path(maindir)/'dss_plot'/'dss_plot.jpg')
    plt.show()

def dataframe_series(df, column_name):
    series = pd.Series(df.datetime, df[column_name])
    return series


if __name__ == '__main__':
    # maindir = Path('/Volumes/Transcend/astrophotography/2021-12-09_cygnus_loop/')
    if len(sys.argv) == 2:
        selected_folder = sys.argv[1]
    else:
        selected_folder = folder_selector.folder_selector()
    df = load_data(selected_folder)
    plot_panels(df, selected_folder)


