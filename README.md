# Playoff Fantasy Hockey Pool

## Introduction

Fantasy hockey is one of my favorite past times but my friends and I alwasy felt constrained by the uninteresting playoff formats offered by the traditional websites. For the 2019/2020 playoffs I decided to take things into my own hands and build a dashboard in Google Sheets that would encompass all the specific nuances we wanted. The results were very positive except for one small detail: **I was manually entering all the stats**. This was both very time consuming on my part and it also failed to satiate the need my friends had for instant updates.

Fast forward 9 months and armed with a shiny new Data Science Diploma I decided to address the data entry issues by pulling the data from an API, manipulating that data, then pushing it to the Dashboard with Python. The results are a very accessible dashboard with stats that automatically updates the player stats within 3 minutes of the live event and requires minimal in-season maintenance. I've decided to share this project so others can host their own playoff fantasy hockey pool with the ,in my humble opinion, best format avaialble. 

## Intended Format

The dashboard is optimized for pools of 12 people but it can easily be managed for any number less than that. I would not recommend having more people than that just because you'll run out of interesting and relevant players to draft but it technically could be expanded if you are willing to reverse engineer the Google Sheet formulas.

Teams will consist of a total of 20 players each. Each team must draft 1 player from each team participating in the NHL playoffs making up the first 16 players with the 4 remaining spots open to any player on any other team. The mandatory one-per-playoff-team rule guarentees that teams will have active players remaining through the entirety of the playoffs while the 4 extra spots allow room for draft strategy and rewards the teams who make the right decisions.

Scoring is based on cumulative points to keep it easy and casual but it could easily be expanded to encompass any stat and scoring combination you might want. The team with teh most points at the end of the playoffs wins.

#### Note:
The restrictions on player selection (one-per-playoff-team) is not hardcoded in any way and can be completely ignored if that is what you'd prefer. 20 players per team is the maximum the dashboard is designed for but anything less than that will work perfectly fine. Changing the scoring to something more complex and sophisticated will require a decent amount of changes in both the python scripts and the dashboard.

There is also no draft support in this project so you'll have to organize that within your own group. I will typically add every player from every playoff team to the dashboard in the 'Players' tab and draft from there.

## Requirements

* An updated version of python and the relevant packages outlined in the project: https://www.python.org/downloads/
* A MySportsFeed personal account with an API key including the STATS addon: https://www.mysportsfeeds.com/
  * This service requires you to request access on a personal level and then to upgrade it to the frequency you want and add the STATS addon. My set up is running at a cost of $36 for 3 months of service at ~1 minute update interval.
* A Google Drive with Google Backup and Sync downloaded on your local machine: https://www.google.com/intl/en_ca/drive/ / https://www.google.com/intl/en_ca/drive/download/
* The willingness to do a relatively small amount of manual entry and reformatting.

## Implementation
### File set up and System configuration
1. Download this repository into the working directory of your choice
2. Sync your Google Drive and working directory
3. Open the FantasyHockeyPoolDashboard.xlsx in Google Sheets 
4. Add the code from the dashboardUpdate.txt to the Google Sheets Script Editor
  * Tools -> Script Editor -> Replace everything with the code from the dashboardUpdate.txt file
5. In the script editor add a Trigger to run the dashboardUpdate at the time interval you'd like
  * Clock icon on left bar of script editor -> Add Trigger
6. Create an environment variable containing you API authentication key and name it "fantasyPoolApiKey"
  * Windows users: https://www.youtube.com/watch?v=IolxqkL7cD8
  * Mac / Linux: https://www.youtube.com/watch?v=5iWhQWVXosU

### Dashboard Setup 
1. Add the owner names for each team in the top left of each team "box" on the 'Teams' tab
2. Add the owner names on the team rank table in the 'Stats' tab
  * Match the names with the colours from the 'Players' tab
  * Clear the data that is currently there for days 1 - 10 (just the coloured cells, not the grey ones)
3. Populate the teams with the players that they drafted on the 'Teams' tab under the 'Player' header for each team
4. Populate dashboard with all the teams that made the playoffs in the Team Data box on the 'Teams' tab
5. Protect all the sheets **except team names** from anyone but you (this did not persist through the upload and download of the repository)
  * We use protection and sharing with editing privilages opposed to just sharing with view only so the owners can change thier team name at will on the 'Team Names' tab
  * right click each tab -> protect sheet -> set permissions -> restrict who can edit this range: Only you -> done
6. Share the dashboard with those in your league with editor access
7. Once playoff games begin follow the "Maintenance" section below

## Maintenance

There are somethings that have not been automated and require daily to weekly attention. I will outline those things in this section and give some reasoning behind them not being automated.

##### Daily:
* Once games begin for the day run the apiPullFantasyHockeyPool.py in your terminal.
  * open your terminal -> navigate to your working directory -> type: python apiPullFantasyHockeyPool.py -> press enter
  * to stop the script from running use: ctrl+c
  * this script will pull new data from the api, format it, and output it to a .csv every 1 minute
  * Reasoning: The script needs to be manually turned on/off

* Once the games have finished for the day stop the previous script and run eodApiPullFantasyHockeyPool.py
  * open your terminal -> navigate to your working directory -> type: python eodApiPullFantasyHockeyPool.py
  * this script will grab the final day's data from the api, format it, and output it to a .csv one time
  * Reasoning: The script needs to be manually turned on/off

* Once the games have finished for the day record the end of day ranks on the Stats tab of the dashboard
  * today's rank will automatically update so it's value (ctrl+shft+v) just needs to be pasted to the next empty space for each owner
  * the day # will automatically populate and the Rank by Day graph will as well
  * Reasoning: I didn't feel like it was worth learning as much of the weird Google Script Editor language as I would need to automate this just to save 30 seconds per day.

#### End of Playoff Round
* When a team is eliminated place a marker under the 'Alive?' header of the Team Data box on the 'Teams' tab
  * I like to use a skull emoji 
  * Reasoning: Automating this would likely be super complicated and not worth the time
  * Real Reasoning: It's super satisfying to fade the eliminated teams and I want that

* When a playoff round is completed copy the formula (right-click -> paste special -> paste formula only) from Round 1 of the Round Point Totals box into the next empty cell to the right (column K for round 2, column M for round 3, column O for round 4)
  * Also copy the values (ctrl+shft+v) from round 1 and paste them over top of themselves to save the round 1 point totals.
  * The difference between the last and current rounds will be calculated to show total points per round
  * Rank Throughout the Playoffs Graph will update
  * Reasoning: End of playoff round is not something that's intuitevely avaialble from the api that we have

## Additional Notes
* The ranks and some other features will likely be broken until every team has played a game. Do not panic in the first few days of the playoffs
* Players do not get included until they play a game. If a player is drafted who is hurt their team and points will be blank (not 0) until they play a game.
* I have left all the players and team names from my testing populated so you have an idea of what it'll look like
* List of things you should be touching on the 'Teams' and 'Stats' tabs, everything else I would leave alone unless you are very familiar with Google Sheet formulas:
  *  Owner Names in the team boxes only, everywhere is connected to them (ex: B2, H2, R25, etc etc)
  *  Player names under the player header in the team boxes. Team, Alive?, and Points autofill
  *  Team and Alive? header in the Team Data box
  *  Ranks for each owner in the colourful section on the 'Stats' tab

## Contact
If you have any questions please feel free to reach out and I'll be happy to answer them or help out if needed:
LinkedIn: https://www.linkedin.com/in/jordanfortney/
GitHub: https://github.com/JordanFortney
Gmail: jordanseanearlfortney@gmail.com
