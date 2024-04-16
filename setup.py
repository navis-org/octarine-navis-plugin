import re

from setuptools import setup, find_packages
from extreqs import parse_requirement_files
from pathlib import Path

VERSIONFILE = "octarine_navis_plugin/__version__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

HERE = Path(__file__).resolve().parent
install_requires, extras_require = parse_requirement_files(
    HERE / "requirements.txt",
)


setup(
    name="octarine-navis-plugin",
    version=verstr,
    packages=find_packages(),
    license="GPLv3",
    description="Octarine plugin to visualize NAVis data in 3D.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/navis-org/octarine-navis-plugin",
    project_urls={
        "Documentation": "https://github.com/navis-org/octarine-navis-plugin",
        "Source": "https://github.com/navis-org/octarine-navis-plugin",
        "Changelog": "https://github.com/navis-org/octarine-navis-plugin/releases",
    },
    author="Philipp Schlegel",
    author_email="pms70@cam.ac.uk",
    keywords="octarine navis 3D visualization",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=install_requires,
    extras_require=dict(extras_require),
    python_requires=">=3.8",
    zip_safe=False,
    include_package_data=True,
    entry_points={
        "octarine.plugins": [
            "octarine_navis_plugin = octarine_navis_plugin:register_plugin",
        ]
    },
)
