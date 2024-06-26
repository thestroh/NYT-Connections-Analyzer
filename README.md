# NYT Connections Analyzer
_"Am I actually improving at the NYT Connections over time?"_

The NYT Connections became a part of my daily routine at the start of 2024, and while other NYT/daily games have some level of statistical result tracking, Connections seemed a bit bare in this regard. I began capturing screenshots of my results because it was a super quick way to log them, both on mobile and desktop, but wanted to automate the process of generating statistics from those screenshots. 

So I built this one weekend to provide an infographic-style display of my NYT Connection results over time, and also some high-level overviews of my results. 

**generate.py** -> Running this will generate an infographic, saved as 'infographic.png', using 'NYT_Connections' as the default folder/directory where the screenshots are stored. That direction can be declare in the create_infographic() function call if needed. 

**screenshot_processing** -> Uses cv2 to analyze the screenshots and find the results based on the colored rectangles in the image. It returns a json-style object containing the date of the game (which comes from the image filename, since screenshots can be easily setup to save with the current date/time), the result (won/lost), the amount of guesses, and the details of the individual guesses (either incorrect, or the color of the correct guess).

**calendar_draw **-> Handles the initial setup of the calendar drawing, which paints the results for all days where a Connections screenshot was found by filename. It follows the same color order as Connections, so yellow = perfect, green = 1 mistake, blue = 2 mistakes, purple = 3 mistakes, and red = failed. 

**stats_draw** -> Adds some simple summary statistics including total games played, longest win streak, average guesses (4 being the lowest, since you need 4 correct guesses to win), and the number of days missed. It also provides a small graphic showing the average guesses it took for each colored connection in the game, and then the amount of times each colored connection was solved first/second/third/fourth. 

Additionally, I included files from Google Fonts for the Roboto Font because I used it in the infographic generation since I didn't like Calibri or Tahoma as much. 

The outcome is an infographic similar to below (my results through June 9th, 2024). 
![Example](https://github.com/thestroh/NYT-Connections-Analyzer/assets/78974700/bc22853b-c603-4b2b-b8c9-a331bf2fdd1f)

At the end of all of this, it appears as though I have been improving! I've had only a single fail after early March, and very few non-perfect games. If I ever edit this to add more details, I think seeing the improvement of my purple-connection guesses over time would be helpful because I think that's really been the key to my improvement - early recognition and completion of the purple-connection. 
