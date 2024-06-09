from PIL import Image, ImageDraw, ImageFont
from calendar_draw import *
from screenshot_processing import *
import os; from os import listdir
from datetime import datetime
from collections import defaultdict

def draw_infographics(dict):
    # Process dictionary to get all desired data
    total_games, longest_streak, streak_start_date, streak_end_date, average_attempts, missed_games = get_aggregate_data(dict)
    average_guesses = get_average_positions(dict)

    image = Image.open("infographic.png")
    draw = ImageDraw.Draw(image)

    font_size = 25
    font_color = (202,202,202)
    font = ImageFont.truetype("Roboto-Regular.ttf", font_size)

    # Coordinates for stats are hard-coded
    draw.text((154,1215), str(total_games), fill=font_color, font=font)
    draw.text((447,1215), str(longest_streak), fill=font_color, font=font)
    draw.text((720,1215), str(average_attempts), fill=font_color, font=font)
    draw.text((942,1215), str(missed_games), fill=font_color, font=font)

    avg_square_x = 160
    label_delta = 25
    avg_square_y = 1300
    avg_square_y_delta = 50
    label_y_offset = 14
    square_length = 21
    square_offset = (square_length - 1)/2

    # Values for relative placement per color
    relative_count_delta = 150
    relative_count_x = avg_square_x + relative_count_delta
    relative_count_y = avg_square_y

    colors = ["Yellow", "Green", "Blue", "Purple"]
    # Collect relative guess data
    relative_color_data = {}
    for color in colors:
        relative_color_data[color] = get_color_stats(dict, color)
    
    for index, color in enumerate(colors):
        # Get bounds and draw rectangle
        left, top, right, bottom = get_bounds(avg_square_x, avg_square_y, square_offset)
        draw.rectangle([left, top, right, bottom], fill = color)
        # Get the value for the average guess for that color and draw it
        value = average_guesses.get(color)
        draw.text((avg_square_x + label_delta, avg_square_y - label_y_offset), str(value), fill=font_color, font=font)

        # Draw larger rectangles to reference the color for relative guess rates
        draw.rectangle([left + ((index+1) * relative_count_delta), 
                        relative_count_y - (square_offset), 
                        right + ((index+1) * relative_count_delta), 
                        relative_count_y + (3 * avg_square_y_delta) + square_offset], 
                        fill = color)
        
        # Store the color data for just the color we're looping through
        color_stats = relative_color_data[color]
        for i in range(4):
            # Draw the first, second, third, and last relative guess counts
            draw.text((relative_count_x + label_delta, relative_count_y - label_y_offset + (i * avg_square_y_delta)), 
                      str(color_stats[list(color_stats.keys())[i]]),
                      fill = font_color, font = font)
            
        relative_count_x += relative_count_delta
        avg_square_y += avg_square_y_delta

    image.save("infographic.png")
    image.show()


def get_aggregate_data(dict):
    """
    Takes an output dictionary containing NYT Connections data and returns aggregate data. Specifically returns the following variables:
    total_games: The total amount of Connections games played.
    longest_streak: The longest amount of wins in a row.
    streak_start_date, streak_end_date: The start and end date of the longest winning streak.
    average_attempts: The average number of guesses across all games, wins and losses.
    missed_games: The number of missed games in the current year.
    @param dict: A dictionary of NYT Connections data in the proper format as returned by XYZ Function.
    """
    # Missed games is total days in current year - number of games played
    days_passed = datetime.now().timetuple().tm_yday
    total_games = sum(len(sub_dict) for sub_dict in dict.values())

    # Setup variables for keeping track of win streak, associated dates, and guesses
    current_streak = 0
    longest_streak = 0
    streak_start_date = None
    streak_end_date = None
    guess_total = 0

    # First level is just indexes
    for sub_dict in dict.values():
        # Second level has actual game data
        for game_dict in sub_dict.values():
            result = game_dict.get("Result")
            date = game_dict.get("Date")
            guess_total += game_dict.get("Guesses")

            if result == "Won":
                # If new streak is beginning, set streak start date
                if current_streak == 0:
                    streak_start_date = date

                # Update streak and check if current streak is longer than stored max streak
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
                streak_end_date = date

            else:
                # Reset streak data
                current_streak = 0
                streak_start_date = None

    # Calculate composite data
    average_attempts = round(guess_total/total_games, 1)
    missed_games = days_passed-total_games
    return total_games, longest_streak, streak_start_date, streak_end_date, average_attempts, missed_games

def get_average_positions(dict):
    """
    Returns the average position for each color/difficulty.
    @param dict: A dictionary of NYT Connections data in the proper format as returned by XYZ Function.
    """

    total_guesses = {"Blue": 0, "Yellow": 0, "Green": 0, "Purple": 0}
    color_counts = {"Blue": 0, "Yellow": 0, "Green": 0, "Purple": 0}

    for sub_dict in dict.values():
        for game_dict in sub_dict.values():
            guess_dict = game_dict.get("Data")

            for guess_number, color in guess_dict.items():
                if color != "Incorrect":
                    total_guesses[color] += guess_number
                    color_counts[color] += 1

    average_guesses = {color: round(total_guesses[color] / color_counts[color], 1) if color_counts != 0 else 0 for color in total_guesses}
    return average_guesses

def get_color_stats(dict, selected_color):
    """
    Returns the count of relative placements for purple (the most difficult) connections.
    @param dict: A dictionary of NYT Connections data in the proper format as returned by XYZ Function.
    @param color: A color value, either "Blue", "Yellow", "Green", or "Purple", for which to analyze.
    """

    colors = ["Yellow", "Green", "Blue", "Purple"]
    if selected_color not in colors:
        print("Please select a valid NYT Connections color, options are Yellow, Green, Blue, and Purple.")
        print("Also check capitalization")
        return

    position_mapping = {1: "First", 2: "Second", 3: "Third"} # Using clarified names instead of index
    relative_positions = {"First": 0, "Second": 0, "Third": 0, "Last": 0}

    for sub_dict in dict.values():
        for game_dict in sub_dict.values():
            guess_dict = game_dict.get("Data")
            color_position = None
            colors_found = 0

            for color in guess_dict.values():
                if color in colors:
                    colors_found += 1
                    if color == selected_color:
                        color_position = colors_found
                        break
            
            if color_position is not None:
                relative_position = position_mapping.get(color_position, "Last")
                relative_positions[relative_position] += 1

    return relative_positions

def get_relative_date_stats(dict, selected_color):
    """
    Returns the relative placement of a color per date.
    @param dict: A dictionary of NYT Connections data in the proper format as returned by XYZ Function.
    @param color: A color value, either "Blue", "Yellow", "Green", or "Purple", for which to analyze.
    """

    colors = ["Yellow", "Green", "Blue", "Purple"]
    if selected_color not in colors:
        print("Please select a valid NYT Connections color, options are Yellow, Green, Blue, and Purple.")
        print("Also check capitalization")
        return

    date_positions = {}

    for sub_dict in dict.values():
        for game_dict in sub_dict.values():
            date = game_dict['Date']
            guess_dict = game_dict.get("Data")
            color_position = None
            colors_found = 0

            for color in guess_dict.values():
                if color in colors:
                    colors_found += 1
                    if color == selected_color:
                        color_position = colors_found
                        break
            
            if color_position is not None:
                date_positions[date] = color_position

    return date_positions