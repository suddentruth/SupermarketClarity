import os
import csv
import Scripts.script_values as v

def merge_known_categories_with_unique_items(year, market):
    """
    Reads the unique items list from the previous step and matches them a list that contains all items of all the years and the from user assigned categories.
    """
    item_list = [] # List to hold unique items for writing to csv
    category_dictionary = {}

    file_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, v.file_complete_items_categories)
    # to ensure category file exists alawys, even if only containing the row header
    if not os.path.exists(file_categories):
        with open(file_categories, 'w') as file:
            file.write("item,category")
    
    try:
        with open(f"{file_categories}", 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader, None)  # Skip the header row (if it exists)
            for row in reader:
                item_name = row[0]
                category = row[1]
                category_dictionary[item_name] = category
    except FileNotFoundError:
        print(f"Error: Input file '{file_categories}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return


    file_unique_items = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_" + v.file_unique_items)
    try:
        with open(f"{file_unique_items}", 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader, None)  # Skip the header row (if it exists)
            for row in reader:
                item_name = row[0]  # Assuming item name is in the first column
                category = category_dictionary.get(item_name, "Unkown")
                item_list.append([item_name, category]) # Add the entire row to the list
    except FileNotFoundError:
        print(f"Error: Input file '{file_unique_items}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return

    file_merged_items_and_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_" + v.file_unique_items_and_categories_merged)
    # Write unique items to the output CSV file
    try:
        with open(f"{file_merged_items_and_categories}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["item", "category"])  # Write the header row (if it exists in input)
            writer.writerows(item_list) # Write all unique items

        # print(f"Successfully merged known categories with unique items of year {year} to '{file_merged_items_and_categories}'.")
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")
