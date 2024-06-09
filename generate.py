from screenshot_processing import *
from calendar_draw import *
from stats_draw import *
import os; from os import listdir
from datetime import datetime
from collections import defaultdict

def create_infographic(folder_path = "NYT_Connections"):
    # Create the initial collection dictionary
    connections_data = {}

    # Loop through folder, analyzing each image and adding the data to the dictionary
    for index, image in enumerate(os.listdir(folder_path)):
        data = find_rectangles(os.path.join(folder_path, image))
        connections_data = {**connections_data, index+1: data}

    # Construct new dictionary which breaks data down by month for easier processing
    monthly_connections_data = defaultdict(dict)
    # Finish constructing the dictionary
    for index, data in connections_data.items():
        date_str = data['Date']
        date = datetime.strptime(date_str, '%Y-%m-%d')
        month = date.month
        monthly_connections_data[month][index] = data

    # Call infographic processing libraries
    # Calendar drawing comes first, otherwise image saving doesn't work properly
    draw_calendar(monthly_connections_data)
    draw_infographics(monthly_connections_data)

create_infographic()