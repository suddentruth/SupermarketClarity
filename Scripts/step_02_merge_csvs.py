import csv
import os
import Scripts.script_values as v

def merge_csv_files(year, market):
    """
    Takes all the csv files that contain the extrated data for each purchase and merges them into one big csv file sorted by date.
    Newest purchases at the end of the list
    """
    all_data = [] # List to store data from all CSV files
    header = None  # To store the header row (if it exists in any of the files)

    dir_csv_extracts = os.path.join(v.dir_data, v.dir_CSV_extracts, market)
    for filename in sorted(os.listdir(dir_csv_extracts), reverse=False):
        if filename.endswith(".csv") and year in filename:
            filepath = os.path.join(v.dir_data, v.dir_CSV_extracts, market, filename)
            try:
                with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    header_row = next(reader, None) # Read the header row (if it exists)

                    if header is None:
                        header = header_row  # Store the header from the first file
                    else:
                        # If a header already exists, skip it in subsequent files.
                        pass

                    for row in reader:
                        all_data.append(row)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # Write merged data to the output CSV file
    file_merged_receipts = os.path.join(v.dir_data, v.dir_CSV_results, market, year + "_" + v.file_merged_receipts)
    try:
        with open( file_merged_receipts, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            if header:
                writer.writerow(header) # Write the header row (from the first file)
            writer.writerows(all_data) # Write all data rows

        # print(f"Successfully merged CSV files into {file_merged_receipts}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")
