import os
import Scripts.script_values as v

def merge_csv_files(year, market):
    """
    Takes all the csv files that contain the extrated data for each purchase and merges them into one big csv file sorted by date.
    Newest purchases at the end of the list
    """
    all_data = [] # List to store data from all CSV files
    header = None  # To store the header row (if it exists in any of the files)

    dir_csv_extracts = os.path.join(v.dir_base_CSV_extracts, market)
    for filename in sorted(os.listdir(dir_csv_extracts), reverse=False):
        if filename.endswith(".csv") and year in filename:
            filepath = os.path.join(v.dir_base_CSV_extracts, market, filename)
            header, rows = v.readCSV(filepath)
            all_data.extend(rows)

    # Write data to CSV file
    file_merged_receipts = os.path.join(v.dir_base_CSV_results, market, year + "_" + v.file_merged_receipts)
    if header and all_data: v.writeItemsToCSV(file_merged_receipts,header,all_data)
    
