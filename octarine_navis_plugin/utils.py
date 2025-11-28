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

import numpy as np

def is_navis(x):
    """Check if an object is a navis object."""
    if not hasattr(x, "__class__"):
        return False
    # Check if any of the parent classes is a navis object
    for b in x.__class__.__mro__:
        if b.__module__.startswith("navis"):
            return True
    return False


def is_neuron(x):
    """Check if an object is a navis neuron."""
    if not is_navis(x):
        return False
    # Check if any of the parent classes is a navis neuron
    for b in x.__class__.__mro__:
        if b.__name__.endswith("Neuron"):
            return True
    return False


def is_neuronlist(x):
    """Check if an object is a navis.NeuronList."""
    if not is_navis(x):
        return False
    # Check if any of the parent classes is a navis neuronlist
    for b in x.__class__.__mro__:
        if b.__name__ == "NeuronList":
            return True
    return False


def is_skeletor(x):
    """Check if an object is a skeletor.Skeleton."""
    if not hasattr(x, "__class__"):
        return False
    # Check if any of the parent classes is a skeletor Skeleton
    for b in x.__class__.__mro__:
        if b.__module__.startswith("skeletor") and b.__name__ == "Skeleton":
            return True
    return False

def set_alpha(color, alpha):
    """Set alpha channel for given color.

    Will add alpha channel if not present.

    Parameters
    ----------
    color : array-like, shape (..., 3) or (..., 4)
            RGB or RGBA color values in range [0, 1].
    alpha : float
            Alpha value to set, in range [0, 1].

    """
    if isinstance(color, np.ndarray):
        color = color.copy()
        if color.ndim == 2:
            if color.shape[1] == 3:
                alpha_channel = np.full((color.shape[0], 1), alpha)
                color = np.hstack((color, alpha_channel))
            elif color.shape[1] == 4:
                color[:, 3] = alpha
            else:
                raise ValueError("Color array must have shape (..., 3) or (..., 4).")
        elif color.ndim == 1:
            if color.shape[0] == 3:
                color = np.append(color, alpha)
            elif color.shape[0] == 4:
                color[3] = alpha
            else:
                raise ValueError("Color array must have shape (..., 3) or (..., 4).")
        else:
            raise ValueError("Color array must have shape (..., 3) or (..., 4).")
    elif isinstance(color, list):
        color = color.copy()
        if len(color) == 3:
            color.append(alpha)
        elif len(color) == 4:
            color[3] = alpha
        else:
            raise ValueError("Color list must have length 3 or 4.")
    elif isinstance(color, tuple):
        if len(color) == 3:
            color = list(color) + [alpha]
        elif len(color) == 4:
            color = list(color)
            color[3] = alpha
        else:
            raise ValueError("Color tuple must have length 3 or 4.")
        color = tuple(color)
    else:
        raise TypeError("Color must be a numpy array, list, or tuple.")

    return color