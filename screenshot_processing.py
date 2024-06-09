import cv2
import numpy as np
import re

def find_rectangles(image_path, diags=False):
    """
    Reads an image to find the rectangles representing NYT Connection Results.
    @param image_path: The path for the image to analyze.
    @pamar diags: True or False, toggles display showing the rectangles found and requires manual input. Not recommended for batch runs, defaults to False.
    """
    # Validate diags argument
    if diags not in [True, False]:
        raise ValueError("diags argument must be either True or False (leave blank to default to False)")

    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert to grayscale and apply blurring
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive thresholding to handle uneven lighting
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    # Initialize lists to store rectangles and their colors
    rectangles = []
    rectangles_with_colors = []

    # Loop over contours
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01 * peri, True) # can modify value if needed

        ##  Optional visualization of polygons pre-filtering
        if diags:
            clone = image.copy()
            cv2.drawContours(clone, [approx], -1, (0, 255, 0), 2)
            cv2.imshow("Approximated Polygon", clone)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Filter based on points to limit to rectangles
        if cv2.isContourConvex(approx) and len(approx) == 4:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(approx)
      
            for i in range(4):
                rectangles.append((int(x + ((w * i)/4)), y, int(w/4), h))

    # Get the ROI of rectangles and return the RGB value
    for (x, y, w, h) in rectangles:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Extract region of interest
        roi = rgb_image[y:y+h, x:x+w]

        # Calculate average RGB values
        avg_r = np.average(roi[:,:,0])
        avg_g = np.average(roi[:,:,1])
        avg_b = np.average(roi[:,:,2])

        avg_color = (int(avg_r), int(avg_g), int(avg_b))
        avg_color_name = color_categorizer(avg_color)

        #rectangles_with_colors.append((x, y, w, h, avg_color_name))
        rectangles_with_colors.append((avg_color_name))

    # Image is read bottom-up, reverse for chronological order
    rectangles_with_colors.reverse()
    # Each guess/attempt has exactly 4 values - break up results by guess
    rectangles_with_colors = [rectangles_with_colors[i:i+4] for i in range(0, len(rectangles_with_colors), 4)]

    guess_data = {}
    for index, guess in enumerate(rectangles_with_colors, start=1):
        # Check if every color in the guess is identical (a correct guess)
        if len(set(guess)) == 1:
            # If so, set the value equal to the color of the correct guess
            guess_data[index] = guess[0].capitalize()
        else:
            # If not add an outlier value to indicate a failed guess
            guess_data[index] = 'Incorrect'

    # Required colors that must be present for a "won" game
    required_colors = {"Blue", "Green", "Yellow", "Purple"}

    # Check if the game was won or lost by seeing if there's a correct guess for every color
    if all(color in guess_data.values() for color in required_colors):
        result = "Won"
    else:
        result = "Lost"

    # Use regular expressions to extract date from image_path - looking for YYYY-MM-DD
    date_pattern = r"\b\d{4}-\d{2}-\d{2}\b"
    match = re.search(date_pattern, image_path)

    if match:
        # Use date in json object if it's available
        image_date = match.group(0)
    else:
        # Fine to still run without a date, just use outlier value to highlight issue
        image_date = "9999-99-99"

    json_object = {
        'Date': image_date,
        'Result': result,
        'Guesses': len(guess_data),
        'Data': guess_data
    }

    # Optionally show the image with identified rectangles
    if diags:
        cv2.imshow("Image", image)
        cv2.waitKey(0)

    return json_object

def color_categorizer(color, color_thresholds = 0):
    """
    Categorizes a color based on its RGB values.
    @param color: A tuple of RGB values.
    @pamar color_thresholds: A dictionary of color names and their threshold RGB values in the structure of {"name": (R_l, G_l, B_l), (R_u, G_u, B_u)}
    """
    # Set default color threshold values based on NYT Connections colors
    if color_thresholds == 0:
        # default NYT connections color values
        # green = (160,195,90)
        # yellow = (249,223,109)
        # blue = (176,196,239)
        # purple = (186,129,197)
        color_thresholds = {
            "green": ((140, 180, 70), (180, 210, 110)),
            "yellow": ((230, 200, 80), (255, 230, 130)),
            "blue": ((150, 170, 220), (185, 205, 250)),
            "purple": ((170, 110, 180), (195, 140, 210)),
        }
    
    # Loop through our thresholds to see if testing color is within range of any
    for color_name, thresholds in color_thresholds.items():
        lower, upper = thresholds
        if all(lower[i] <= color[i] <= upper[i] for i in range(3)):
            return color_name
    # Return outlier value if no RGB value is matched
    return "UNKNOWN COLOR"