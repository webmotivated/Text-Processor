import os
import sys
import pandas

# ---Files---
# Unzip contents into the same directory

# ---Pandas module installation [Windows] ---
# 1. Install Python. (Opt for 'Add Python to PATH' during installation)
# 2. In Command Prompt type in the command: pip install manager
# 3. Once finished, type the following: pip install pandas . Wait for the downloads to be over and once it is done you will be able to run Pandas inside your Python programs on Windows.


# Open test_input.txt file saved in the same directory as the integrity_score.py file
# Prep and parse data as table (dataframe)
# Do necessary cleanups and conversions
with open(os.path.join(sys.path[0], "test_input.txt"), "r") as f:
    data = pandas.read_csv(f, sep=",", header=None, index_col=None)
    data.columns = ['Date', 'User', 'Type', 'Device', 'Words', 'Stars']
    df = pandas.DataFrame(data=data, columns = data.columns) #create dataframe
    df.Words = df.Words.str.replace('words','') 
    df.Date = df.Date.str.replace('nd','')
    df.Date = df.Date.str.replace('th','')
    df.Words = pandas.to_numeric(df.Words)
    df.Date = pandas.to_datetime(df.Date, errors='coerce', format='%d %B %H:%M') # Recognise date
    df['SCount'] = df['Stars'].str.len() # Stars into numeric 
    df['MA'] = df.expanding(min_periods=1)['SCount'].mean() #Adds a column with moving average (stars)
    df['DU'] = df.duplicated(subset='Device', keep = 'first') # Adds a column with boolean duplication check. ‘first’ - considers first value as unique and rest of the same values as duplicate.
    # print (df)
    
       

# Integrity score calc

score = 100
for i, row in df.iterrows():
                
    # hour_knock. knock 20 points if review comes through in the same hour
    if i==0 : hour_knock=0 # only check from 2nd line onwards (note: 1st line's i = 0)
    elif df.Date[i].month == df.Date[i-1].month and df.Date[i].day == df.Date[i-1].day and df.Date[i].hour == df.Date[i-1].hour and df.Date[i].minute != df.Date[i-1].minute: hour_knock=-20
    else: hour_knock=0

    # minute_knock. knock 40 points if review comes through in the same minute
    if i==0 : minute_knock=0 # only check from 2nd line onwards (note: 1st line's i = 0)
    elif df.Date[i].month == df.Date[i-1].month and df.Date[i].day == df.Date[i-1].day and df.Date[i].hour == df.Date[i-1].hour and df.Date[i].minute == df.Date[i-1].minute :
        minute_knock=-40
        hour_knock=0 
    else: minute_knock=0

    # words_knock. Genuine reviewers tend to say less - knock 0.5 points off for each review that contains more than 100 words.
    if df.Words[i] > 100: words_knock=-0.5   
    else: words_knock=0

    # stars_knock. Non-genuine reviews are likely to have a five star rating take 2% points off the integrity score for each review that has 5 stars
    if df.SCount[i] == 5: stars_knock=-2   
    else: stars_knock=0

    # MA_knock. Quadruple the penalty if the average is under 3.5 stars.
    if df.MA[i] < 3.5: MA_knock=-8   
    else: MA_knock=0

    # Same_device. If we are seeing multiple reviews coming from the same device knock points off each time.
    if df.DU[i] == True: same_device = -30   
    else: same_device = 0

    # Solicited_premium. If the review was left by someone who was invited by the professional then add 3% points to the integrity score.
    if df.Type[i] == "solicited": solicited_premium = 3   
    else: solicited_premium = 0

    # Calculate score         
    adjscore = score + words_knock + hour_knock + minute_knock + stars_knock + MA_knock + same_device + solicited_premium
    score = adjscore
    if score >100: score =100
    
    # Report integrity score
    # Report any rows with any NaN values.
    if df.isnull().loc[i,:].sum()>0: print ("Could not read review summary data") #if any NaN found in row 
    elif score >70: print ("Info:Jon has a trusted review score of" ,score)
    elif score <70 and score >50: print ("Warning:Jon has a trusted review score of" ,score)
    elif score <50: print ("Alert:Jon has been de-activated due to a low trusted review score")

    

    

    


