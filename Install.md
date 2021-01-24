# Step by step intall guide

Install lofar-sun-tool from scratch.

## Install conda

(see anaconda.org)

## Create virtual enviroment

We recommend creating a standalone python enviroment for a more isolated and stable runtime.

```bash
conda create -n lofarsun python=3.7.5
```

Then activate the enviroment:

```bash
conda activate lofarsun
```

## Install dependencies

```bash
conda install -c conda-forge sunpy==2.0.6 matplotlib jupyterlab
```

note : pip higher priority than conda
