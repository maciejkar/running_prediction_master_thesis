# Running Performance Prediction

This project focuses on predicting running performance using machine learning techniques, specifically analyzing data from the French Athletics Federation (FFA) database.

## Project Structure

```
├── data/                      # Data directory
│   ├── README.md             # Data documentation
│   ├── halfmarathon_dataset.csv    # Processed half marathon data
│   ├── marathon_dataset.csv        # Processed marathon data
│   ├── raw_master_ffa_results.csv  # Raw FFA results (not in repo)
│   └── athlets.csv           # Athlete information (not in repo)
├── models/                   # Trained models (see below for exclusions)
│   ├── README.md             # Model documentation
│   └── best_pipeline/        # Best performing models for each algorithm
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

## Model Files and Exclusions

The `models/` directory contains trained machine learning models. **Large model files** (such as RandomForest models, which can exceed 50MB) are **excluded from the repository** due to GitHub's file size limitations. Only smaller models (e.g., Linear Regression, Ridge, Lasso, SVR, etc.) are included.

If you need the excluded models, you can retrain them using the provided scripts and notebooks. See `models/README.md` for more details on the available models and how to use or retrain them.

## Setup

1. Clone the repository:
```