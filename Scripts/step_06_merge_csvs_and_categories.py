import os
import Scripts.script_values as v

def enrich_items_with_category(year, market):
    """
    Enrich the list of all bought items over the year with the known matching category.
    Save new list into an enriched receipts CSV file
    """
    # Create a dictionary for category lookup from the category file
    category_dictionary = {}
    file_categories = os.path.join(v.dir_base_CSV_results, market, market+"_"+v.file_complete_items_categories)
    completeItemsCategoriesRows = v.readCSV(file_categories)[1]
    # row[0] is item_name, row[1] is category
    for row in completeItemsCategoriesRows:
        category_dictionary[row[0]] = row[1]

    # Read big receipt file and attach category to it. Leave category empty if unknown
    enriched_items = []
    file_merged_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_"+ v.file_merged_receipts)
    mergedReceiptsRows = v.readCSV(file_merged_receipts)[1]
    # row[0] is item_name, row[1] is Price, row[2] is Quantity, row[3] is Date
    for row in mergedReceiptsRows:
        category = category_dictionary.get(row[0], "") # Get category or empty string if not found
        totalPrice = round(float(row[1])*float(row[2]),2) # Calculate total price
        enriched_items.append([row[0], row[1], row[2], row[3], category, totalPrice]) # category and totalPrice as enrichment
   
    # Write data to CSV file
    file_enriched_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    if enriched_items: v.writeItemsToCSV(file_enriched_receipts, ["Item Name", "Price", "Quantity", "Date", "Category","Total Price"], enriched_items)