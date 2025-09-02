import sys

import extractdata
import transformdata
import savedata

LOCALE_KEY = "page_language"
HTML_KEY = "html_content"
csv_file = "meta_scrapped_ads.csv"


def main() -> None:
    extracted_data = extractdata.get_grid_html()
    transformed_data = transformdata.get_canonical_data(
        extracted_data[HTML_KEY], extracted_data[LOCALE_KEY]
    )
    savedata.save_to_csv(transformed_data, csv_file)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"ETL error: {e}")
        sys.exit(1)
