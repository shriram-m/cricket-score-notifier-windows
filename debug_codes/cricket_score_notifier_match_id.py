###############################################################################
##  cricket_score_notifier.py
##=============================================================================
##  This script is used to notify cricket scores on Windows 10 machines based 
##  on custom notification settings. The live scores are fetched from ESPN 
##  Cricifo, from this URL: 'http://static.cricinfo.com/rss/livescores.xml'. 
##  prints the output in the console.
##  
##  Note: This script was developed and tested on Windows 10, Python v3.7.9.
##  
##=============================================================================
##  
##  Usage: (0) Install 'beautifulsoup4', 'plyer', and 'lxml' python modules 
##             using the below commands.
##                              pip install beautifulsoup4
##                              pip install plyer
##                              pip install lxml
##  
##         (1) Configure the application settings (Line #36 to Line #51).
##  
##         (2) Open a terminal in the same directory as this file and run the 
##             command:         python cricket_score_notifier.py
##  
##         (3) A list of current matches will be displayed with an index each.
##             Enter the match index that you want to follow for notifications.
##             Done! You can now enjoy the notifications...
##  
##=============================================================================
##  
## Author: Shriram M
## Version: 1.5.0
##  
###############################################################################
##########################    Application Settings    #########################
###############################################################################
#                             Notification settings                            
notify_after_every_inning = True
notify_after_every_wicket = True
notify_after_every_batter_milestone = True
notify_after_every_batting_team_milestone = True
notify_after_every_x_overs = False
# Numbers of overs 'X' after which notification will be given. This is 
# applicable only if 'notify_after_every_x_overs' is True
x_overs_to_notify = 5

#                                Other settings                                
# Time interval (in seconds) between polling for live scores
refresh_interval_sec = 5

# Time duration (in seconds) for which the notification would be displayed
notification_display_duration_sec = 2
###############################################################################
###############################################################################


###############################################################################
##########################         Main Program       #########################
###############################################################################
import requests
from bs4 import BeautifulSoup
from time import sleep
import sys
from plyer import notification

previous_score_string = ""
previous_runs_team = -1

previous_runs_batter1 = -1
previous_runs_batter2 = -1
previous_name_batter1 = ""
previous_name_batter2 = ""

previous_wickets = -1
previous_batting_team = ""
previous_overs = ""

match_url_template = "http://www.cricinfo.com/ci/engine/match/{match_id}.html"

batter_notification_dict = {}

while True:
    try:
        match_id = sys.argv[1]
        match_url = match_url_template.format(match_id=match_id)
        r = requests.get(match_url)
        soup = BeautifulSoup(r.text,"lxml") 
        score = soup.findAll("title")

        try:
            r.raise_for_status()
        except Exception as exc:
            print ("Connection Failure. Try again!")
            continue
        
        current_score_string = str(score[0].text)
        if current_score_string != previous_score_string:
            print(current_score_string + "\n")
            previous_score_string = current_score_string

            score_split = current_score_string.split(" ")
            runs = -1
            wickets = -1
            batting_team = ""
            for string in score_split:
                if "/" in string:
                    runs = int(string.split("/")[0].strip())
                    wickets = int(string.split("/")[1].strip())
                    batting_team = str(score_split[score_split.index(string) - 1]).strip()
                    break

            detailed_scores = (current_score_string[current_score_string.find("(")+1 : current_score_string.find(")")]).strip()
            detailed_scores_split = detailed_scores.split(",")
            overs = detailed_scores_split[0].split(" ")[0].strip()

            batter1_score = ""
            batter2_score = ""

            batter1_name = None
            batter2_name = None

            if detailed_scores.count(",") >= 2:
                batter1_score = detailed_scores_split[1].split(" ")[-1].strip()
                batter1_name = detailed_scores_split[1].replace(batter1_score, "").strip()
                batter1_score = batter1_score.replace("*", "")

            if detailed_scores.count(",") >= 3:
                batter2_score = detailed_scores_split[2].split(" ")[-1].strip()
                batter2_name = detailed_scores_split[2].replace(batter2_score, "").strip()
                batter2_score = batter2_score.replace("*", "")

            if previous_wickets == -1:
                previous_wickets = wickets
            
            if previous_runs_team == -1:
                previous_runs_team = runs

            if previous_batting_team == "":
                previous_batting_team = batting_team

            title = ""

            if "." not in overs:
                if overs != previous_overs:
                    previous_overs = overs
                    if notify_after_every_x_overs and int(previous_overs) % x_overs_to_notify == 0:
                        title = "After " + previous_overs + " overs..."
            elif ".6" in overs:
                if str(int(overs.replace(".6", "")) + 1) != previous_overs:
                    previous_overs = str(int(overs.replace(".6", "")) + 1)
                    if notify_after_every_x_overs and int(previous_overs) % x_overs_to_notify == 0:
                        title = "After " + previous_overs + " overs..."
            
            if runs != previous_runs_team:
                if notify_after_every_batting_team_milestone:
                    if runs % 50 == 0 and runs > 0:
                        title = batting_team + " " + str(runs) + " !!"
                previous_runs_team = runs

            if notify_after_every_batter_milestone:
                if len(batter1_score) > 0 and int(batter1_score) % 50 == 0 and int(batter1_score) > 0:
                    if not(batter1_name in batter_notification_dict and batter_notification_dict[batter1_name]):
                        batter_notification_dict[batter1_name] = True
                        title = batter1_name + " " + batter1_score + " !!"
                elif batter1_name is not None:
                    batter_notification_dict[batter1_name] = False

                if len(batter2_score) > 0 and int(batter2_score) % 50 == 0 and int(batter2_score) > 0:
                    if not(batter2_name in batter_notification_dict and batter_notification_dict[batter2_name]):
                        batter_notification_dict[batter2_name] = True
                        title = batter2_name + " " + batter2_score + " !!"
                elif batter2_name is not None:
                    batter_notification_dict[batter2_name] = False

            if wickets != previous_wickets:
                if notify_after_every_wicket: 
                    if wickets > previous_wickets:
                        title = "Wicket !!"
                    elif wickets < previous_wickets: # wicket column decreases if a wicket has been revoked
                        title = "Wicket Revoked !!"
                previous_wickets = wickets

            if previous_batting_team != batting_team:
                previous_batting_team = batting_team
                if notify_after_every_inning:
                    title = "New Innings !!"

            if len(title) > 0:
                notification.notify(
                    title=title,
                    message=current_score_string,
                    app_name="Live Cricket Score",
                    timeout=notification_display_duration_sec
                )

                # Wait a little longer when wicket has fallen to avoid artefacts
                if title == "Wicket !!":
                    sleep(2 * refresh_interval_sec)


    except requests.exceptions.ConnectionError:
        pass

    except requests.exceptions.TooManyRedirects:
        pass

    sleep(refresh_interval_sec)
