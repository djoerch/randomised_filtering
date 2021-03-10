import setuptools
import itertools

from glob import glob


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="randomised_filtering",
    version="0.0.1",
    author="Daniel Jorgens",
    author_email="djoerch@gmail.com",
    description="Randomised tractogram filtering.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="github.com/djoerch/randomised_filtering",
    packages=setuptools.find_packages(),
    install_requires=[
        'dipy>=0.16.0',
        'nibabel',
        'numpy',
        'tqdm',
        'pandas'
    ],
    scripts=glob("scripts/*"),
)
