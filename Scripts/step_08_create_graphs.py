import Scripts.script_values as v
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import dayplot as dp

# Library amd function to parallelize the loading of dataframes
from concurrent.futures import ThreadPoolExecutor
def load_dataframe(args):
    category, year, file_table, dummy = args
    if os.path.exists(file_table):
        return ((category, year), pd.read_csv(file_table))
    else:
        return ((category, year), dummy)

def create_graph_Spent_per_Day(year, market):
    df = pd.read_csv(f"{os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Day)}")
    df['Date'] = df['Date'].astype(str)
    dfBackground = pd.DataFrame({
        'Date': [f'{year}-01-01', f'{year}-12-31'],
        'Spent': [0, 0]
    })

    # Start plot creation
    dfBackground['Date'] = pd.to_datetime(dfBackground['Date'],format="%Y-%m-%d")
    df['Date'] = pd.to_datetime(df['Date'],format="%Y-%m-%d")
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Spent'], 'o-')
    plt.plot(dfBackground['Date'], dfBackground['Spent'], marker="", linestyle="") #invisible plot to get good x-axis of whole year
    plt.xlabel('Date')
    plt.ylabel('Spent Money (Euro)')
    plt.title(f"Spending Over Time in {year} per day")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)

    # Save the plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Day+".png")}" , bbox_inches='tight')

def create_graph_Spent_per_Month(year, market):
    df = pd.read_csv(f"{os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Month)}")
    # Add start and end of year to data set if not already given.
    df['Date'] = df['Date'].astype(str)
    dfBackground = pd.DataFrame({
        'Date': [f'{year}-01', f'{year}-12'],
        'Spent': [0, 0]
    })

    # Start plot creation
    dfBackground['Date'] = pd.to_datetime(dfBackground['Date'],format="%Y-%m")
    df['Date'] = pd.to_datetime(df['Date'],format="%Y-%m")
    plt.figure(figsize=(12, 6)) 
    plt.plot(df['Date'], df['Spent'], 'o-')
    plt.plot(dfBackground['Date'], dfBackground['Spent'], marker="", linestyle="") #invisible plot to get good x-axis of whole year
    plt.xlabel('Month')
    plt.ylabel('Spent Money in €')
    plt.title(f"Spending Over Time in {year} per month")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)

    # Show the plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Month+".png")}", bbox_inches='tight')

def create_graph_Spent_per_Category_per_Month(year, market):
    ### FIRST PLOT ###
    df = pd.read_csv(f"{os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month)}")
    df['Date'] = pd.to_datetime(df['Date'],format="%Y-%m") #remove year
    df = df.pivot(index='Date', columns='Category', values='Spent')
    
    df.to_csv(f"{os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month_pivoted)}")

    # Change linestyle after 10 categories because then the color repeats
    linestyles = ['solid', 'dashed', 'dashdot', 'dotted'] # linestyles for better readability of graph
    selectedLinestyle = 0
    plotNumberCounter = 0
    plt.figure(figsize=(12, 6))
    for category in df.columns:
        plt.plot(df.index, df[category], label=category, marker='o', linestyle=linestyles[selectedLinestyle]) #Plot each column with its name as a legend
        plotNumberCounter += 1
        if plotNumberCounter == 10:
            selectedLinestyle += 1
            plotNumberCounter = 0
            if selectedLinestyle == 4:
                selectedLinestyle = 0

    # Add labels and title
    plt.xlabel('Months')
    plt.ylabel('Spent Money in €')
    plt.title(f"Spending Over Time Each Month in {year} per Category")
    plt.legend(bbox_to_anchor=(1.0, 1.0)) 
    plt.grid(True)

    # Save plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Category_per_Month+".png")}", bbox_inches='tight')

    ### SECOND PLOT ###
    ## create as stacked bars graphs
    plt.figure(figsize=(12, 6))    
    plotNumberCounter = 0
    edgeColor = [ "pink", "black", "red", "blue", "purple"] # edgecolor for better readability of graph
    selectedEdgeColor = 0
    bottom = np.zeros(12)
    width = 20 # magic number somehow correlated to the x-scale
    fig, ax = plt.subplots()
    # Change edgeColor after 10 categories because then the inner color repeats
    for category in df.columns:
        ax.bar(df.index, df[category], width , label=category, bottom=bottom, edgecolor=edgeColor[selectedEdgeColor] )
        bottom += df[category]
        plotNumberCounter += 1
        if plotNumberCounter == 10:
            selectedEdgeColor += 1
            plotNumberCounter = 0
            if selectedEdgeColor == 5:
                selectedEdgeColor = 0

    plt.xlabel('Months')
    plt.ylabel('Spent Money in €')
    plt.title(f"Spending Over Time Each Month in {year} per Category")
    plt.legend(bbox_to_anchor=(1.0, 1.0))
    plt.grid(True)
    ax.set_axisbelow(True) # put grid more into the background
    ax.yaxis.grid(color='gray', linestyle='dashed')

    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Category_per_Month+"-stacked.png")}", bbox_inches='tight')
    


def create_graph_Spent_per_Category_per_Year(year, market):
    df = pd.read_csv(f"{os.path.join(v.dir_base_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Year)}")

    plt.figure(figsize=(12, 6))
    fig, ax = plt.subplots()
    plt.bar(df['Category'], df['Spent'])
    plt.xlabel('Category')
    plt.ylabel('Spent Money in €')
    plt.title(f"Spending Over Time in {year} per Category")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    ax.set_axisbelow(True) # put grid more into the background
    ax.yaxis.grid(color='gray', linestyle='dashed')

    # Save plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Category_per_Year+".png")}", bbox_inches='tight')

def create_graph_Spent_per_Month_over_Years(market):
    dfs = []
    dir_csv_results_for_graphs = os.path.join(v.dir_base_for_graphs, market)
    for filename in sorted(os.listdir(dir_csv_results_for_graphs), reverse=False):
        if v.file_graph_Spent_per_Month in filename:
            filepath = os.path.join(dir_csv_results_for_graphs, filename)
            df = pd.read_csv(filepath)
            df['Date'] = df['Date'].astype(str)
            df['Date'] = pd.to_datetime(df['Date'],format="%Y-%m")
            dfs.append(df)

    # Start plot creation    
    plt.figure(figsize=(12, 6)) 
    for df in dfs:
        plt.plot(df['Date'], df['Spent'], 'o-')

    plt.xlabel('Month')
    plt.ylabel('Spent Money in €')
    plt.title(f"Spending Over Time Per Month Over Years")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)

    # Save plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, v.file_graph_Spent_per_Month_over_Years+".png")}", bbox_inches='tight')

def create_graph_Spent_for_Category_per_Year(year, market, category):
    file_tableSpentPerCategoryXPerDay = os.path.join(v.dir_base_for_categories,market,year+"_"+category+"_"+v.file_graph_Spent_per_Category_per_Year)
    df = pd.read_csv(file_tableSpentPerCategoryXPerDay)
    
    fig, ax = plt.subplots(figsize=(15,6))
    # cmap = plt.cm.Greens
    cmap = plt.cm.copper
    
    dp.calendar(
        dates=df["Date"],
        values=df["Spent"],
        cmap=cmap,
        start_date=f"{year}-01-01",
        end_date=f"{year}-12-31",
        ax=ax,
        week_starts_on="Monday"
    )

    plt.colorbar(plt.pcolor(df['Spent'].values.reshape(1,-1), cmap=cmap,visible=False))
    plt.title(f"Heatmap for category \"{category}\" in year {year}")
    
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+category+"_"+v.file_graph_Spent_per_Category_per_Year+".png")}", bbox_inches='tight')

def create_graph_Spent_for_Category(market):
    
    # Get the years of data
    dir_csv_results_for_graphs = os.path.join(v.dir_base_for_graphs, market)
    years = sorted({filename[:4] for filename in os.listdir(dir_csv_results_for_graphs) if v.file_graph_Spent_per_Month in filename})
    file_unique_categories = os.path.join(v.dir_base_CSV_results, market, market+"_"+v.file_unique_categories)
    categories = [row[0] for row in v.readCSV(file_unique_categories)[1]]

    # Preload all dataframes
    dataframes = {}
    dummyframes = {year: pd.DataFrame(data={'Date': [f"{year}-01-01", f"{year}-12-31"], 'Spent': [0, 0]}) for year in years}
    # Prepare arguments for parallel loading
    load_args = []
    for category in categories:
        for year in years:
            file_table = os.path.join(
                v.dir_base_for_categories, market,
                f"{year}_{category}_{v.file_graph_Spent_per_Category_per_Year}"
            )
            load_args.append((category, year, file_table, dummyframes[year]))

    # Parallel load of dataframes from CSV files
    dataframes = {}
    with ThreadPoolExecutor() as executor:
        for key, df in executor.map(load_dataframe, load_args):
            dataframes[key] = df

    # Plot creation
    fig, axs = plt.subplots(
        figsize=(15 * max(1, len(years)), 6 * max(1, len(categories))),
        nrows=len(categories), ncols=len(years),
        squeeze=False
    )
    # Check this page for other, better colors: https://matplotlib.org/stable/users/explain/colors/colormaps.html
    cmap = plt.cm.copper

    # Set figure title
    fig.suptitle("Spent Money per Category per Day over Years", fontsize=55 , y=1.005)
    for i, category in enumerate(categories):
        for j, year in enumerate(years):
            df = dataframes[(category, year)]
            ax = axs[i, j]
            # Subplot title: category and year
            ax.set_title(f"{category}\n{year}", fontsize=30)

            dp.calendar(
                dates=df['Date'],
                values=df['Spent'],
                cmap=cmap,
                start_date=f"{year}-01-01",
                end_date=f"{year}-12-31",
                week_starts_on="Monday",
                ax=ax
            )
            
            heatmap = plt.pcolor(df['Spent'].values.reshape(1,-1), cmap=cmap,visible=False)
            cb = fig.colorbar(heatmap,ax=ax)
            # if not os.path.exists(file_tableSpentPerCategoryXPerDay): cb.remove() # doesn't work out as wanted. If last row contains no data for a year it will not be shown.
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Leave space for suptitle
    
    # plt.show()
    plt.savefig(
        os.path.join(v.dir_graph_images, market, "Over_Years_per_category_"+v.file_graph_Spent_per_Category_per_Year+".png"),
        bbox_inches='tight'
    )
