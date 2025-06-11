# Data Directory

This directory contains the datasets used in the running prediction project.

## Available Datasets

### Processed Datasets
- `halfmarathon_dataset.csv`: Processed dataset for half marathon predictions
- `marathon_dataset.csv`: Processed dataset for marathon predictions

### Raw Data (Not included in repository)
The following raw data files are not included in the repository due to their size:
- `raw_master_ffa_results.csv` (432MB)
- `raw_master_ffa_results_part1.csv` (197MB)
- `raw_master_ffa_results_part2.csv` (86MB)
- `raw_master_ffa_results_part3.csv` (149MB)
- `athlets.csv` (6.8MB)

## Data Collection

The raw data was collected from the French Athletics Federation (FFA) website using the web scraping scripts:
- `ffa_scraper.py`
- `scrap_data.py`
- `extract_athlets_results.ipynb`

## Data Processing

The raw data was processed using:
- `transform_data.ipynb`: Data transformation and preprocessing
- `main_part.ipynb`: Main analysis and feature engineering

## How to Obtain Raw Data

To obtain the raw data:
1. Run the scraping scripts in the following order:
   - `ffa_scraper.py`
   - `scrap_data.py`
   - `extract_athlets_results.ipynb`
2. The scripts will create the necessary raw data files in this directory

Note: The scraping process may take several hours due to the large amount of data and rate limiting on the FFA website.