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

import uuid

import octarine as oc
import pandas as pd
import numpy as np
import pygfx as gfx

from .utils import set_alpha


def volume2gfx(x, **kwargs):
    """Convert a single navis.Volume to a pygfx.Mesh."""
    # Parse the color argument(s)
    if "color" not in kwargs:
        if "c" in kwargs:
            kwargs["color"] = kwargs.pop("c")
        elif getattr(x, "color", None) is not None:
            kwargs["color"] = x.color
        else:
            kwargs["color"] = (0.95, 0.95, 0.95, 0.1)

    # Convert to gfx
    vis = oc.visuals.mesh2gfx(x, **kwargs)

    # Use the volume's name, if present
    vis._object_id = getattr(x, "name", uuid.uuid4())

    return vis


def neuron2gfx(x, color=None, random_ids=False, **kwargs):
    """Convert a Neuron/List to pygfx visuals.

    Parameters
    ----------
    x :               TreeNeuron | MeshNeuron | Dotprops | VoxelNeuron | NeuronList
                      Neuron(s) to plot.
    color :           list | tuple | array | str
                      Color to use for plotting.
    **kwargs
                      Additional arguments to pass to the plotting functions:
                        - alpha: float
                        - connectors: bool
                        - connectors_only: bool
                        - cn_colors: dict
                        - color_by: str
                        - shade_by: str
                        - palette: str
                        - vmin: float
                        - vmax: float
                        - linewidth: float
                        - linestyle: str
                        - cn_layout: dict
                        - radius: bool
                        - center: bool
                        - soma: bool
                        - random_ids: bool



    Returns
    -------
    list
                    Contains pygfx objects for each neuron.

    """
    # Delayed import to avoid long import times for octarine
    import navis
    from navis.plotting.colors import prepare_colormap, vertex_colors

    # Make sure we're operating on a NeuronList
    if isinstance(x, navis.BaseNeuron):
        x = navis.NeuronList(x)
    elif not isinstance(x, navis.NeuronList):
        raise TypeError(f'Unable to process data of type "{type(x)}"')

    # Parse color argument(s) into a colormap
    colors = color if color is not None else kwargs.get("c", kwargs.get("colors", None))
    palette = kwargs.get("palette", None)
    color_by = kwargs.get("color_by", None)
    shade_by = kwargs.get("shade_by", None)

    if not isinstance(color_by, type(None)):
        if not palette:
            raise ValueError(
                'Must provide `palette` (e.g. "viridis") argument '
                "if using `color_by`"
            )

        colormap = vertex_colors(
            x,
            by=color_by,
            alpha=kwargs.get("alpha", 1),
            palette=palette,
            vmin=kwargs.get("vmin", None),
            vmax=kwargs.get("vmax", None),
            na=kwargs.get("na", "raise"),
            color_range=1,
        )
    else:
        colormap, _ = prepare_colormap(
            colors,
            neurons=x,
            palette=palette,
            alpha=kwargs.get("alpha", None),
            color_range=1,
        )

    if not isinstance(shade_by, type(None)):
        alphamap = vertex_colors(
            x,
            by=shade_by,
            use_alpha=True,
            palette="viridis",  # palette is irrelevant here
            vmin=kwargs.get("smin", None),
            vmax=kwargs.get("smax", None),
            na=kwargs.get("na", "raise"),
            color_range=1,
        )

        new_colormap = []
        for c, a in zip(colormap, alphamap):
            if not (isinstance(c, np.ndarray) and c.ndim == 2):
                c = np.tile(c, (a.shape[0], 1))

            if c.shape[1] == 4:
                c[:, 3] = a[:, 3]
            else:
                c = np.insert(c, 3, a[:, 3], axis=1)

            new_colormap.append(c)
        colormap = new_colormap

    # List to fill with pygfx visuals
    visuals = []
    for i, neuron in enumerate(x):
        # Generate random ID -> we need this in case we have duplicate IDs
        if random_ids:
            object_id = uuid.uuid4()
        else:
            object_id = neuron.id  # this may also be a random ID

        if isinstance(neuron, navis.TreeNeuron):
            if kwargs.get("radius", False) == "auto":
                # Number of nodes with radii
                n_radii = (
                    neuron.nodes.get("radius", pd.Series([])).fillna(0) > 0
                ).sum()
                # If less than 30% of nodes have a radius, we will fall back to lines
                if n_radii / neuron.nodes.shape[0] < 0.3:
                    kwargs["radius"] = False

            if kwargs.get("radius", False):
                _neuron = navis.conversion.tree2meshneuron(
                    neuron, warn_missing_radii=False
                )
                _neuron.connectors = neuron.connectors
                neuron = _neuron

                # See if we need to map colors to vertices
                if isinstance(colormap[i], np.ndarray) and colormap[i].ndim == 2:
                    colormap[i] = colormap[i][neuron.vertex_map]

        neuron_color = colormap[i]
        if not kwargs.get("connectors_only", False):
            if isinstance(neuron, navis.TreeNeuron):
                visuals += skeleton2gfx(neuron, neuron_color, object_id, **kwargs)
            elif isinstance(neuron, navis.MeshNeuron):
                visuals += mesh2gfx(neuron, neuron_color, object_id, **kwargs)
            elif isinstance(neuron, navis.Dotprops):
                visuals += dotprop2gfx(neuron, neuron_color, object_id, **kwargs)
            elif isinstance(neuron, navis.VoxelNeuron):
                visuals += voxel2gfx(neuron, neuron_color, object_id, **kwargs)
            else:
                navis.config.logger.warning(f"Skipping neuron of type '{type(neuron)}'")

        if (
            kwargs.get("connectors", False) or kwargs.get("connectors_only", False)
        ) and neuron.has_connectors:
            visuals += connectors2gfx(neuron, neuron_color, object_id, **kwargs)

    return visuals


def connectors2gfx(neuron, neuron_color, object_id, **kwargs):
    """Convert connectors to pygfx visuals."""
    import navis

    cn_lay = navis.config.default_connector_colors.copy()

    if kwargs.get("cn_layout", None):
        cn_lay.update(kwargs.get("cn_layout", {}))

    for k in ("cn_size", "cn_alpha"):
        if kwargs.get(k, None) is not None:
            cn_lay[k.split("_")[1]] = kwargs.get(k)

    which_cn = kwargs.get("connectors", None)
    if isinstance(which_cn, (list, np.ndarray, tuple)):
        connectors = neuron.connectors[neuron.connectors.type.isin(which_cn)]
    elif which_cn == "pre":
        connectors = neuron.presynapses
    elif which_cn == "post":
        connectors = neuron.postsynapses
    elif isinstance(which_cn, str):
        connectors = neuron.connectors[neuron.connectors.type == which_cn]
    else:
        connectors = neuron.connectors

    visuals = []
    cn_colors = kwargs.get("cn_colors", None)
    for j, this_cn in connectors.groupby("type"):
        if kwargs.get("cn_mesh_colors", False) or cn_colors == "neuron":
            color = neuron_color
        elif isinstance(cn_colors, dict):
            color = cn_colors.get(j, cn_lay.get(j, {}).get("color", (0.1, 0.1, 0.1)))
        elif cn_colors:
            color = cn_colors
        else:
            color = cn_lay.get(j, {}).get("color", (0.1, 0.1, 0.1))

        color = navis.plotting.colors.eval_color(color, color_range=1)

        if cn_lay.get("alpha", None) is not None:
            color = set_alpha(color, cn_lay["alpha"])

        pos = (
            this_cn[["x", "y", "z"]]
            .apply(pd.to_numeric)
            .values.astype(np.float32, copy=False)
        )

        mode = cn_lay["display"]
        if mode == "circles" or isinstance(neuron, navis.MeshNeuron):
            con = oc.visuals.points2gfx(pos, color=color, size=cn_lay.get("size", 100))
        elif mode == "lines":
            tn_coords = (
                neuron.nodes.set_index("node_id")
                .loc[this_cn.node_id.values][["x", "y", "z"]]
                .apply(pd.to_numeric)
                .values
            )

            # Zip coordinates and add a row of NaNs to indicate breaks in the
            # segments
            coords = np.hstack(
                (pos, tn_coords, np.full(pos.shape, fill_value=np.nan))
            ).reshape((len(pos) * 3, 3))
            coords = coords.astype(np.float32, copy=False)

            # Create line plot from segments
            con = oc.visuals.lines2gfx(
                coords, linewidth=kwargs.get("linewidth", 1), color=color
            )
        else:
            raise ValueError(f'Unknown connector display mode "{mode}"')

        # Add custom attributes
        con._object_type = "neuron"
        con._neuron_part = "connectors"
        con._neuron_id = neuron.id
        con._name = str(getattr(neuron, "name", neuron.id))
        con._object_id = object_id
        con._object = neuron

        visuals.append(con)
    return visuals


def mesh2gfx(neuron, neuron_color, object_id, **kwargs):
    """Convert mesh (i.e. MeshNeuron) to pygfx visuals."""
    # Skip empty neurons
    if not len(neuron.faces):
        return []

    m = oc.visuals.mesh2gfx(neuron, color=neuron_color)

    # Add custom attributes
    m._object_type = "neuron"
    m._neuron_part = "neurites"
    m._neuron_id = neuron.id
    m._name = str(getattr(neuron, "name", neuron.id))
    m._object_id = object_id
    m._object = neuron
    return [m]


def voxel2gfx(neuron, neuron_color, object_id, **kwargs):
    """Convert voxels (i.e. VoxelNeuron) to pygfx visuals."""
    vols = oc.visuals.volume2gfx(
        neuron.grid,
        color=neuron_color,
        spacing=neuron.units_xyz.magnitude,
        offset=neuron.offset,
    )

    # Add custom attributes
    for vol in vols:
        vol._object_type = "neuron"
        vol._neuron_part = "neurites"
        vol._neuron_id = neuron.id
        vol._name = str(getattr(neuron, "name", neuron.id))
        vol._object_id = object_id
        vol._object = neuron

    return vols


def skeleton2gfx(neuron, neuron_color, object_id, **kwargs):
    """Convert skeleton (i.e. TreeNeuron) into pygfx visuals."""
    import navis

    if neuron.nodes.empty:
        navis.config.logger.warning(f"Skipping TreeNeuron w/o nodes: {neuron.id}")
        return []
    elif neuron.nodes.shape[0] == 1:
        navis.config.logger.warning(f"Skipping single-node TreeNeuron: {neuron.label}")
        return []

    visuals = []
    if not kwargs.get("connectors_only", False):
        neuron_color = np.asarray(neuron_color).astype(np.float32, copy=False)

        # Generate coordinates, breaks in segments are indicated by NaNs
        if neuron_color.ndim == 1:
            coords = navis.plotting.plot_utils.segments_to_coords(neuron)
        else:
            coords, neuron_color = navis.plotting.plot_utils.segments_to_coords(
                neuron, node_colors=neuron_color
            )
            # `neuron_color` is now a list of colors for each segment; we have to flatten it
            # and add `None` to match the breaks
            neuron_color = np.vstack(
                [np.append(t, [[None] * t.shape[1]], axis=0) for t in neuron_color]
            ).astype(np.float32, copy=False)

        coords = np.vstack([np.append(t, [[None] * 3], axis=0) for t in coords])
        coords = coords.astype(np.float32, copy=False)

        # Create line plot from segments
        line = oc.visuals.lines2gfx(
            coords,
            linewidth=kwargs.get("linewidth", kwargs.get("lw", 2)),
            dash_pattern=kwargs.get("linestyle", "-"),
            color=neuron_color,
        )

        # Add custom attributes
        line._object_type = "neuron"
        line._neuron_part = "neurites"
        line._neuron_id = neuron.id
        line._name = str(getattr(neuron, "name", neuron.id))
        line._object = neuron
        line._object_id = object_id

        visuals.append(line)

        # Extract and plot soma
        soma = navis.utils.make_iterable(neuron.soma)
        if kwargs.get("soma", True):
            # If soma detection is messed up we might end up producing
            # hundrets of soma which will freeze the session
            if len(soma) >= 10:
                navis.config.logger.warning(
                    f"Neuron {neuron.id} appears to have {len(soma)}"
                    " somas. That does not look right & we will ignore "
                    "them for plotting."
                )
            else:
                for s in soma:
                    # Skip `None` somas
                    if isinstance(s, type(None)):
                        continue

                    # If we have colors for every vertex, we need to find the
                    # color that corresponds to this root (or it's parent to be
                    # precise)
                    if isinstance(neuron_color, np.ndarray) and neuron_color.ndim > 1:
                        s_ix = np.where(neuron.nodes.node_id == s)[0][0]
                        soma_color = neuron_color[s_ix]
                    else:
                        soma_color = neuron_color

                    n = neuron.nodes.set_index("node_id").loc[s]
                    r = (
                        getattr(n, neuron.soma_radius)
                        if isinstance(neuron.soma_radius, str)
                        else neuron.soma_radius
                    )
                    s = gfx.Mesh(
                        gfx.sphere_geometry(
                            radius=np.float32(r),
                            width_segments=16,
                            height_segments=8,
                        ),
                        gfx.MeshPhongMaterial(color=soma_color),
                    )
                    s.local.y = n.y
                    s.local.x = n.x
                    s.local.z = n.z

                    # Add custom attributes
                    s._object_type = "neuron"
                    s._neuron_part = "soma"
                    s._neuron_id = neuron.id
                    s._name = str(getattr(neuron, "name", neuron.id))
                    s._object = neuron
                    s._object_id = object_id

                    visuals.append(s)

    return visuals


def dotprop2gfx(x, neuron_color, object_id, **kwargs):
    """Convert dotprops(s) to pygfx visuals.

    Parameters
    ----------
    x :             navis.Dotprops | pd.DataFrame
                    Dotprop(s) to plot.

    Returns
    -------
    list
                    Contains pygfx visuals for each dotprop.

    """
    # Skip empty neurons
    if not len(x.points):
        return []

    # Generate TreeNeuron
    scale_vec = kwargs.pop("dps_scale_vec", "auto")
    tn = x.to_skeleton(scale_vec=scale_vec)
    return skeleton2gfx(tn, neuron_color, object_id, **kwargs)


def skeletor2gfx(s, **kwargs):
    """Convert a skeletor skeleton to a neuron2gfx object."""
    import navis

    s = navis.TreeNeuron(s, soma=None, id=getattr(s, "id", uuid.uuid4()))
    return neuron2gfx(s, **kwargs)
