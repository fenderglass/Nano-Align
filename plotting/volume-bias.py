#!/usr/bin/env python2.7

#(c) 2015-2016 by Authors
#This file is a part of Nano-Align program.
#Released under the BSD license (see LICENSE file)

"""
Measure volume- and hydro-related bias
for SVR and MV models
"""

from __future__ import print_function
import sys
import os
import argparse
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from scipy.stats import linregress

nanoalign_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, nanoalign_root)
import nanoalign.signal_proc as sp
from nanoalign.blockade import read_mat
from nanoalign.model_loader import load_model


def get_bias(blockades_file, model_file, cluster_size):
    """
    Gets AA-specific bias between the empirical and theoretical signals
    """
    WINDOW = 4

    blockades = read_mat(blockades_file)
    clusters = sp.preprocess_blockades(blockades, cluster_size=cluster_size,
                                       min_dwell=0.5, max_dwell=20)
    peptide = clusters[0].blockades[0].peptide

    blockade_model = load_model(model_file)

    errors = defaultdict(list)
    model_signal = blockade_model.peptide_signal(peptide)
    for cluster in clusters:
        discr_signal = sp.discretize(cluster.consensus, len(peptide))

        flanked_peptide = ("-" * (WINDOW - 1) + peptide +
                           "-" * (WINDOW - 1))
        num_peaks = len(peptide) + WINDOW - 1

        for i in xrange(0, num_peaks):
            kmer = flanked_peptide[i : i + WINDOW]
            if "-" not in kmer:
                for aa in kmer:
                    errors[aa].append(discr_signal[i] - model_signal[i])

    return errors


def fancy_plot(errors, plot_type):
    """
    Draws the plot
    """
    VOLUMES = {"I": 169, "F": 203, "V": 142, "L": 168,
               "W": 238, "M": 171, "A": 92, "G": 66,
               "C": 106, "Y": 204, "P": 129, "T": 122,
               "S": 99, "H": 167, "E": 155, "N": 135,
               "Q": 161, "D": 124, "K": 171, "R": 202}

    #hydrophilicity indices from Janin, 1979
    HYDRO =   {"I": 3.1, "F": 2.2, "V": 2.9, "L": 2.4,
               "W": 1.6, "M": 1.9, "A": 1.7, "G": 1.8,
               "C": 4.6, "Y": 0.5, "P": 0.6, "T": 0.7,
               "S": 0.8, "H": 0.8, "E": 0.3, "N": 0.4,
               "Q": 0.3, "D": 0.4, "K": 0.05, "R": 0.1}

    if plot_type == "volume":
        sorted_aa = sorted(errors.keys(), key=VOLUMES.get)
    else:
        sorted_aa = sorted(errors.keys(), key=HYDRO.get)
    sorted_values = map(errors.get, sorted_aa)

    x_axis = range(1, len(sorted_aa) + 1)
    medians = map(lambda x: np.median(x), sorted_values)
    print("P-value:", linregress(x_axis, medians)[3])
    poly = np.polyfit(x_axis, medians, 1)
    poly_fun = np.poly1d(poly)

    matplotlib.rcParams.update({"font.size": 16})
    fig = plt.subplot()
    bp = fig.boxplot(sorted_values, sym="", notch=True)
    fig.set_xticklabels(sorted_aa)

    fig.spines["right"].set_visible(False)
    fig.spines["top"].set_visible(False)
    fig.get_xaxis().tick_bottom()
    fig.get_yaxis().tick_left()
    fig.set_ylim(-2, 2)

    for y in [-1, 0, 1]:
        fig.plot([y] * 20, "--",
                 lw=0.5, color="black", alpha=0.3)

    for box in bp["boxes"]:
        box.set(color="#7570b3", linewidth=2)
    for whisker in bp["whiskers"]:
        whisker.set(color="white", linewidth=2)
    for cap in bp["caps"]:
        cap.set(color="white", linewidth=2)
    for median in bp["medians"]:
        median.set(color="red", linewidth=2)

    fig.plot(x_axis, poly_fun(x_axis), "r-", linewidth=1.5)

    if plot_type == "volume":
        fig.set_xlabel("Amino acids (sorted by volume)")
    else:
        fig.set_xlabel("Amino acids (sorted by hydrophillicity)")
    fig.set_ylabel("Signed error")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Compute volume- and"
                                     "hydro-related bias", formatter_class= \
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("nanospectra_file", metavar="nanospectra_file",
                        help="path to nanospectra file (in mat format)")
    parser.add_argument("model_file", metavar="model_file",
                        help="path to trained blockade model file "
                        "('-' for mean volume model)")
    parser.add_argument("-c", "--cluster-size", dest="cluster_size", type=int,
                        default=10, help="blockades cluster size")
    parser.add_argument("--hydro", action="store_true",
                        default=False, dest="hydro",
                        help="Order AA by hydrophilicity instead of volume")
    args = parser.parse_args()

    errors = get_bias(args.nanospectra_file, args.model_file, args.cluster_size)
    mode = "volume" if not args.hydro else "hydro"
    fancy_plot(errors, mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
