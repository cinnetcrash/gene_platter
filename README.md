# Gene Platter

**Interactive Temporal Visualization of Accessory and Core Genes**

---

## Description

Gene Platter is a lightweight, Python-based application for visualizing the yearly distribution of accessory or core genes across microbial genomic datasets.  
It allows users to interactively select one or multiple genes and view their temporal dynamics through time-series plots.  
The application supports exporting high-quality PNG graphs and ensures strict input/output file handling via command-line arguments.

---

## Features

- Parse `.tab` formatted accessory/core gene files automatically.
- Multi-gene selection and dynamic line plots.
- Download plots as PNG with a single click.
- Strict input file and output folder validation.
- Clean and user-friendly command-line interface (CLI).

---

## Requirements

- Python 3.7+
- Python libraries:
  ```bash
  pip install dash plotly pandas


