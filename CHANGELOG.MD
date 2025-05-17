v.0.2.1
+ Added market info to "complete_items_categories" file
+ CleanUp now saves "complete_items_categories" file to main directory with timestamp to prevent accidential deletion.
    + Adapted .gitignore file respectively.

v0.2.0
+ Added support for markets DM and EDEKA
+ Refactored code reduce overhead by extracting write and read CSV parts.
+ Improved date detection if first step when analyzing the PDF file
+ Support now multiple PDF pages
+ Providing market information in the two main commands is now mandatory. Also changed the order. First Argument needs to be market, second year is optional, defaults to current year.
+ Updated Readme
+ Changed graph "Spent per Category per Year" from line chat to bar chart.

v0.1.0
+ Initial Setup
+ Supported market REWE
+ Baseline functionality of extracting data from PDF receipts, save them into CSV files, and create following graphs from it
    + Spent per Day
    + Spent per Month
    + Spent per Category per Year
    + Spent per Category per Month (as line chart)
    + Spent per Category per Month (as bar chart)
    + Spent per Month_over Years
+ Provided two scripts one for creation of data based on market and year, the other one for deleting data which means resetting the repository.