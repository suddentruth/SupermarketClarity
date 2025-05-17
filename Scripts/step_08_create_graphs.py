import Scripts.script_values as v
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def create_graph_Spent_per_Day(year, market):
    df = pd.read_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Day)}")
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
    df = pd.read_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Month)}")
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
    df = pd.read_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month)}")
    df['Date'] = pd.to_datetime(df['Date'],format="%Y-%m") #remove year
    df = df.pivot(index='Date', columns='Category', values='Spent')
    
    df.to_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month_pivoted)}")

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
    df = pd.read_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Year)}")

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
    dir_csv_results_for_graphs = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market)
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