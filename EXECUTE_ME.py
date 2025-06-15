import os
import sys
import dateutil.parser as parser
import datetime as dt

import Scripts.script_values as v
import Scripts.step_01_pdf2csv as step_01
import Scripts.step_02_merge_csvs as step_02
import Scripts.step_03_extract_unique_items as step_03
import Scripts.step_04_merge_known_categories_with_unique_items as step_04
import Scripts.step_05_merge_to_complete_item_categories as step_05
import Scripts.step_06_merge_csvs_and_categories as step_06
import Scripts.step_07_graphdata_functions as gf
import Scripts.step_08_create_graphs as cg

from tesserocr import PyTessBaseAPI

# lib and function to parallelize the pdf extraction
from concurrent.futures import ThreadPoolExecutor
def extract_pdf_to_csv(pdf, market, year):
    csv_file = pdf.replace("pdf", "csv")
    pdf_file = os.path.join(v.dir_your_receipts, market, pdf)
    step_01.extract_receipt_data(pdf_file, csv_file, year, market)

def png_to_pdf_ocr(png, market):
    png_file = os.path.join(v.dir_your_receipts, market, png)
    pdf_file = png_file.replace(".png", ".pdf")
    with PyTessBaseAPI(path=v.tesseract_training_data, lang="deu") as api:
        api.SetImageFile(png_file)
        text = api.GetUTF8Text()
        try:
            with open(pdf_file, 'w', newline='', encoding='utf-8') as file:
                file.write(text)
        except Exception as e:
            print(f"An error occurred while writing to the output file: {e} \n{v.BLUE}File path: {pdf_file}{v.RESET}")

def create_directory(dir_name):
    """Creates a directory if it doesn't exist and returns True on success, False otherwise."""
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True) # Creates directories gracefully)
            print(f"Directory '{dir_name}' created.")
            return True
        else:
            return False
    except OSError as e:  # Catch potential errors during directory creation
        print(f"Error creating directory '{dir_name}': {e}")
        return False

if __name__ == "__main__":
    # Handle the different input arguments
    if len(sys.argv) == 0:
        sys.exit(f"{v.RED}Provide name of one supported market:{v.RESET}\n{v.BLUE}{v.markets.values()}{v.RESET}.")
    
    if len(sys.argv) > 1:
        try:
            market = sys.argv[1]
            print(f"Received second argument for supermarket: {v.BLUE}{market}{v.RESET}")
            if market not in v.markets:
                sys.exit(f"{v.RED}Market must be supported. Check following list:{v.RESET}\n{v.BLUE}{v.markets.values()}{v.RESET}")
            dirs_to_create = [
                os.path.join(v.dir_your_receipts, market),
                os.path.join(v.dir_data, v.dir_CSV_extracts, market),
                os.path.join(v.dir_data, v.dir_CSV_results, market),
                os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market),
                os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, v.dir_for_categories, market),
                os.path.join(v.dir_graph_images, market)
            ]
            for d in dirs_to_create:
                create_directory(d)
        except:
            sys.exit(f"{v.RED}Error: First argument must be a valid supermarket name. Check following list:{v.RESET}\n{v.BLUE}{v.markets.values()}{v.RESET}")
    else:
        sys.exit(f"{v.RED}Provide name of one supported market:{v.RESET}\n{v.BLUE}{v.markets.values()}{v.RESET}.")

    if len(sys.argv) > 2:
        try:
            year = sys.argv[2]
            print(f"Received second argument for year: {year}")
            if len(year) != 4: raise ValueError # throw error if year is not 4 characters long
            parsed_date = parser.parse(year)  # Attempts to parse as a date if not it will throw error
        except ValueError:
            print(f"{v.RED}Error: Second argument must be a valid year, example '2025'.{v.RESET}")
    else:
        year = dt.datetime.now().strftime("%Y") # Default value
        print(f"No second argument provided. Using default value of current year, right now {v.BLUE}{year}{v.RESET}.")

    category = ""
    if len(sys.argv) > 3:
        try:
            category = str(sys.argv[3])
            print(f"Received third argument for category: {category}")
            file_unique_categories = os.path.join(v.dir_data, v.dir_CSV_results, market, market+"_"+v.file_unique_categories)
            categories = v.readCSV(file_unique_categories)[1]
            if categories:
                known_categories = []
                for cat in categories:
                    known_categories.append(cat[0])
                if category not in known_categories:
                    print(f"Failed to find category, using default value \"\". Possible values for categories are:\n{v.BLUE}{known_categories}{v.RESET}")
            
        except Exception as e:
            print(f"No valid category as third argument provided. In your data set only following categories are allowed.\nTherefore, none is selected.\n{v.BLUE}{categories}{v.RESET}")
    


    # 00 - Convert PNGs into PDFs for special cases
    # Not beautiful but it works.
    if market == v.markets.get("LIDL") or market == v.markets.get("Müller"):
        print("Step 0")
        allFiles = os.listdir(os.path.join(v.dir_your_receipts, market))
        allFiles = [file for file in allFiles if not file.startswith(".")]
        if len(allFiles) == 0:
            sys.exit(f"{v.BLUE}First time run.\nCopy your receipts into this directory '{os.path.join(v.dir_your_receipts,market)}'.\nThen run the script again!{v.RESET}")

        allPNGs = [file for file in allFiles if ".png" in file]
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(png_to_pdf_ocr, png, market) for png in allPNGs]
            for future in futures:
                future.result()

    # 01 - Convert original receipts from pdf to csv files
    print("Step 1")
    allFiles = os.listdir(os.path.join(v.dir_your_receipts,market))
    allFiles = list(filter(lambda file: not file.startswith("."), allFiles)) # exclude system files that start with '.'.
    if len(allFiles) == 0:
        sys.exit(f"{v.BLUE}First time run.\nCopy your receipts into this directory '{os.path.join(v.dir_your_receipts,market)}'.\nThen run the script again!{v.RESET}")
    
    allPDFs = [file for file in allFiles if ".pdf" in file]
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(extract_pdf_to_csv, pdf, market, year) for pdf in allPDFs]
        for future in futures:
            future.result()
    
    # 02 - Merge CSVs receipts to x_merged_receipts where x is the year
    print("Step 2")
    step_02.merge_csv_files(year, market)
    
    # 03 - Extract unique items from x_merged_receipt files
    print("Step 3")
    step_03.extract_unique_items(year, market)
    
    # 04 - Unique items and known categories merged
    print("Step 4")
    step_04.merge_known_categories_with_unique_items(year, market)

    # 05 - Sidestep - Merge all unique items and categories over the years into one complete_item_category.csv file
    print("Step 5")
    step_05.merge_to_complete_categories(market)

    # 06 - Create final enriched receipts
    print("Step 6")
    step_06.enrich_items_with_category(year, market)
    
    # 07 - Create the data for the graphs
    print("Step 7")
    gf.calculate_Spent_per_Day(year, market)
    gf.calculate_Spent_per_Month(year, market)
    gf.calculate_Spent_per_Category_per_Month(year, market)
    gf.calculate_Spent_per_Category_per_Year(year, market)
    if category: gf.calculate_Spent_for_Category_x_per_Year(year, market, category)
    gf.calculate_Spent_for_Categories_over_years(market)
    
    # 08 - Create graphs
    print("Step 8")
    cg.create_graph_Spent_per_Day(year, market)
    cg.create_graph_Spent_per_Month(year, market)
    cg.create_graph_Spent_per_Category_per_Year(year, market)
    cg.create_graph_Spent_per_Category_per_Month(year, market)
    cg.create_graph_Spent_per_Month_over_Years(market)
    if category: cg.create_graph_Spent_for_Category_per_Year(year, market, category)
    cg.create_graph_Spent_for_Category(market)


    print(f"{v.GREEN}done :) Please check directory '{os.path.join(v.dir_graph_images, market)}' for images!{v.RESET}")
