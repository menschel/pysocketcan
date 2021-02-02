import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysocketcan",
    version="0.0.1",
    author="Patrick Menschel",
    author_email="menschel.p@posteo.de",
    description="A simple interface to socketcan",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/menschel/pysocketcan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Beta",
        "Programming Language :: Python :: 3",
        "License :: CC-BY-NC",
        "Operating System :: OS Independent",
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
    keywords='socketcan can'

)
