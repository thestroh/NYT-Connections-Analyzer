from PIL import Image, ImageDraw
from datetime import datetime, timedelta


def draw_calendar(dict):
    # Open the template image for processing
    image = Image.open("infographic_template.png")
    draw = ImageDraw.Draw(image)

    # Set the fill value for transparent rectangles (skipped days)
    transparent_value = (0, 255, 0, 0)

    ### Image Setup ###
    # Set the starting location (1/1/2024)
    x = 19; y = 310
    # Set drawing constants
    square_length = 21
    square_offset = (square_length - 1)/2
    # Starting on Sunday in January, which isn't the first so just manually offset
    days_to_skip = 1
    # Padding between days in the same month (e.g. 1/2/24 - 1/1/24 x value)
    day_padding = 32
    # Padding between rows in the same month (e.g. 1/8/24 - 1/1/24 y value)
    week_padding = 30
    # Padding between months in the same row (e.g. 2/1/24 - 1/1/24 x value)
    month_padding = 258
    # Padding between months in different rows (e.g. 5/1/24 - 1/1/24 y value)
    row_height = 275
    # Set the initial days to skip for the current year (week starts on Sundays)
    initial_days_skipped = 1

    # Get all dates in current year to validate data
    expected_dates = get_expected_dates()

    # Loop through monthly data and set iterator
    i = 0
    x_space = 0
    for month, data_dict in dict.items():
        # Set the initial space in row/column for x,y
        y_space = 0

        # Check if new row is needed
        if month%5 == 0:
            # Reset x
            x = 19 
            # Update y
            y = 310 + ((month/5)*row_height)

        # Check if any days need to be skipped and move x cursor accordingly
        while initial_days_skipped > 0:
            x_space += 1
            initial_days_skipped -= 1

        # Next, loop daily result per month
        for index, data in data_dict.items():
            if str(data['Date']) == expected_dates[i]:

                # Check if we need a new row in current month
                if x_space%7 == 0 and x != 0:
                    y_space += 1
                    x_space = 0

                # Update x,y cursors in new variables
                xcurrent = x + (x_space * day_padding)
                ycurrent = y + (y_space * week_padding)

                # Get coordinates for bounds of square
                left, top, right, bottom = get_bounds(xcurrent, ycurrent, square_offset)

                # Draw the square using the value assigned for the guess count
                draw.rectangle([left, top, right, bottom], fill = guess_color(data['Result'], data['Guesses']))

                # Increment
                i += 1
                x_space += 1
            else:
                try:
                    # Check if the date exists at all first
                    index_value = expected_dates.index(str(data['Date']))

                    # Increment by the difference between the matching index and current iterated index
                    x_space += (index_value-i)
                    i = index_value

                    # Get coordinates for rectangle - could move this into a sub-function for better code clarity
                    xcurrent = x + (x_space * day_padding)
                    ycurrent = y + (y_space * week_padding)
                    left, top, right, bottom = get_bounds(xcurrent, ycurrent, square_offset)
                    draw.rectangle([left, top, right, bottom], fill = guess_color(data['Result'], data['Guesses']))

                    # Final increment for next cycle
                    i += 1
                    x_space += 1

                except ValueError:
                    print("Date error on index: ", i, "and date: ", str(data['Date']))
                    # Should I add something here to change the increment? Test later

        # Adjust x for the next column/month
        x = x + month_padding
        # Reset y_space
        y_space = 0
    
    image.save("infographic.png")


def get_bounds(x,y, square_offset):
    left = x - square_offset
    top = y - square_offset
    right = x + square_offset
    bottom = y + square_offset
    return left, top, right, bottom

def guess_color(result, guess_count):
    # Check for loss or victory
    if result == "Lost":
        return "red"
    
    guesses_to_colors = {
        4: "yellow",
        5: "green",
        6: "blue",
        7: "purple"
    }

    if guess_count in guesses_to_colors:
        return guesses_to_colors[guess_count]
    else:
        # Could return red here, but it really should never get here so using an outlier color
        return "pink"



def parse_date(date_str):
    return datetime.strptime(date_str, "%m/%d/%Y")

def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def get_expected_dates(start_date = datetime(datetime.now().year, 1, 1).strftime("%m/%d/%Y"), end_date = datetime.now().strftime("%m/%d/%Y")):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    expected_dates = [date.strftime("%Y-%m-%d") for date in date_range(start_date, end_date)]
    return expected_dates