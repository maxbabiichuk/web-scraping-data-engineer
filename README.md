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
Run top_ten_ads.py for getting top 10 ads
```bash
python top_ten_ads.py
```

## Briefly explaination of the approach

I didn't have access to Facebook Ads API, thats why I use web scraping approach for data collection. Data tranformed and saved according to Canonical Schema (in schema.yaml file). Data saved to meta_scrapped_ads.csv file.
Then added proxy performance metrics (see below) and compute total score for every adds. Then I tried to get top 10 different adds, by grouping adds by adviser, message and media type (see list below).

## Proxy performance metrics
| Score                 | Weight     | Description                                                                                   | Formula
| --------------------- | ---------- | --------------------------------------------------------------------------------------------- | -----------
| `ad_age_days`         | 0.3        | One of the strongest signals: it spins for a long time → the ad is “alive” and effective.     | log(1  + ad_age_days)
| `ads_from_same_page`  | 0.25       | Page activity shows that the advertiser is professional and scales campaigns.                 | sqrt(ads_from_same_page)
| `creative_type_score` | 0.2        | Video, image, etc. affect engagement, but are not the key factor.                             | video=2, image=1, both=2.5
| `text_len_score`      | 0.15       | Short texts usually work better, but are less critical.                                       | 1 / (len(text) + 1)
| `language_score`      | 0.1        | It affects indirectly — the correct language for the audience, a small penalty, but important.| English - 1, Other - 0.5 

## Top 10 ads
You can see top 10 ads in the top_ten_ads.csv