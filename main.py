from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headerdoneschedule = False
header = []
elements = []

allmonths = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                "november", "december"]

# get specific year and month
year = input("What year? Enter with this format. (ex: 2022):    ")
numMonths = input("Does your range of dates have multiple calendar months in them? 'y' for yes and 'n' for no:    ")
if numMonths == 'y':
    numMonths = 2
elif numMonths == 'n':
    numMonths = 1
else:
    raise AttributeError
count = 0
months = []
while count < numMonths:
    months.append(input("What is/are the starting and ending month(s)? Enter one at a time, in the ORDER you want,"
                        " with no capital letter. (ex: november):    "))
    count += 1
indexes = []
for month in months:
    indexes.append(allmonths.index(month))
if numMonths != 1:
    ranges = indexes[1] - indexes[0]
    # if the range is negative than that means that the range goes into the new year
    if ranges < 0:
        ranges += 13
    else:
        ranges += 1
else:
    ranges = 1
days = []
print("What is the start and finish date?")
print("ex:\n14\n16\nWhich could mean from March 14th to April 16th")

for i in range(0, 2):
    days.append(input("Enter one a time:  "))

# search link with the data
link = "https://www.basketball-reference.com/leagues/NBA_" + year + "_standings.html"
# installs local chromes supported driver
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(link)
    driver.execute_script("document.getElementsByClassName('tooltip')[2].click()")
# if the expanded standings have not been made for this year yet then do the year prior
except:
    link = "https://www.basketball-reference.com/leagues/NBA_" + str(int(year) - 1) +"_standings.html"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(link)
    driver.execute_script("document.getElementsByClassName('tooltip')[2].click()")

try:
    # grab the csv, without the beginning strings that are not related to the data
    datateams = str(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "csv_expanded_standings"))
    ).text).replace("--- When using SR data, please cite us and provide a link and/or a mention.\n\n\n \n,,,Place,"
                    "Place,Conference,Conference,Division,Division,Division,Division,Division,Division,All-Star,"
                    "All-Star,Margin,Margin,Month,Month,Month,Month,Month,Month,Month\nRk,Team,Overall,Home,Road,"
                    "E,W,A,C,SE,NW,P,SW,Pre,Post,≤3,≥10,Oct,Nov,Dec,Jan,Feb,Mar,Apr\n", "")
    datateamrows = datateams.split("\n")
    teamnames = []
    # grabs all the team names in the NBA into a list
    for i in range(0, len(datateamrows)):
        temp = []
        temp.append(0)
        temp.append(datateamrows[i].split(",")[1])
        teamnames.append(temp)
finally:
    driver.close()

for i in range(0, ranges):
    link = "https://www.basketball-reference.com/leagues/NBA_" + year + "_games-" + allmonths[(indexes[0] + i)%12] + ".html"
    # installs local chromes supported driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # opens link
    driver.get(link)

    # finds specific button that changes the table to a csv format
    driver.execute_script("document.getElementsByClassName('tooltip')[2].click()")

    # wait until the format is completely loaded
    try:
        # grab the csv, without the beginning strings that are not related to the data
        data = str(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "csv_schedule"))
        ).text).replace("--- When using SR data, please cite us and provide a link and/or a mention.\n\n\n \n", "")
        # split every new line into a item in a list
        datarows = data.split("\n")
        # if the header has been made, remove it
        if headerdoneschedule:
            datarows = datarows[1:len(datarows)]
        # setting up values for our loop
        for row in datarows:
            # checking if the header has been made yet
            if not headerdoneschedule:
                # since it hasn't split the row into smaller items separated by a comma
                header = row.split(",")
                headerdoneschedule = True
            else:
                elements.append(row.split(","))
    finally:
        driver.close()

# translate the months to their smaller parts to match the same format as the one's in the list
monthdict = {"january": "Jan",
             "february": "Feb",
             "march": "Mar",
             "april": "Apr",
             "may": "May",
             "june": "Jun",
             "july": "Jul",
             "august": "Aug",
             "september": "Sep",
             "october": "Oct",
             "november": "Nov",
             "december": "Dec"}
# this list will keep track of every team name that appears in the range given
rangelist = []
# same date format as in the data
start = monthdict[months[0]] + " " + days[0]
foundrange = False
if len(months) == 1:
    end = monthdict[months[0]] + " " + days[1]
else:
    end = monthdict[months[1]] + " " + days[1]

for element in elements:
    # once the start range is found than let the program know it can start adding the names to a list
    if any(start in string for string in element):
        foundrange = True
    # if it's the last day then end the range
    if any(end in string for string in element):
        foundrange = False
    # if the loop is still in the range or on the last day
    if foundrange or any(end in string for string in element):
        # add the NBA team names to the list
        rangelist.append(element[2])
        rangelist.append(element[4])
print()
print("-------- LIST OF TEAM'S GAMES IN ORDER FROM THE RANGE GIVEN -----")
print()
print(rangelist)
# list of all the NBA team names, including a counter for each to keep track of how many games they played in the range
for teamcount in teamnames:
    # grabs the current team in the range
    for currentteam in rangelist:
        # if the current team name in the list of the NBA team matches the one in the range, then increment the
        # number of games played by 1
        if teamcount[1] == currentteam:
            # and remove the current team instance from the list
            rangelist.remove(teamcount[1])
            teamcount[0] = teamcount[0] + 1

teamnames.sort(key=lambda x: x[0], reverse=True)
print()
print("----- AMOUNT OF GAMES PLAYED PER TEAM IN THE RANGE GIVEN -----")
print()
for teamresult in teamnames:
    print(teamresult[1] + ": " + str(teamresult[0]))
