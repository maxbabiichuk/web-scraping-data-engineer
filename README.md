# Data Engineer Test Task

This project collects data from Facebook ads using the web scraping (“microlearning” ads hardcoded). Transform data to Canonical Schema and save it to CSV. Also it's calculate proxy performance score for ads and show top 10 performers


## Installation

Clone the repository and install the dependencies:

```bash
cd your-repo
pip install -r requirements.txt
```

## How to use

Run ETL for data collection. meta_scrapped_ads.csv file will be created
```bash
python meta_ads_etl.py
```

## Briefly explaination of the approach

I didn't have access to Facebook Ads API, thats why I use web scraping approach for data collection. Data tranformed and saved according to Canonical Schema (in schema.yaml file). Data saved to meta_scrapped_ads.csv file