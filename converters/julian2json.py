#!/usr/bin/env python3
"""Converter from Julian's npy files to JSON file for Athena

At the moment we assume that numpy files are named `{b,w}_l_X.npy`.
"""

import argparse, glob
import json
import numpy as np

def _run():
    """Top level routine"""
    args = _get_args()

    globstr = "w_l_*.npy"
    layers = {}
    for fname in glob.glob(globstr):
        number = int(fname[-5])
        weight = np.load(fname)
        bias = np.load('b' + fname[1:])
        layers[number] = (weight, bias)
    for num, (wt, bias) in layers.items():
        print(bias.shape)
    out_dict = {
        'layers': _get_layers(layers),
        'inputs': _get_inputs(layers),
        'outputs': _get_outputs(layers)
        }
    defaults = network.get('defaults')
    if defaults:
        out_dict['defaults'] = defaults
    print(json.dumps(out_dict))

def _get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('network_dir')
    return parser.parse_args()

def _get_layers(layers):
    last_layer = len(layers) - 1
    layers = []
    n_out = layers[0][0].shape[0]
    for number, (wt, bias) in layers.items():
        assert wt.shape[1] == bias.shape[0]
        assert wt.shape[0] == n_out
        n_out = wt.shape[1]
        out_layer = {
            'activation': 'linear' if number == last_layer else 'sigmoid'
            'weights': wt.flatten('F')
            'bias': bias.flatten('F')
        }
        layers.append(out_layer)
    return layers

def _get_inputs(layers):
    """
    The inputs from julian are (currently) hardcoded
    """
    inputs = ['pt', 'eta'] + [
        'track_2_d0_significance',
        'track_3_d0_significance',
        'track_2_z0_significance',
        'track_3_z0_significance',
        'n_tracks_over_d0_threshold',
        'jet_prob',
        'jet_width_eta',
        'jet_width_phi'] + [
            'vertex_significance', 'n_secondary_vertices',
            'n_secondary_vertex_tracks', 'delta_r_vertex',
            'vertex_mass', 'vertex_energy_fraction']
    assert len(inputs) == layers[0][0].shape[0]
    for input_name in inputs:
        offset = 0
        scale = 1
        inputs.append({'name': input_name, 'offset': 0, 'scale': 1})
    return inputs

def _get_outputs(layers):
    assert layers[-1][0].shape[1] == 1
    return ['discriminant']

if __name__ == '__main__':
    _run()
