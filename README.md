# Octarine NAVis Plugin
This plugin enables [Octarine](https://github.com/schlegelp/octarine)
to visualize [NAVis](https://github.com/navis-org/navis) data such as skeletons, meshes,
volumes, etc.

## Installation

```bash
pip install octarine-navis-plugin -U
```

Note that you will have to install `Octarine` and `NAVis` separately.
This is intentional to keep the dependencies light.


## Usage

The plugin will automatically be loaded alongside `Octarine` and extends the functionality by:

1. Allowing to pass `navis.Neuron/Lists`, `navis.Volumes` and `skeletor.Skeletons` to the generic `Viewer.add()` method.
2. Adding a dedicated `Viewer.add_neurons` method with
   various specialized parameters that shadow the options in `navis.plot3d`.

```python
import navis
import octarine as oc

# Initialize the viewer
v = oc.Viewer()

# Grab some neurons
n = navis.example_neurons(5, kind='mesh')

# Add them to the viewer
v.add(n)

# Alternatively use the specialized method with additional options
navis.strahler_index(n)
v.clear()
v.add_neurons(n, color_by='strahler_index', palette='viridis')
```

![example](_static/example_screenshot.png)