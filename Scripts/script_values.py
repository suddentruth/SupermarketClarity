"""
    Tesseract is used for reading text from images like for LIDL.
    Requires adaptation if not installed via homebrew.
    Check this link for core project: https://github.com/tesseract-ocr/tesseract
    Check this link for python wrapper: https://github.com/sirfz/tesserocr
"""
tesseract_training_data = "/opt/homebrew/share/tessdata"

### VALUES ###
# the different directories for processing data
dir_your_receipts = "Your Receipts"
dir_data = "Data"
dir_CSV_extracts = "CSV Extracts"
dir_CSV_results = "CSV Results"
dir_for_graphs = "For graphs"
dir_for_categories = "For categories"
dir_graph_images = "Graphs"


# the main directories
import os
dir_base_CSV_extracts = os.path.join(dir_data, dir_CSV_extracts)
dir_base_CSV_results = os.path.join(dir_data, dir_CSV_results)
dir_base_for_graphs = os.path.join(dir_data, dir_CSV_results, dir_for_graphs)
dir_base_for_categories = os.path.join(dir_data, dir_CSV_results, dir_for_graphs, dir_for_categories)

# file names for data extraction and processing to tables
file_merged_receipts = "merged_receipts.csv"
file_unique_items = "unique_items.csv"
file_unique_categories = "unique_categories.csv"
file_complete_items_categories = "complete_items_categories.csv"
file_unique_items_and_categories_merged = "unique_items_and_categories_merged.csv"
file_enriched_receipts = "enriched_receipts.csv"

# file names for the graphs creation
file_graph_Spent_per_Day = "Spent_per_Day.csv"
file_graph_Spent_per_Month = "Spent_per_Month.csv"
file_graph_Spent_per_Month_over_Years = "Spent_per_Month_over_Years.csv"
file_graph_Spent_per_Category_per_Month = "Spent_per_Category_per_Month.csv"
file_graph_Spent_per_Category_per_Month_pivoted = "Spent_per_Category_per_Month_pivoted.csv"
file_graph_Spent_per_Category_per_Year = "Spent_per_Category_per_Year.csv"

markets = { "REWE" : "REWE", 
            "EDEKA" : "EDEKA",
            "DM" : "DM",
            "LIDL" : "LIDL",
            "Kaufland" : "Kaufland",
            "Müller" : "Müller",
            "OBI" : "OBI"}

# Basic color codes for terminal print messages
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'  # This resets the color back to default

### FUNCTIONS ###
import csv

def writeItemsToCSV(file_path, header, items):
    try:
        with open(f"{file_path}", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            if items: writer.writerows(items)
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e} \n{BLUE}File path: {file_path}\nHeader: {header}\nItems: {items}{RESET}")

def readCSV(file_path):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)
            rows = []
            for row in reader:
                rows.append(row)
            return header, rows
    except Exception as e:
        print(f"Error reading CSV file: {e}\n{BLUE}File path: {file_path}{RESET}")
        return None, []

def readLinesFromFakePDF(file_path):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            lines = []
            for line in file:
                lines.append(line.strip())
            return lines
    except Exception as e:
        print(f"Error reading png to pdf converted file while extracing data. File: {e}\n{BLUE}File path: {file_path}{RESET}")
        return []

def readTextFromFakePDF(file_path):
    # Special handling for png files. Using reader as pdf_file string
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            text = ""
            for line in file:
                text += line
            return text
    except Exception as e:
        print(f"Error reading png to pdf converted when getting the date. File: {e}\n{BLUE}File path: {file_path}{RESET}")
        return ""
    