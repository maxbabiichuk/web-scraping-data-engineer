import csv
import yaml

config = yaml.safe_load(open("schema.yaml"))
canonical_schema = config["canonical_schema"]


def save_to_csv(data, csv_file):
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        for row in data:
            # Convert date to format YYYY-MM-DD
            row_to_write = row.copy()
            if row_to_write["published_date"]:
                row_to_write["published_date"] = row_to_write["published_date"].strftime("%Y-%m-%d")

            row_to_write = {}
            for field, dtype in canonical_schema.items():
                value = row.get(field)

                if dtype == "datetime" and value:
                    row_to_write[field] = value.strftime("%Y-%m-%d")
                else:
                    row_to_write[field] = value if value is not None else ""
            writer.writerow(row_to_write)

    print(f"Data saved to {csv_file}")