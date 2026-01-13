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

import warnings

# Note: the register_plugin function is called by octarine. To avoid
# circular imports, we need this function to (a) come first before
# importing octarine itself and (b) import the necessary functions
# inside the function.
def register_plugin():
    """Register the navis converters with octarine."""
    import octarine as oc

    from .objects import neuron2gfx, skeletor2gfx
    from .utils import is_neuron, is_neuronlist, is_skeletor

    # Register the neuron2gfx converter
    oc.register_converter(is_neuron, neuron2gfx)
    oc.register_converter(is_neuronlist, neuron2gfx)
    oc.register_converter(is_skeletor, skeletor2gfx)

import octarine as oc

from .objects import neuron2gfx, skeletor2gfx
from .utils import is_neuron, is_neuronlist, is_skeletor


@oc.viewer.update_viewer(legend=True, bounds=True)
def add_neurons(
    self,
    x,
    color=None,
    alpha=None,
    color_by=None,
    shade_by=None,
    palette=None,
    vmin=None,
    vmax=None,
    smin=None,
    smax=None,
    norm_global=False,
    connectors=False,
    connectors_only=False,
    cn_colors=None,
    cn_layout=None,
    cn_size=None,
    cn_alpha=None,
    cn_mesh_colors=False,
    random_ids=False,
    linewidth=1,
    linestyle='-',
    radius=False,
    soma=True,
    dps_scale_vec='auto',
    name=None,
    center=True,
    clear=False
):
    """Add NAVis neuron(s) to the viewer.

    Parameters
    ----------
    x :             navis Neuron | NeuronList
                    The neuron(s) to add to the viewer.
    color :         single color | list thereof, optional
                    Color(s) for the neurons.
    alpha :         float, optional
                    Transparency of the neurons. If provided, will
                    override the alpha value of the color.
    color_by :      str, optional
                    Name of a property to use for coloring the neurons.
                    Overwrites the `color` parameter.
                    Use these parameters to adjust the color palette:
                     - palette (str): Name of a color palette to use.
                     - vmin/vmax (float): Min and max values for the scale.
                     - norm_global (bool): Whether to normalize the scale
                       globally across all neurons.
    shade_by :      str, optional
                    Name of a property to use for shading the neurons.
                    Use these parameters to adjust the shading:
                     - smin/smax (float): Min and max values for the scale.
    connectors :    bool, optional
                    Whether to plot connectors. Use these parameters
                    to adjust the way connectors are plotted:
                     - `cn_colors` (dict): A dictionary mapping connector
                       types to colors. E.g. {'pre': 'red', 'post': 'blue'}.
                     - `cn_layout` (dict): Layout of the connectors. See
                       `navis.config.default_connector_colors` for options.
                     - `cn_size` (float): Size of the connectors.
                     - `cn_alpha` (float): Transparency of the connectors.
                     - `cn_mesh_colors` (bool): Whether to color the connectors
                       by the neuron's color.
    connectors_only : bool
                    Whether to plot only the connectors (but not the neuron itself).
    random_ids :    bool
                    Whether to use random UUIDs instead of neuron IDs.
                    This is useful if the neurons you are adding have
                    duplicate IDs.

    For skeletons only

    linewidth :     float, optional
                    Width of the lines.
    linestyle :     str, optional
                    Style of the lines.
    radius :        float, optional
                    For skeletons only: whether to use the skeleton's radius
                    information to plot the neuron as a tube (mesh).
    soma :          bool, optional
                    Whether to plot the soma (if present) as a sphere.

    For dotprops only

    dps_scale_vec : float | "auto"
                    Scale factor for the individual tangent vectors.
                    If "auto" (default), the scale factor is determined
                    automatically.

    General viewer parameters

    name :          str, optional
                    If provided, the neuron(s) will be added to the viewer
                    with this name. Overwrites the neurons' IDs.
    center :        bool, optional
                    Whether to re-center the camera after adding the neuron(s).
    clear :         bool, optional
                    Whether to clear the scene before adding the neuron(s).


    """
    import navis
    import skeletor as sk

    # Add a shortcut for skeletor skeletons
    if isinstance(x, sk.Skeleton):
        x = navis.TreeNeuron(x)

    if is_neuron(x):
        pass
    elif is_neuronlist(x):
        if x.is_degenerated:
            warnings.warn("NeuronList contains duplicate IDs.")
    else:
        raise ValueError(f"Input must be a navis Neuron/List, got {type(x)}.")

    vis = neuron2gfx(
        x,
        color=color,
        alpha=alpha,
        connectors=connectors,
        cn_colors=cn_colors,
        cn_alpha=cn_alpha,
        cn_size=cn_size,
        cn_mesh_colors=cn_mesh_colors,
        color_by=color_by,
        shade_by=shade_by,
        palette=palette,
        vmin=vmin,
        vmax=vmax,
        smin=smin,
        smax=smax,
        linewidth=linewidth,
        cn_layout=cn_layout,
        radius=radius,
        random_ids=random_ids,
        dps_scale_vec=dps_scale_vec,
        soma=soma,
        linestyle=linestyle
    )

    if clear:
        self.clear()

    for v in vis:
        if name:
            v._object_id = name

        self._add_to_scene(v, center=False)

    if center:
        self.center_camera()

# Add a dedicated method to the viewer to add neurons
oc.Viewer.add_neurons = add_neurons