import csv
import os
import Scripts.script_values as v

def merge_to_complete_categories(market):
    """
    Takes all the files that contain the unique items and matched categories over the years.
    Merges them and puts them back into the complete_items_categories files.
    """

    unique_items = set()  # Use a set to efficiently store unique item names
    item_list = [] # List to hold unique items for writing to csv

    # Load known category items into item list
    file_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, v.file_complete_items_categories)
    try:
        with open(file_categories, 'r', newline='', encoding='utf-8') as catfile:
            reader = csv.reader(catfile)
            header = next(reader, None)  # Skip the header row (if it exists)

            for row in reader:
                item_name = row[0]
                category = row[1]
                if item_name not in unique_items:
                    unique_items.add(item_name)
                    item_list.append([item_name, category])
    except FileNotFoundError:
        print(f"Error: Input file '{file_categories}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return

    # update unique items and item-category list with data from all the years
    dir_csv_results = os.path.join(v.dir_data, v.dir_CSV_results, market)
    for filename in sorted(os.listdir(dir_csv_results), reverse=False):
        if v.file_unique_items_and_categories_merged in filename:
            filepath = os.path.join(dir_csv_results, filename)

            try:
                with open(filepath, 'r', newline='', encoding='utf-8') as catfile:
                    reader = csv.reader(catfile)
                    header = next(reader, None)  # Skip the header row (if it exists)

                    for row in reader:
                        item_name = row[0]
                        category = row[1]
                        if item_name not in unique_items:
                            unique_items.add(item_name)
                            item_list.append([item_name, category])

            except FileNotFoundError:
                print(f"Error: Input file '{filepath}' not found.")
                return
            except Exception as e:
                print(f"An error occurred while reading the input file: {e}")
                return

    # Write unique items to the output CSV file
    file_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, v.file_complete_items_categories)
    try:
        with open(f"{file_categories}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["item", "category"])  # Write the header row (if it exists in input)
            writer.writerows(item_list) # Write all unique items

        # print(f"Successfully merged dictionary of all years of unique items and categories to one list in '{file_categories}'.")

    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")
