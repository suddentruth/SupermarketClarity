import os
import Scripts.script_values as v

def merge_known_categories_with_unique_items(year, market):
    """
    Reads the unique items list from the previous step and matches them a list that contains all items of all the years and the from user assigned categories.
    """
    item_list = [] # List to hold unique items for writing to csv
    category_dictionary = {}

    ### Handle Categories ###
    file_categories = os.path.join(v.dir_base_CSV_results, market, market+"_"+v.file_complete_items_categories)
    # to ensure category file exists always, even if only containing the header row
    if not os.path.exists(file_categories): v.writeItemsToCSV(file_categories,["item","category"],[])
    
    categoryRows = v.readCSV(file_categories)[1]
    # row[0] is item_name, row[1] is category
    for row in categoryRows:
        category_dictionary[row[0]] = row[1]

    ### Handle Unique items
    file_unique_items = os.path.join(v.dir_base_CSV_results, market, year + "_" + v.file_unique_items)
    uniqueRows = v.readCSV(file_unique_items)[1]
    # row[0] is item_name
    for row in uniqueRows:
        item_list.append([row[0], category_dictionary.get(row[0], "Unknown")]) #maps unique items with known category or otherwise adds "Unknown" category

    ### Write merged info ###
    # Write data to CSV file
    file_merged_items_and_categories = os.path.join(v.dir_base_CSV_results, market, year + "_" + v.file_unique_items_and_categories_merged)
    if item_list: v.writeItemsToCSV(file_merged_items_and_categories, ["item", "category"], item_list)