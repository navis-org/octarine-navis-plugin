#    This script is part of the Octarine NAVis plugin
#    (https://github.com/navis-org/octarine-navis-plugin).
#    Copyright (C) 2024 Philipp Schlegel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import octarine as oc

from .objects import neuron2gfx, skeletor2gfx
from .utils import is_neuron, is_neuronlist, is_skeletor


def register_plugin():
    """Register the navis converters with octarine."""
    # Register the neuron2gfx converter
    oc.register_converter(is_neuron, neuron2gfx)
    oc.register_converter(is_neuronlist, neuron2gfx)
    oc.register_converter(is_skeletor, skeletor2gfx)

    # Add a dedicated method to the viewer to add neurons
    oc.Viewer.add_neuron = add_neurons


@oc.viewer.update_viewer(legend=True, bounds=True)
def add_neurons(
    self,
    x,
    color=None,
    alpha=1,
    connectors=False,
    cn_colors=None,
    color_by=None,
    shade_by=None,
    palette=None,
    vmin=None,
    vmax=None,
    linewidth=1,
    synapse_layout=None,
    radius=False,
    center=True,
    clear=False,
):
    """Add NAVis neuron(s) to the viewer.

    Parameters
    ----------
    x :         navis Neuron | NeuronList
                The neuron(s) to add to the viewer.
    color :     single color | list thereof, optional
                Color(s) for the neurons.
    connectors : bool, optional
                Whether to plot connectors.
    cn_colors : dict, optional
                A dictionary mapping connectors to colors.
    radius :    float, optional
                The radius of the skeleton.

    """
    if not is_neuron(x) and not is_neuronlist(x):
        raise ValueError(f"Input must be a navis Neuron/List, got {type(x)}.")

    vis = neuron2gfx(
        x,
        color=color,
        alpha=alpha,
        connectors=connectors,
        cn_colors=cn_colors,
        color_by=color_by,
        shade_by=shade_by,
        palette=palette,
        vmin=vmin,
        vmax=vmax,
        linewidth=linewidth,
        synapse_layout=synapse_layout,
        radius=radius,
    )

    if clear:
        self.clear()

    for v in vis:
        self.scene.add(v)

    if center:
        self.center_camera()
