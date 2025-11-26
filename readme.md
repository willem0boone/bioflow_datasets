# Bioflow datasets

## About
Visualising the contributions of DTO-Bioflow to the EDITO data lake. 

The data consists of new and existing datasets that are hosted on IPT and flow 
through EMODnet Biology to the DTO. In STAC, it is located in EMODnet 
Biology occurrences collection. It has a parquet asset containing all data.

Using the DASID, the parquet can be filtered to find the DTO-Bioflow datasets.
In ```/sources``` there are list of DASIDS that were used.

## Overview of scripts

### 0. Harvests
These scripts are used to access the data, fitler and export.

| script                  | description |
|-------------------------|-------------|
| 0_harvest_all_meta.py   |             |
| 0_harvest_dasid_4687.py |             |
| 0_harvest_datasets.py   |             |
| 0_search_etn.py         |             |

### 1. Plots

| script                         | description |
|--------------------------------|-------------|
| 1_match_worms.py               |             |
| 1_plot_aphia_pie.py            |             |
| 1_plot_occurrence_heatmap.py   |             |
| 1_plot_occurrence_map.py       |             |
| 1_plot_timeline.py             |             |
| 1_plot_timeline_interactive.py |             |

### 2. More plots
| script                      | description |
|-----------------------------|-------------|
| 2_makegif_occurrence_map.py |             |
| 2_plot_aphia_sunburst.py    |             |


### 3. Dashboard
| script                 | description |
|------------------------|-------------|
| 3_dashboard.py         |             |
| 3_magegif_timelines.py |             |



