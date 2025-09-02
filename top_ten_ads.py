import pandas as pd
from datetime import timedelta
import numpy as np
import yaml
config = yaml.safe_load(open("schema.yaml"))
canonical_schema = config["canonical_schema"]

weights = {
    "ad_age_days_score": 0.3,
    "ads_from_same_page_score": 0.25,
    "creative_type_score": 0.2,
    "text_len_score": 0.15,
    "language_score": 0.1
}

df = pd.read_csv('meta_scrapped_ads.csv')
df['published_date'] = df['published_date'].astype('datetime64[ns]')

tomorrow = pd.Timestamp('today') + timedelta(days=1)
df["ad_age_days_score"] = np.log(1 + (tomorrow - df['published_date']).dt.days)
df["ads_from_same_page_score"] = np.sqrt(df.groupby("advertiser_name")["advertiser_name"].transform("count"))
df["creative_type_score"] = df["media_type"].map({"image-only": 1, "video-only": 2, "both": 2.5}).fillna(0)
df["text_len_score"] = 1/(len(df["ad_creative_body"]) + 1)
df["language_score"] = np.where(df["ad_creative_body_lang"] == 'en', 1, 0.5)
df["total_score"] = sum(df[feature] * weight for feature, weight in weights.items())

df["min_published_date"] = df.groupby(["advertiser_name", "ad_creative_body", "media_type"])["published_date"].transform("min")
df = df[df["published_date"] == df["min_published_date"]].drop(columns="min_published_date")
df = df.groupby(["advertiser_name", "ad_creative_body", "media_type"], as_index=True).first().reset_index()

df_sorted = df.sort_values(by='total_score', ascending=False).reset_index(drop=True)
df_filtered = df_sorted.reindex(columns=[col for col in canonical_schema if col in df.columns])
df_filtered.head(10).to_csv('top_ten_ads.csv', index=False)
print("Top ten ads saved to 'top_ten_ads.csv'")
