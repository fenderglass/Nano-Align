#(c) 2015-2016 by Authors
#This file is a part of Nano-Align program.
#Released under the BSD license (see LICENSE file)

from __future__ import print_function
from string import maketrans
import os
import pickle
import random
from itertools import chain

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import f_regression


class RandomForestBlockade(object):
    def __init__(self):
        self.predictor = None
        self.window = 4
        self.rf_cache = {}

        self.volumes = {"I": 1688, "F": 2034, "V": 1417, "L": 1679,
                        "W": 2376, "M": 1708, "A": 915, "G": 664,
                        "C": 1056, "Y": 2036, "P": 1293, "T": 1221,
                        "S": 991, "H": 1673, "E": 1551, "N": 1352,
                        "Q": 1611, "D": 1245, "K": 1713, "R": 2021,
                        "X": 1500, "U": 1056, "Z": 1580, "B": 1300}

        self.hydro =   {"I": 450, "F": 280, "V": 420, "L": 380,
                        "W": -90, "M": 190, "A": 180, "G": -40,
                        "C": 250, "Y": -130, "P": -160, "T": -70,
                        "S": -80, "H": -320, "E": -350, "N": -350,
                        "Q": -350, "D": -350, "K": -390, "R": -450,
                        "X": 0, "U": 250, "Z": -350, "B": -350}

    def load_from_pickle(self, filename):
        """
        Loads serialized SVR
        """
        self.predictor = pickle.load(open(filename, "rb"))

    def store_pickle(self, filename):
        """
        Serizlize into file
        """
        assert self.predictor is not None
        pickle.dump(self.predictor, open(filename, "wb"))

    def train(self, peptides, signals):
        features = map(lambda p: self._peptide_to_features(p, shuffle=True),
                       peptides)
        train_features = np.array(sum(features, []))

        #regulzrisation
        noise_features = []
        for data in train_features:
            noise_features.append(map(lambda f: f + random.gauss(0, 10), data))

        train_signals = np.array(sum(signals, []))
        assert len(train_features) == len(train_signals)

        self.predictor = RandomForestRegressor(n_estimators=10)
        self.predictor.fit(noise_features, train_signals)

        #print(f_regression(noise_features, train_signals))
        print(self.predictor.feature_importances_)
        print(self.predictor.score(noise_features, train_signals))

    def _rf_predict(self, feature_vec):
        """
        Predicts signal for a feature vector
        """
        if feature_vec not in self.rf_cache:
            np_feature = np.array(feature_vec).reshape(1, -1)
            self.rf_cache[feature_vec] = self.predictor.predict(np_feature)[0]
        return self.rf_cache[feature_vec]

    def peptide_signal(self, peptide):
        """
        Generates theoretical signal of a given peptide
        """
        assert self.predictor is not None

        features = self._peptide_to_features(peptide, shuffle=False)
        signal = np.array(map(lambda x: self._rf_predict(x), features))
        #signal = signal / np.std(signal)
        return signal

    def _peptide_to_features(self, peptide, shuffle):
        volumes = map(self.volumes.get, peptide)
        #hydro = map(self.hydro.get, peptide)
        num_peaks = len(volumes) + self.window - 1
        flanked_volumes = ([0] * (self.window - 1) + volumes +
                           [0] * (self.window - 1))
        #flanked_hydro = ([0] * (self.window - 1) + hydro +
        #                 [0] * (self.window - 1))

        features = []
        for i in xrange(0, num_peaks):
            v = flanked_volumes[i : i + self.window]
            if shuffle:
                random.shuffle(v)
            features.append(tuple(v))

            #h = flanked_hydro[i : i + self.window]
            #combined = zip(v, h)
            #random.shuffle(combined)
            #features.append(tuple(list(chain(*combined))))

        return features
