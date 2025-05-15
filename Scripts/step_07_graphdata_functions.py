import Scripts.script_values as v
import csv
import os


def read_enriched_receipts(year, market):
    file_enriched_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_"+ v.file_enriched_receipts)
    selected_csv = []
    try:
        with open(f"{file_enriched_receipts}", 'r', newline='', encoding='utf-8') as cat_infile:
            reader = csv.reader(cat_infile)
            header = next(reader, None)

            for row in reader:
                selected_csv.append(row)

            return selected_csv
    except FileNotFoundError:
        print(f"Error: Enriched receipt file '{file_enriched_receipts}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the category file: {e}")
        return

def read_complete_items_categories(market):
    file_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, v.file_complete_items_categories)
    selected_csv = []
    try:
        with open(f"{file_categories}", 'r', newline='', encoding='utf-8') as cat_infile:
            reader = csv.reader(cat_infile)
            header = next(reader, None)

            for row in reader:
                selected_csv.append(row)

            return selected_csv
    except FileNotFoundError:
        print(f"Error: Complete item category file '{file_categories}' not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the category file: {e}")
        return


def calculate_Price_Times_Quantity(year, market):
    original_csv = read_enriched_receipts(year, market)
    enriched_csv = []
    for row in original_csv:
        totalPrice = float(row[1])*float(row[2])
        enriched_csv.append(row + [totalPrice])
    return enriched_csv

def calculate_Spent_per_Day(year, market):
    enriched_csv = calculate_Price_Times_Quantity(year, market)
    table_Spent_Per_Day = []
    dateToCheck = "01.01.1970"
    spentPerDay = 0
    for row in enriched_csv:
        if row == enriched_csv[-1]: # last row! ensure the last value is correctly checked in.
            if row[3] == dateToCheck: # last item of the last day
                spentPerDay += row[5]
                table_Spent_Per_Day.append([dateToCheck, round(spentPerDay,2)])
            else: # only item bought. Emergency buy, huh? 
                table_Spent_Per_Day.append([dateToCheck, round(spentPerDay,2)])
                dateToCheck = row[3]
                spentPerDay = row[5]
                table_Spent_Per_Day.append([dateToCheck, round(spentPerDay,2)])
        if row[3] == dateToCheck: # one more item for this known date
            spentPerDay += row[5]
        else: # new date, new calculations!
            table_Spent_Per_Day.append([dateToCheck, round(spentPerDay,2)])
            dateToCheck = row[3]
            spentPerDay = row[5] 

    table_Spent_Per_Day.pop(0) # to remove default value of 01.01.1970
    
    
    # Write the CSV file
    file_graph_Spent_per_Day = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Day)
    try:
        with open(f"{file_graph_Spent_per_Day}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Date", "Spent"])
            writer.writerows(table_Spent_Per_Day)

        # print(f"Wrote CSV with spend money per day per month of year {year} to '{file_graph_Spent_per_Day}'.")
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")

    
    
    return table_Spent_Per_Day # returns a list with two columns. First the day, Second total sum spent money


def calculate_Spent_per_Month(year, market):
    enriched_csv = calculate_Price_Times_Quantity(year, market)
    table_Spent_Per_Month = []
    dateToCheck = "01.1970"
    spentPerMonth = 0
    for row in enriched_csv:
        if row == enriched_csv[-1]: # last row! ensure the last value is correctly checked in.
            if dateToCheck in row[3]: # last item of the last day
                spentPerMonth += row[5]
                table_Spent_Per_Month.append([dateToCheck, round(spentPerMonth,2)])
            else: # only item bought. Emergency buy, huh? 
                table_Spent_Per_Month.append([dateToCheck, round(spentPerMonth,2)])
                dateToCheck = row[3][-7:]
                spentPerMonth = row[5]
                table_Spent_Per_Month.append([dateToCheck, round(spentPerMonth,2)])
        if dateToCheck in row[3]: # one more item for this known date
            spentPerMonth += row[5]
        else: # new date, new calculations!
            table_Spent_Per_Month.append([dateToCheck, round(spentPerMonth,2)])
            dateToCheck = row[3][-7:]
            spentPerMonth = row[5]

    table_Spent_Per_Month.pop(0) # to remove default value of 01.01.1970
    
    # Write the CSV file
    file_graph_Spent_per_Month = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Month)
    try:
        with open(f"{file_graph_Spent_per_Month}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Date", "Spent"])
            writer.writerows(table_Spent_Per_Month)

        # print(f"Wrote CSV with spend money per month of year {year} to '{file_graph_Spent_per_Month}'.")
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")

    
    
    return table_Spent_Per_Month # returns a list with two columns. First the month, Second total sum spent money

# header_enriched_receipt = ["Item Name","Price","Quantity","Date","Category"]
def calculate_Spent_per_Category_per_Month(year, market):
    enriched_csv = calculate_Price_Times_Quantity(year, market)
    complete_items_categories_csv = read_complete_items_categories(market)
    unique_categories = set()
    dateToCheck = ""
    dictToList = []
    rangeOfMonths = range(1,13) # Create months to ease checking
    months = []
    # Do some limbo to get months in form of %mm for %mm.%YYYY later
    for x in rangeOfMonths:
        if x < 10:
            months.append("0" + str(x))
        else:
            months.append(str(x))

    # Get unique categories of this year
    for row in complete_items_categories_csv:
        category = row[1] 
        if category not in unique_categories:
            unique_categories.add(category)
    
    unique_categories = sorted(unique_categories)

    for month in months:
        dateToCheck = f"{month}.{year}" # Date string to check for
        spentPerCategoryPerYear = {} # Resetted for each month

        for category in unique_categories:
            spentPerCategoryPerYear[category] = 0
            for row in enriched_csv:
                if row[4] == category and dateToCheck in row[3]:
                    spentPerCategoryPerYear[category] += row[5]

        for category in unique_categories:
            dictToList.append([dateToCheck, category, round(spentPerCategoryPerYear[category],2)])

    # Write the CSV file
    file_graph_Spent_per_Category_per_Month = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month)
    try:
        with open(f"{file_graph_Spent_per_Category_per_Month}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Date", "Category", "Spent"])
            writer.writerows(dictToList)

        # print(f"Wrote CSV with spend money per category per month of year {year} to '{file_graph_Spent_per_Category_per_Month}'.")
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")

    return dictToList

def calculate_Spent_per_Category_per_Year(year, market):
    enriched_csv = calculate_Price_Times_Quantity(year, market)
    complete_items_categories_csv = read_complete_items_categories(market)
    unique_categories = set()

    for row in complete_items_categories_csv:
        category = row[1]
        if category not in unique_categories:
            unique_categories.add(category)

    unique_categories = sorted(unique_categories)

    spentPerCategoryPerYear = {}
    for category in unique_categories:
        spentPerCategoryPerYear[category] = 0
        for row in enriched_csv:
            if row[4] == category:
                spentPerCategoryPerYear[category] += row[5]

    dictToList = []
    for category in unique_categories:
        dictToList.append([category, round(spentPerCategoryPerYear[category],2)])


    # Write the CSV file
    file_graph_Spent_per_Category_per_Year = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Year)
    try:
        with open(f"{file_graph_Spent_per_Category_per_Year}", 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Category", "Spent"])
            writer.writerows(dictToList)

        # print(f"Wrote CSV with spend money per category per month of year {year} to '{file_graph_Spent_per_Category_per_Year}'.")
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")

    return dictToList
