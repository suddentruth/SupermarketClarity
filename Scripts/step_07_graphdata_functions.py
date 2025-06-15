import Scripts.script_values as v
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


def run_category_year(args):
    year, market, category = args
    calculate_Spent_for_Category_x_per_Year(year, market, category)

def calculate_Spent_per_Day(year, market):
    table_Spent_Per_Day = getSpentPerTime(market, year, "Day")
    
    # Write data to CSV file
    file_graph_Spent_per_Day = os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Day)
    if table_Spent_Per_Day: v.writeItemsToCSV(file_graph_Spent_per_Day, ["Date", "Spent"], table_Spent_Per_Day) 

def calculate_Spent_per_Month(year, market):
    table_Spent_Per_Month = getSpentPerTime(market, year, "Month")
    
    # Write data to CSV file
    file_graph_Spent_per_Month = os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Month)
    if table_Spent_Per_Month: v.writeItemsToCSV(file_graph_Spent_per_Month, ["Date", "Spent"], table_Spent_Per_Month)

# header_enriched_receipt = ["Item Name","Price","Quantity","Date","Category"]
def calculate_Spent_per_Category_per_Month(year, market):
    file_enriched_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    enrichedReceiptsRows = v.readCSV(file_enriched_receipts)[1]
    unique_categories = getUniqueCategories(market)

    items = []
    months = [f"{year}-{str(m).zfill(2)}" for m in range(1, 13)]

    for month in months:
        spentPerCategory = {cat: 0.0 for cat in unique_categories}
        for row in enrichedReceiptsRows:
            if len(row) < 6:
                continue
            cat = row[4]
            if cat in spentPerCategory and row[3].startswith(month):
                try:
                    spentPerCategory[cat] += float(row[5])
                except Exception:
                    continue
        for cat in unique_categories:
            items.append([month, cat, round(spentPerCategory[cat], 2)])

    # Write data to CSV file
    file_graph_Spent_per_Category_per_Month = os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month)
    if items: v.writeItemsToCSV(file_graph_Spent_per_Category_per_Month, ["Date", "Category", "Spent"], items)

def calculate_Spent_per_Category_per_Year(year, market):
    file_enriched_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    enrichedReceiptsRows = v.readCSV(file_enriched_receipts)[1]
    unique_categories = getUniqueCategories(market)

    spentPerCategoryPerYear = {}
    for category in unique_categories:
        spentPerCategoryPerYear[category] = 0
        # row[0] is item_name, row[1] is Price, row[2] is Quantity, row[3] is Date, row[4] is Category, row[5] is Total Price
        for row in enrichedReceiptsRows:
            if row[4] == category:
                spentPerCategoryPerYear[category] += float(row[5])

    items = []
    for category in unique_categories:
        items.append([category, round(spentPerCategoryPerYear[category],2)])

    # Write data to CSV file
    file_graph_Spent_per_Category_per_Year = os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Year)
    if items: v.writeItemsToCSV(file_graph_Spent_per_Category_per_Year, ["Category", "Spent"], items)

def calculate_Spent_for_Category_x_per_Year(year, market, category):
    """
    Calculates daily spending for a specific category in a year and writes to CSV.
    """
    file_enriched_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_" + v.file_enriched_receipts)
    enrichedReceiptsRows = v.readCSV(file_enriched_receipts)[1]

    filtered = [row for row in enrichedReceiptsRows if len(row) >= 5 and row[4] == category]
    table = getSpentPerTime(market, year, "Day", filtered)
    file_table = os.path.join(v.dir_base_for_categories, market, f"{year}_{category}_{v.file_graph_Spent_per_Category_per_Year}")
    if table:
        v.writeItemsToCSV(file_table, ["Date", "Spent"], table)

def calculate_Spent_for_Categories_over_years(market):
    """
    Calculates daily spending for each category over all years.
    """
    dir_graphs = os.path.join(v.dir_base_for_graphs, market)
    years = sorted({filename[:4] for filename in os.listdir(dir_graphs) if v.file_graph_Spent_per_Month in filename})
    file_unique_categories = os.path.join(v.dir_base_CSV_results, market, market + "_" + v.file_unique_categories)
    categories = [row[0] for row in v.readCSV(file_unique_categories)[1]]

    with ThreadPoolExecutor() as executor:
        executor.map(run_category_year, [(year, market, category) for category in categories for year in years])

## helper functions ##
def getUniqueCategories(market):
    """
    Returns a sorted list of unique, normalized categories for a market.
    """
    unique_categories = set()
    file_categories = os.path.join(v.dir_base_CSV_results, market, market + "_" + v.file_complete_items_categories)
    for row in v.readCSV(file_categories)[1]:
        if len(row) > 1:
            unique_categories.add(row[1].strip())
    return sorted(unique_categories)


def getSpentPerTime(market, year, time, data=None):
    """
    Aggregates spending per day or month.
    time: "Month" or "Day"
    """
    file_enriched_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    if data is None:
        enrichedReceiptsRows = v.readCSV(file_enriched_receipts)[1]
    else:
        enrichedReceiptsRows = data

    spent = defaultdict(float)
    for row in enrichedReceiptsRows:
        if len(row) < 6:
            continue
        try:
            date = row[3]
            amount = float(row[5])
        except Exception:
            continue
        if time == "Month":
            key = date[:7]  # YYYY-MM
        elif time == "Day":
            key = date      # YYYY-MM-DD
        else:
            continue
        spent[key] += amount

    # Return sorted by date
    return sorted([[k, round(v, 2)] for k, v in spent.items()])