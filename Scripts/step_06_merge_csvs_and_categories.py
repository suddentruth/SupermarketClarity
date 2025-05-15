import os
import csv
import Scripts.script_values as v

def enrich_items_with_category(year, market):
    """
    Enrich the list of all bought items over the year with the known matching category.
    Save new list into an enriched receipts CSV file
    """
    # Create a dictionary for category lookup from the category file
    file_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, v.file_complete_items_categories)
    category_dictionary = {}
    try:
        with open(f"{file_categories}", 'r', newline='', encoding='utf-8') as cat_infile:
            reader = csv.reader(cat_infile)
            next(reader, None)  # Skip header row if it exists

            for row in reader:
                item_name = row[0]
                category = row[1]
                category_dictionary[item_name] = category
    except FileNotFoundError:
        print(f"Error: Category file '{file_categories}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the category file: {e}")
        return

    # Read big receipt file and attach category to it. Leave category empty if unknown
    file_merged_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_"+ v.file_merged_receipts)
    enriched_items = []
    try:
        with open(f"{file_merged_receipts}", 'r', newline='', encoding='utf-8') as merged_infile:
            reader = csv.reader(merged_infile)
            header = next(reader, None)
            
            for row in reader:
                item_name = row[0]
                category = category_dictionary.get(item_name, "") # Get category or empty string if not found
                enriched_items.append([item_name, row[1], row[2], row[3], category]) # Add item and category

    except FileNotFoundError:
        print(f"Error: Merged file '{file_merged_receipts}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the merged file: {e}")
        return

    # Write enriched data to output CSV
    file_enriched_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    try:
        with open(f"{file_enriched_receipts}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Item Name", "Price", "Quantity", "Date", "Category"])  # Write header row
            writer.writerows(enriched_items)

        # print(f"Successfully enriched receipts of year {year} and wrote them to '{file_enriched_receipts}'.")

    except Exception as e:
        print(f"An error occurred while writing the output file: {e}")

