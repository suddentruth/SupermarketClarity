
import os
import sys
import Scripts.script_values as v
import datetime as dt

def remove_directory(dir_name):
    """Removes a directory if it exists and returns True on success, False otherwise."""
    remove_files(dir_name)
    try:
        if os.path.exists(dir_name):
            os.removedirs(dir_name)
            print(f"Directory '{dir_name}' removed.")
            return True
        else:
            print(f"Directory '{dir_name}' did not exist.")
            return False
    except OSError as e:  # Catch potential errors during directory creation
        print(f"Error removing directory '{dir_name}': {e}")
        return False
    
def remove_files(dir_name):
    """Removes files in a directory if they exist and returns True on success, False otherwise."""
    try:
        if os.path.exists(dir_name):
            dir_list = os.listdir(dir_name)
            filtered_list = list(filter(lambda file: not file.startswith("."), dir_list))
            for file in filtered_list:
                if os.path.isfile(os.path.join(dir_name,file)):
                    if v.file_complete_items_categories in file:
                        newDestination = dt.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")+" "+str(file)
                        os.rename(os.path.join(dir_name,file), newDestination)
                        print(f"file {file} renamed and moved to {newDestination}.")
                    else:
                        os.remove(os.path.join(dir_name,file))
                        print(f"file '{file}' in dir {dir_name} removed.")           
            return True
        else:
            print(f"Directory '{dir_name}' did not exist.")
            return False
    except Exception as e:
        print(f"Error removing files in directory '{dir_name}': {e}")
        return False

if __name__ == "__main__":
    if input(f"{v.BLUE}Are you sure you want to delete a lot of files? (y/n){v.RESET}") != "y":
        exit()

    if len(sys.argv) == 0:
        sys.exit(f"{v.RED}Provide name of one supported market:{v.RESET}\n{v.BLUE}{v.markets.values()}{v.RESET}.")
    

    if len(sys.argv) > 1:
        try:
            market = sys.argv[1]
            print(f"Received second argument for supermarket: {v.BLUE}{market}{v.RESET}")
            if market not in v.markets:
                sys.exit(f"{v.RED}Market must be supported. Check following list:{v.RESET}\n{v.BLUE}{v.markets.values()}{v.RESET}")
            remove_directory(os.path.join(v.dir_your_receipts, market))
            remove_directory(os.path.join(v.dir_data, v.dir_CSV_extracts, market))
            remove_directory(os.path.join(v.dir_data, v.dir_CSV_results, market))
            remove_directory(os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, market))
            remove_directory(os.path.join(v.dir_data, v.dir_CSV_results, v.dir_for_graphs, v.dir_for_categories, market))
            remove_directory(os.path.join(v.dir_graph_images, market))
        except:
            sys.exit(f"{v.RED}Error: First argument must be a valid supermarket name. Check following list:{v.RESET}\n{v.BLUE}{v.markets.values()}{v.RESET}")
   

    print(f"{v.GREEN}done{v.RESET}")

