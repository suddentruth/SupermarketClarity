import Scripts.script_values as v
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def create_graph_Spent_per_Day(year, market):
    df = pd.read_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Day)}")
    df['Date'] = df['Date'].astype(str)
    # Add start and end of year to data set if not already given.
    # startOfYear = pd.DataFrame({
    #     'Date': [f'01.01.{year}'],
    #     'Spent': [0]
    # })
    # endOfYear = pd.DataFrame({
    #     'Date': [f'31.12.{year}'],
    #     'Spent': [0]
    # })
    # if df['Date'].loc[0] != f'01.01.{year}':
    #     df = pd.concat([startOfYear, df], ignore_index=True)
    # if df['Date'].loc[len(df)-1] != f'31.12.{year}':
    #     df = pd.concat([df, endOfYear], ignore_index=True)
    dfBackground = pd.DataFrame({
        'Date': [f'01.01.{year}', f'31.12.{year}'],
        'Spent': [0, 0]
    })

    # Start plot creation
    dfBackground['Date'] = pd.to_datetime(dfBackground['Date'],dayfirst=True)
    df['Date'] = pd.to_datetime(df['Date'],dayfirst=True)
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Spent'], 'o-')
    plt.plot(dfBackground['Date'], dfBackground['Spent'], marker="", linestyle="") #invisible plot to get good x-axis
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
        'Date': [f'1.{year}', f'12.{year}'],
        'Spent': [0, 0]
    })

    # Start plot creation
    dfBackground['Date'] = pd.to_datetime(dfBackground['Date'],format="%m.%Y")
    df['Date'] = pd.to_datetime(df['Date'],format="%m.%Y")
    plt.figure(figsize=(12, 6)) 
    plt.plot(df['Date'], df['Spent'], 'o-')
    plt.plot(dfBackground['Date'], dfBackground['Spent'], marker="", linestyle="") #invisible plot to get good x-axis
    plt.xlabel('Month')
    plt.ylabel('Spent Money in €')
    plt.title(f"Spending Over Time in {year} per month")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)

    # Show the plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Month+".png")}", bbox_inches='tight')

def create_graph_Spent_per_Category_per_Month(year, market):
    df = pd.read_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month)}")
    df['Date'] = df['Date'].astype(int) #remove year
    df = df.pivot(index='Date', columns='Category', values='Spent')
    
    df.to_csv(f"{os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market, year + "_" + v.file_graph_Spent_per_Category_per_Month_pivoted)}")

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

    # Show the plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Category_per_Month+".png")}", bbox_inches='tight')

    ## create as stacked bars graphs
    plt.figure(figsize=(12, 6))    
    plotNumberCounter = 0
    edgeColor = [ "pink", "black", "red", "blue", "purple"] # edgecolor for better readability of graph
    selectedEdgeColor = 0
    bottom = np.zeros(12)
    fig, ax = plt.subplots()
    for category in df.columns:
        ax.bar(df.index, df[category], 0.5, label=category, bottom=bottom, edgecolor=edgeColor[selectedEdgeColor] )
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

    plt.figure(figsize=(12, 6))  # Adjust figure size as needed for better readability
    plt.plot(df['Category'], df['Spent'], marker='o', linestyle='-') # 'o' adds markers at each data point
    plt.xlabel('Category')
    plt.ylabel('Spent Money in €')
    plt.title(f"Spending Over Time in {year} per Category")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)

    # Show the plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, year+"_"+v.file_graph_Spent_per_Category_per_Year+".png")}", bbox_inches='tight')

def create_graph_Spent_per_Month_over_Years(market):
    """
    Shows the amount of money spent by concatenating the years that are available as data.

    Therefore no invisible background plot needed in this case.
    """
    dfs = []
    dir_csv_results_for_graphs = os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market)
    for filename in sorted(os.listdir(dir_csv_results_for_graphs), reverse=False):
        if v.file_graph_Spent_per_Month in filename:
            filepath = os.path.join(dir_csv_results_for_graphs, filename)
            df = pd.read_csv(filepath)
            df['Date'] = df['Date'].astype(str)
            df['Date'] = pd.to_datetime(df['Date'],format="%m.%Y")
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

    # Show the plot
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig(f"{os.path.join(v.dir_graph_images, market, v.file_graph_Spent_per_Month_over_Years+".png")}", bbox_inches='tight')


