#!/usr/bin/env python

# Built-in packages
import logging
import argparse
from argparse import RawDescriptionHelpFormatter

# Add-on packages
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3


# Local Packages
from interface import wideToDesign
import logger as sl


def getOptions():
    """ Function to pull in arguments """
    description = """ Distribution Analysis: Plot sample distrubtions. """
    parser = argparse.ArgumentParser(description=description, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("--input", dest="fname", action='store', required=True, help="Input dataset in wide format.")
    parser.add_argument("--design", dest="dname", action='store', required=True, help="Design file.")
    parser.add_argument("--ID", dest="uniqID", action='store', required=True, help="Name of the column with unique identifiers.")
    parser.add_argument("--group", dest="group", action='store', required=False, help="Name of column in design file with Group/treatment information.")
    parser.add_argument("--fig", dest="ofig", action='store', required=True, help="Output figure name [pdf].")
    parser.add_argument("--fig2", dest="ofig2", action='store', required=True, help="Output figure name [html].")
    parser.add_argument("--debug", dest="debug", action='store_true', required=False, help="Add debugging log output.")
    args = parser.parse_args()
#     args = parser.parse_args(['--input', '/home/jfear/sandbox/secim/data/ST000015_AN000032_v2.tsv',
#                               '--design', '/home/jfear/sandbox/secim/data/ST000015_design_v2.tsv',
#                               '--ID', 'Name',
#                               '--group', 'treatment',
#                               '--fig', '/home/jfear/sandbox/secim/data/test.pdf',
#                               '--fig2', '/home/jfear/sandbox/secim/data/test2.html',
#                               '--debug'])
    return(args)


def adjXCoord(ax):
    """ Adjust xlim on plots with no negative number.

    KDE of 0's can results in negative values, when data has no negative values
    then change xaxis to start at 0.

    """
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(0, xmax)


def pltByTrt(dat, ax):
    """ Color Lines by Group

    If group information is provided, then color distribution lines by group.

    """
    colors = pd.tools.plotting._get_standard_colors(len(dat.group))
    colLines = list()
    for i, grp in enumerate(dat.levels):
        samples = dat.design[dat.design[dat.group] == grp].index
        samp = dat.wide[samples]
        samp.plot(kind='kde', title='Distribution by Sample', ax=ax, c=colors[i])

        # Adjust coordinates if no negative values
        min = samp.values.min()
        if min >= 0:
            adjXCoord(ax)

        colLines.append(matplotlib.lines.Line2D([], [], c=colors[i], label=grp))

    return plt.legend(colLines, dat.levels, loc='upper left')


def pltBySample(dat, ax):
    """ Color Lines by Group

    If no group information then color distribution lines by sample.

    """
    samp = dat.wide[dat.sampleIDs]
    samp.plot(kind='kde', title='Distribution by Sample', ax=ax)

    # Adjust coordinates if no negative values
    min = samp.values.min()
    if min >= 0:
        adjXCoord(ax)


def main(args):
    # Import data
    logger.info(u'Importing data with following parameters: \n\tWide: {0}\n\tDesign: {1}\n\tUnique ID: {2}\n\tGroup Column: {3}'.format(args.fname, args.dname, args.uniqID, args.group))
    dat = wideToDesign(args.fname, args.dname, args.uniqID, args.group)
    dat.wide.convert_objects(convert_numeric=True)

    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)

    # If there is group information, color by group.
    if hasattr(dat, 'group'):
        logger.info('Plotting sample distributions by group')
        legend1 = pltByTrt(dat, ax)
    else:
        logger.info('Plotting sample distributions')
        pltBySample(dat, ax)

    # Create Legend
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles, labels, ncol=5, loc='upper right', fontsize=10)

    # Create second legend if there is group information
    if hasattr(dat, 'group'):
        ax.add_artist(legend1)

    plt.savefig(args.ofig, format='pdf')
    mpld3.save_html(fig, args.ofig2)


if __name__ == '__main__':
    # Command line options
    args = getOptions()

    logger = logging.getLogger()
    if args.debug:
        sl.setLogger(logger, logLevel='debug')
    else:
        sl.setLogger(logger)

    main(args)
