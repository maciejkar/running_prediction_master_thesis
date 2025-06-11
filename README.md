# Running Prediction - Master Thesis Project

This repository contains the code and analysis for my master thesis project focused on running performance prediction using data from the French Athletics Federation (FFA).

## Project Overview

The project aims to analyze and predict running performances using historical data from the French Athletics Federation. The analysis includes data collection, processing, and machine learning models to predict athlete performances.

## Project Structure

```
├── data/                      # Data directory
│   ├── README.md             # Data documentation
│   ├── halfmarathon_dataset.csv    # Processed half marathon data
│   ├── marathon_dataset.csv        # Processed marathon data
│   ├── raw_master_ffa_results.csv  # Raw FFA results (not in repo)
│   └── athlets.csv           # Athlete information (not in repo)
├── models/                    # Trained models
├── figs/                      # Generated figures
├── ffa_scraper.py            # FFA website scraper
├── scrap_data.py             # Data collection script
├── extract_athlets_results.ipynb  # Athlete results extraction
├── transform_data.ipynb      # Data preprocessing
└── main_part.ipynb           # Main analysis notebook
```

### Data Collection and Processing

The project uses data from the French Athletics Federation (FFA) database, collected through web scraping. The data collection process involves:

1. **Data Collection**:
   - `ffa_scraper.py`: Main scraper for FFA website
   - `scrap_data.py`: Script to collect athlete information
   - `extract_athlets_results.ipynb`: Extracts detailed results for each athlete

2. **Data Processing**:
   - `transform_data.ipynb`: Processes raw data into structured datasets
   - Creates two main datasets:
     - `halfmarathon_dataset.csv`: Processed half marathon data
     - `marathon_dataset.csv`: Processed marathon data

3. **Data Structure**:
   The processed datasets include:
   - Athlete information (age, gender, physical characteristics)
   - Historical performance data
   - Race conditions and locations
   - Performance metrics

Note: Raw data files are not included in the repository due to their size. See `data/README.md` for details on how to obtain and process the raw data.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/maciejkar/running_prediction_master_thesis.git
cd running_prediction_master_thesis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Collection

The project uses web scraping to collect athlete data from the French Athletics Federation website. The data collection process is implemented in `ffa_scraper.py` and `scrap_data.py`.

### Data Structure
The collected data includes:
- Athlete information (name, date of birth, sex, weight, height)
- Event details (date, name, tour, location)
- Performance metrics

## Analysis

The analysis is conducted in Jupyter notebooks:
- `transform_data.ipynb`: Data preprocessing and feature engineering
- `main_part.ipynb`: Main analysis including model training and evaluation

## Requirements

The project requires Python 3.12.6 and the following main dependencies (see requirements.txt for complete list):
- pandas
- numpy
- requests
- beautifulsoup4
- jupyter
- scikit-learn
- matplotlib
- seaborn

## Usage

1. Data Collection:
   - Run the scraping scripts to collect athlete data
   - Process the raw data using the provided notebooks

2. Analysis:
   - Follow the notebooks in sequence:
     1. `transform_data.ipynb` for data preprocessing
     2. `main_part.ipynb` for the main analysis

## License

[Add your chosen license here]

## Author

Maciej Karczewski