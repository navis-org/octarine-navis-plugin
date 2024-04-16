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
