# Stage-in to STAC

This utility takes a YAML file with catalog URL entries, resolves the enclosure and stages the associated EO data.

The EO data is staged to one (or more) folder(s) and the STAC catalog.json file(s) is (are) in the same folder(s)

## Try me on Binder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gl/ellip%2Fincubator%2Fstage-in/master?urlpath=lab)

## Installation

Create a conda environment with Python 3 and the dependencies:

```bash
pyyaml
pystac
shapely
click
cioppy
geopandas
```

Then within that environment, run

```bash
python setup.py install
```

## Getting started


```bash
stage-in -t /new_disk/data/staged/ -c stagein.yaml
```

```
* <Catalog id=catid>
    * <Collection id=collection1>
      * <EOItem id=S2A_MSIL2A_20191216T004701_N0213_R102_T53HPA_20191216T024808>
      * <EOItem id=S2B_MSIL2A_20200130T004659_N0213_R102_T53HPA_20200130T022348>
    * <Collection id=collection2>
      * <EOItem id=S1B_IW_SLC__1SDV_20200122T050405_20200122T050432_019925_025B0B_7EEB>
      * <EOItem id=S1B_IW_SLC__1SDV_20200203T050405_20200203T050432_020100_0260B2_59CC>
/new_disk/data/staged/catalog.json
```


## Limitations

The number of missions supported is growing.

- Sentinel-2 Level-1C, Level-2A
- Sentinel-1 GRD, SLC
- Sentinel-3 WIP

New missions can be added with a dedicated module with a class that implements a `row_to_item(self, row)` method and has `bands` and `properties`

