import Scripts.script_values as v
import os

def calculate_Spent_per_Day(year, market):
    table_Spent_Per_Day = getSpentPerTime(market, year, "Day")
    
    # Write data to CSV file
    file_graph_Spent_per_Day = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Day)
    if table_Spent_Per_Day: v.writeItemsToCSV(file_graph_Spent_per_Day, ["Date", "Spent"], table_Spent_Per_Day) 

def calculate_Spent_per_Month(year, market):
    table_Spent_Per_Month = getSpentPerTime(market, year, "Month")
    
    # Write data to CSV file
    file_graph_Spent_per_Month = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Month)
    if table_Spent_Per_Month: v.writeItemsToCSV(file_graph_Spent_per_Month, ["Date", "Spent"], table_Spent_Per_Month)

# header_enriched_receipt = ["Item Name","Price","Quantity","Date","Category"]
def calculate_Spent_per_Category_per_Month(year, market):
    file_enriched_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    enrichedReceiptsRows = v.readCSV(file_enriched_receipts)[1]
    unique_categories = getUniqueCategories(market)

    items = []
    rangeOfMonths = range(1,13) # Create months to ease checking
    months = []
    # Do some limbo to get months in form of %mm for %YYYY-%mm later
    for x in rangeOfMonths:
        if x < 10: months.append("0" + str(x))
        else: months.append(str(x))
    
    for month in months:
        dateToCheck = f"{year}-{month}" # Date string to check for
        spentPerCategoryPerYear = {} # Resetted for each month

        for category in unique_categories:
            spentPerCategoryPerYear[category] = 0
            # row[0] is item_name, row[1] is Price, row[2] is Quantity, row[3] is Date, row[4] is Category, row[5] is Total Price
            for row in enrichedReceiptsRows:
                if row[4] == category and dateToCheck in row[3]:
                    spentPerCategoryPerYear[category] += float(row[5])

        for category in unique_categories:
            items.append([dateToCheck, category, round(spentPerCategoryPerYear[category],2)])

    # Write data to CSV file
    file_graph_Spent_per_Category_per_Month = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month)
    if items: v.writeItemsToCSV(file_graph_Spent_per_Category_per_Month, ["Date", "Category", "Spent"], items)

def calculate_Spent_per_Category_per_Year(year, market):
    file_enriched_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_"+ v.file_enriched_receipts)
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
    file_graph_Spent_per_Category_per_Year = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Year)
    if items: v.writeItemsToCSV(file_graph_Spent_per_Category_per_Year, ["Category", "Spent"], items)

## helper functions ##
def getUniqueCategories(market):
    unique_categories = set()
    file_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, market+"_"+v.file_complete_items_categories)
    categoriesRows = v.readCSV(file_categories)[1]
    # row[0] is item_name, row[1] is Category
    for row in categoriesRows:
        if row[1] not in unique_categories:
            unique_categories.add(row[1])
    
    return sorted(unique_categories)

def getSpentPerTime(market, year, time):
    """
      Use "Month" or "Day" for time argument

      To extend add content at the lines where "dateToCheck" is used.

      Consists in general of 3 cases to check
      1. Did we reach the last row?
        a. if the date did not change, add to current entry the table
        b. date changed, new new entry in table
    """
    file_enriched_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    enrichedReceiptsRows = v.readCSV(file_enriched_receipts)[1]
    table_Spent_Per_Time = []
    if time == "Month": dateToCheck = "1970-01"
    elif time == "Day": dateToCheck = "1970-01-01"
    spentPerTime = 0.0
    # row[0] is item_name, row[1] is Price, row[2] is Quantity, row[3] is Date, row[4] is Category, row[5] is Total Price
    for row in enrichedReceiptsRows:
        row[5] = float(row[5])
        if row == enrichedReceiptsRows[-1]: # last row! ensure the last value is correctly checked in.
            if row[3] == dateToCheck or dateToCheck in row[3]: # first one valid for time as days, second for time as months
                spentPerTime += row[5]
                table_Spent_Per_Time.append([dateToCheck, round(spentPerTime,2)])
            else: # only item bought. Emergency buy, huh? 
                table_Spent_Per_Time.append([dateToCheck, round(spentPerTime,2)])
                if time == "Month": dateToCheck = row[3][:7] # turns 2025-03-21 into 2025-03
                elif time == "Day": dateToCheck = row[3]
                spentPerTime = row[5]
                table_Spent_Per_Time.append([dateToCheck, round(spentPerTime,2)])
        if row[3] == dateToCheck or dateToCheck in row[3]: # first one valid for time as days, second for time as months
            spentPerTime += row[5]
        else: # new date, new calculations!
            table_Spent_Per_Time.append([dateToCheck, round(spentPerTime,2)])
            if time == "Month": dateToCheck = row[3][:7] # turns 2025-03-21 into 2025-03
            elif time == "Day": dateToCheck = row[3]
            spentPerTime = row[5]

    table_Spent_Per_Time.pop(0) # to remove default value of 1970-01
    return table_Spent_Per_Time