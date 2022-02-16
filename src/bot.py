#!/usr/bin/env python3

'''IMPORT'''

import bot_config
import collections
import datetime
import io
import matplotlib
import matplotlib.pyplot as plt
import numpy
import operator
import os
import random
import re
import telebot
import threading
import time
import schedule

from GoogleNews import GoogleNews
from PIL import Image
from selenium import webdriver

'''INITIALIZATION'''

googlenews = GoogleNews()

'''BOT'''

bot = telebot.TeleBot(bot_config.BotToken)

'''FUNCTIONS DEFINITION'''

def empty_leave_lunch():

    global LeaveLunchUsers

    try:

        LeaveLunchUsers

    except NameError:

        LeaveLunchUsers = list() #initialize LeaveLunchUsers list

    LeaveLunchUsers.clear() #clear LeaveLunchUsers list

def find_directory_path():

    name = bot_config.CommsGTFDir
    path = os.path.abspath(os.sep) #system-independent root directory str ('/' for Linux and 'C:\\' for Windows)

    for root, dirs, _ in os.walk(path):

        if name in dirs:

            return os.path.join(root, name)

def lunch_ban_reminder():

    ScheduledLunchBanReminderHourMin       = time.strptime(bot_config.ScheduledLunchBanReminderTime,'%H:%M') #get hour and minute from ScheduledLunchBanReminderTime
    ScheduledLunchBanReminderCombinedTime  = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ScheduledLunchBanReminderHourMin.tm_hour,ScheduledLunchBanReminderHourMin.tm_min)) #combine today's date and hour and minute from ScheduledLunchBanReminderTime
    ScheduledLunchBanReminderTimeStamp     = datetime.datetime.timestamp(ScheduledLunchBanReminderCombinedTime) #get combined ScheduledLunchBanReminderTime timestamp
    ScheduledLunchPollStartingHourMin      = time.strptime(bot_config.ScheduledLunchPollStartingTime,'%H:%M') #get hour and minute from ScheduledLunchPollStartingTime
    ScheduledLunchPollStartingCombinedTime = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ScheduledLunchPollStartingHourMin.tm_hour,ScheduledLunchPollStartingHourMin.tm_min)) #combine today's date and hour and minute from ScheduledLunchPollStartingTime
    ScheduledLunchPollStartingTimeStamp    = datetime.datetime.timestamp(ScheduledLunchPollStartingCombinedTime) #get combined ScheduledLunchPollStartingTime timestamp

    bot.send_message(bot_config.CommsGTFID,"There are only <b>{} minutes</b> left before today's lunch poll starts. Please, ban those hours when you won't be able to attend by typing /lunch_ban".format(int(ScheduledLunchPollStartingTimeStamp-ScheduledLunchBanReminderTimeStamp)//60),parse_mode='HTML') #send /lunch_ban reminder about minutes left prior to scheduled lunch poll

def lunch_poll_check():

    global AlreadyVoted
    global LunchPollEndingTime
    global LunchPollStartingTime
    global LunchPollVotes
    global NonScheduledLunchPollFlag
    global ScheduledLunchPollFlag

    try:

        AlreadyVoted

    except NameError:

        AlreadyVoted = dict() #initialize AlreadyVoted dictionary

    try:

        LunchPollEndingTime

    except NameError:

        LunchPollEndingTime = 0  #initialize LunchPollEndingTime

    try:

        LunchPollStartingTime

    except NameError:

        LunchPollStartingTime = 0 #initialize LunchPollStartingTime

    try:

        LunchPollVotes

    except NameError:

        LunchPollVotes = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions))) #initialize LunchPollVotes dictionary

    try:

        NonScheduledLunchPollFlag

    except NameError:

        NonScheduledLunchPollFlag = False #initialize NonScheduledLunchPollFlag

    try:

        ScheduledLunchPollFlag

    except NameError:

        ScheduledLunchPollFlag = False #initialize ScheduledLunchPollFlag

    if int(time.time()) > LunchPollEndingTime: #if lunch poll has ended

        if ScheduledLunchPollFlag == True:

            ScheduledLunchPollFlag = False

        elif NonScheduledLunchPollFlag == True:

            NonScheduledLunchPollFlag = False

        if sum(LunchPollVotes.values()) > 0: #if someone has voted

            lunch_poll_result() #show lunch poll result

            del AlreadyVoted
            del LunchPollEndingTime
            del LunchPollStartingTime
            del LunchPollVotes

def lunch_poll_reminder():

    global ScheduledLunchPollFlag

    try:

        ScheduledLunchPollFlag

    except NameError:

        ScheduledLunchPollFlag = False #initialize ScheduledLunchPollFlag

    if ScheduledLunchPollFlag == True: #if there is a scheduled lunch poll going on

        ScheduledLunchPollReminderHourMin      = time.strptime(bot_config.ScheduledLunchPollReminderTime,'%H:%M') #get hour and minute from ScheduledLunchPollReminderTime
        ScheduledLunchPollReminderCombinedTime = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ScheduledLunchPollReminderHourMin.tm_hour,ScheduledLunchPollReminderHourMin.tm_min)) #combine today's date and hour and minute from ScheduledLunchPollReminderTime
        ScheduledLunchPollReminderTimeStamp    = datetime.datetime.timestamp(ScheduledLunchPollReminderCombinedTime) #get combined ScheduledLunchPollReminderTime timestamp
        ScheduledLunchPollEndingHourMin        = time.strptime(bot_config.ScheduledLunchPollEndingTime,'%H:%M') #get hour and minute from ScheduledLunchPollEndingTime
        ScheduledLunchPollEndingCombinedTime   = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ScheduledLunchPollEndingHourMin.tm_hour,ScheduledLunchPollEndingHourMin.tm_min)) #combine today's date and hour and minute from ScheduledLunchPollEndingTime
        ScheduledLunchPollEndingTimeStamp      = datetime.datetime.timestamp(ScheduledLunchPollEndingCombinedTime) #get combined ScheduledLunchPollEndingTime timestamp

        bot.send_message(bot_config.CommsGTFID,"There are only <b>{} minutes</b> left before today's lunch poll ends. Hurry up and vote!".format(int(ScheduledLunchPollEndingTimeStamp-ScheduledLunchPollReminderTimeStamp)//60),parse_mode="HTML") #send voting reminder about minutes left prior to scheduled lunch poll ending

def lunch_poll_result():

    global LunchHistory
    global LunchPollChatID
    global LunchPollVotes

    try:

        LunchHistory

    except NameError:

        LunchHistory = dict() #initialize LunchHistory dictionary

    try:

        LunchPollChatID

    except NameError:

        LunchPollChatID = bot_config.CommsGTFID #initialize LunchPollChatID

    try:

        LunchPollVotes

    except NameError:

        LunchPollVotes = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions))) #initialize LunchPollVotes dictionary

    LunchPollVotesResult = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions))) #initialize LunchPollVotesResult dictionary
    LunchPollVotesResult.update(LunchPollVotes.items()) #update LunchPollVotesResult with LunchPollVotes
    VotedHour = {hour:LunchPollVotesResult[hour] for hour in LunchPollVotesResult if LunchPollVotesResult[hour]!=0} #dict containing the hours that have been voted for
    SelectedLunchTime = max(VotedHour, key=VotedHour.get) #earliest most voted hour

    Data               = (LunchPollVotesResult.values())
    DataLength         = len(bot_config.LunchPollOptions) #length of data vector (number of different lunch time hours)
    YTicksPos          = numpy.arange(DataLength) #y ticks location as an array
    Fig                = plt.figure() #figure object
    LunchTimeResultBar = plt.barh(YTicksPos, Data) #horizontal bars plot
    Ax                 = LunchTimeResultBar[0].axes #axes object
    Lim                = Ax.get_xlim()+Ax.get_ylim() #axes limit

    for bar in LunchTimeResultBar:

        bar.set_zorder(1)
        bar.set_facecolor('none')
        x, y = bar.get_xy() #bar data
        w, h = bar.get_width(), bar.get_height() #bar size
        Grad = numpy.atleast_2d(numpy.linspace(0,1*w/max(Data),256)) #color gradient
        Ax.imshow(Grad, extent=[x,x+w,y,y+h], aspect="auto", zorder=0, norm=matplotlib.colors.NoNorm(vmin=0,vmax=1)) #apply color gradient into bar

    Ax.axis(Lim) #limit the axis
    plt.title("Lunch Time Results") #figure title
    plt.xlabel("Selected lunch time: {}".format(SelectedLunchTime)) #set x axis label
    plt.xticks(numpy.arange(max(Data)+1),fontsize=5) #figure x ticks
    plt.yticks(YTicksPos, bot_config.LunchPollOptions, fontsize=5) #figure y ticks (lunch time hours)

    buffer = io.BytesIO() #binary buffer
    Fig.savefig(buffer) #save figure in buffer
    buffer.seek(0) #starting position of the buffer

    bot.send_photo(LunchPollChatID,photo=buffer) #send figure as photo
    bot.send_message(LunchPollChatID,"The lunch poll ended. We are eating at *{}* today!".format(SelectedLunchTime),parse_mode='Markdown') #send ending message
    LunchHistory[datetime.datetime.now()] = SelectedLunchTime #lunch history update with selected lunch time

def reset_lunch_ban():

    global ActiveLunchPollOptions

    ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

def reset_scheduled_lunch_poll():

    global ScheduledLunchPollFlag

    ScheduledLunchPollFlag = False

def run_threaded(job_func):

    threading.Thread(target=job_func).start()

def scheduled_jobs_run():

    while True:

        schedule.run_pending()
        time.sleep(1)

def scheduled_lunch_poll():

    global ActiveLunchPollOptions
    global LunchPollEndingTime
    global LunchPollStartingTime
    global ScheduledLunchPollFlag

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    try:

        LunchPollEndingTime

    except NameError:

        LunchPollEndingTime = 0  #initialize LunchPollEndingTime

    try:

        LunchPollStartingTime

    except NameError:

        LunchPollStartingTime = 0 #initialize LunchPollStartingTime

    try:

        ScheduledLunchPollFlag

    except NameError:

        ScheduledLunchPollFlag = False #initialize ScheduledLunchPollFlag

    if ActiveLunchPollOptions: #if ActiveLunchPollOptions is not empty

        ScheduledLunchPollFlag = True

        MarkUp = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True) #create keyboard object

        for hour in ActiveLunchPollOptions:

            MarkUp.add(telebot.types.KeyboardButton(hour)) #add button object to keyboard object

        buffer = open(find_directory_path()+"/Images/Random/Sodexo.jpg",'rb') #binary buffer
        buffer.seek(0) #starting position of the buffer

        bot.send_photo(bot_config.CommsGTFID,buffer) #send image

        bot.send_message(bot_config.CommsGTFID,bot_config.LunchPollText,reply_markup=MarkUp) #send keyboard to all users

        LunchPollStartingTime           = int(time.time()) #define poll starting time
        ScheduledLunchPollEndingHourMin = time.strptime(bot_config.ScheduledLunchPollEndingTime,'%H:%M')
        ScheduledCombinedTime           = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ScheduledLunchPollEndingHourMin.tm_hour,ScheduledLunchPollEndingHourMin.tm_min))
        LunchPollEndingTime             = datetime.datetime.timestamp(ScheduledCombinedTime)

'''COMMANDS'''
# ETHICS_COMPLIANCE COMMAND

@bot.message_handler(commands=[bot_config.EthicsComplianceCommand]) #Trigger: /ethics_compliance
def ethics_comliance_command(message): #/ethics_compliance function

    EthicsComplianceSelectedFolder = random.choice(bot_config.EthicsComplianceFolders)

    buffer = open(find_directory_path()+bot_config.EthicsCompliancePath+EthicsComplianceSelectedFolder+'/'+EthicsComplianceSelectedFolder+' feliz.jpg','rb') #binary buffer
    buffer.seek(0) #starting position of the buffer

    bot.send_photo(message.chat.id,buffer) #send image

    time.sleep(10)

    buffer = open(find_directory_path()+bot_config.EthicsCompliancePath+EthicsComplianceSelectedFolder+'/'+EthicsComplianceSelectedFolder+' triste.jpg','rb') #binary buffer
    buffer.seek(0) #starting position of the buffer

    bot.send_photo(message.chat.id,buffer) #send image

# HELP COMMAND

@bot.message_handler(commands=[bot_config.HelpCommand]) #Trigger: /help
def help_command(message): #/help function

    bot.send_message(message.chat.id,'112') #send /help message

# JOIN_LUNCH COMMAND

@bot.message_handler(commands=[bot_config.JoinLunchCommand]) #Trigger: /join_lunch
def join_lunch_command(message): #/join_lunch function

    global ActiveLunchPollOptions
    global LeaveLunchUsers

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    try:

        LeaveLunchUsers

    except NameError:

        LeaveLunchUsers = list()

    MaxActiveLunchPollHourMin = time.strptime(ActiveLunchPollOptions[-1],'%H:%M')
    MaxActiveCombinedTime     = datetime.datetime.combine(datetime.datetime.now(),datetime.time(MaxActiveLunchPollHourMin.tm_hour,MaxActiveLunchPollHourMin.tm_min))
    MaxActiveLunchPollTime    = int(datetime.datetime.timestamp(MaxActiveCombinedTime)) #first active lunch hour option (earliest hour)

    if datetime.datetime.weekday(datetime.datetime.now()) < 5: #if it is Monday, Tuesday, Wednesday, Thursday or Friday

        if message.date < MaxActiveLunchPollTime:

            if message.from_user.id in LeaveLunchUsers:

                LeaveLunchUsers.remove(message.from_user.id)
                bot.reply_to(message, "{} is ashamed and decided to return...  Welcome back!".format(message.from_user.first_name))

            else:

                bot.reply_to(message, "You are already into today's lunch! Please, type /leave_lunch if you don't want to be count on")

        else:

            if datetime.datetime.weekday(datetime.datetime.now()) < 4: #if it is Monday, Tuesday, Wednesday or Thursday

                bot.reply_to(message,"Today's lunch is over! You will be in automatically for tomorrow's lunch...")

            else:

                bot.reply_to(message,"Please, get a life and forget me during the weekend...")

    else:

        if datetime.datetime.weekday(datetime.datetime.now()) == 6: #if it is Sunday

            bot.reply_to(message,"You will be in automatically for tomorrow's lunch...")

        else:

            bot.reply_to(message,"Please, get a life and forget me during the weekend...")

# LEAVE_LUNCH COMMAND

@bot.message_handler(commands=[bot_config.LeaveLunchCommand]) #Trigger: /leave_lunch
def leave_lunch_command(message): #/leave_lunch function

    global ActiveLunchPollOptions
    global AlreadyBanned
    global AlreadyVoted
    global LeaveLunchUsers
    global LunchPollVotes

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    try:

        AlreadyBanned

    except NameError:

        AlreadyBanned = dict()

    try:

        AlreadyVoted

    except NameError:

        AlreadyVoted = dict()

    try:

        LeaveLunchUsers

    except NameError:

        LeaveLunchUsers = list()

    try:

        LunchPollVotes

    except NameError:

        LunchPollVotes = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions)))

    MaxActiveLunchPollHourMin = time.strptime(ActiveLunchPollOptions[-1],'%H:%M')
    MaxActiveCombinedTime     = datetime.datetime.combine(datetime.datetime.now(),datetime.time(MaxActiveLunchPollHourMin.tm_hour,MaxActiveLunchPollHourMin.tm_min))
    MaxActiveLunchPollTime    = int(datetime.datetime.timestamp(MaxActiveCombinedTime)) #first active lunch hour option (earliest hour)

    if datetime.datetime.weekday(datetime.datetime.now()) < 5: #if it is Monday, Tuesday, Wednesday, Thursday or Friday

        if message.date < MaxActiveLunchPollTime:

            if message.from_user.id not in LeaveLunchUsers: #if user hasn't left lunch

                LeaveLunchUsers.append(message.from_user.id) #append user to leavers list

                if message.from_user.id in AlreadyBanned: #if user has banned hours

                    if isinstance(AlreadyBanned[message.from_user.id],list): #if the user banned a list of hours

                        ActiveLunchPollOptions.extend(list(hour for hour in AlreadyBanned[message.from_user.id])) #extend hours list

                    else:

                        ActiveLunchPollOptions.append(AlreadyBanned[message.from_user.id]) #append single hour

                    NowDatetime = datetime.datetime.now()

                    for i in range(len(ActiveLunchPollOptions)):

                        ActiveLunchPollHourMin    = time.strptime(ActiveLunchPollOptions[i],'%H:%M')
                        ActiveLunchPollOptions[i] = datetime.datetime.combine(NowDatetime,datetime.time(ActiveLunchPollHourMin.tm_hour,ActiveLunchPollHourMin.tm_min))

                    ActiveLunchPollOptions = sorted(list(set(ActiveLunchPollOptions)))

                    for i in range(len(ActiveLunchPollOptions)):

                        ActiveLunchPollOptions[i] = ActiveLunchPollOptions[i].strftime('%H:%M')

                    del AlreadyBanned[message.from_user.id] #delete user from banners list
                    bot.reply_to(message, "The hours you banned were reactivated...")

                if message.from_user.id in AlreadyVoted: #if user has voted

                    LunchPollVotes[AlreadyVoted[message.from_user.id]] -= 1 #remove vote
                    del AlreadyVoted[message.from_user.id] #delete user from voters list
                    bot.reply_to(message, "Your vote was erased from the current lunch poll...")

                bot.reply_to(message, "{} is not coming to lunch today! What an astonishing lack of commitment...".format(message.from_user.first_name))

            else:

                bot.reply_to(message, "You are already out of today's lunch! Please, add yourself again by typing /join_lunch")

        else:

            if datetime.datetime.weekday(datetime.datetime.now()) < 4: #if it is Monday, Tuesday, Wednesday or Thursday

                bot.reply_to(message,"Today's lunch is over! You must wait until tomorrow for leaving...")

            else:

                bot.reply_to(message,"Please, get a life and forget me during the weekend...")

    else:

        if datetime.datetime.weekday(datetime.datetime.now()) == 6: #if it is Sunday

            bot.reply_to(message,"You must wait until tomorrow for leaving...")

        else:

            bot.reply_to(message,"Please, get a life and forget me during the weekend...")

# LUNCH_ACTIVE COMMAND

@bot.message_handler(commands=[bot_config.LunchActiveCommand]) #Trigger: /lunch_active
def lunch_active_command(message): #/lunch_active function

    global ActiveLunchPollOptions

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    if datetime.datetime.weekday(datetime.datetime.now()) < 5: #if it is Monday, Tuesday, Wednesday, Thursday or Friday

        if ActiveLunchPollOptions: #if ActiveLunchPollOptions is not empty

            bot.reply_to(message,"*Active lunch hours:*\n{}".format(', '.join(sorted(list(ActiveLunchPollOptions)))),parse_mode='Markdown')

        else:

            if datetime.datetime.weekday(datetime.datetime.now()) < 4: #if it is Monday, Tuesday, Wednesday or Thursday

                bot.reply_to(message, "All hours have been already banned...")

            else:

                bot.reply_to(message,"Please, get a life and forget me during the weekend...")

    else:

        bot.reply_to(message,"Please, get a life and forget me during the weekend...")

# LUNCH_BAN COMMAND

@bot.message_handler(commands=[bot_config.LunchBanCommand]) #Trigger: /lunch_ban
def lunch_ban_command(message): #/lunch_ban function

    global ActiveLunchPollOptions
    global LeaveLunchUsers
    global NonScheduledLunchPollFlag
    global ScheduledLunchPollFlag

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    try:

        LeaveLunchUsers

    except NameError:

        LeaveLunchUsers = list()

    try:

        NonScheduledLunchPollFlag

    except NameError:

        NonScheduledLunchPollFlag = False

    try:

        ScheduledLunchPollFlag

    except NameError:

        ScheduledLunchPollFlag = False

    MaxActiveLunchPollHourMin = time.strptime(ActiveLunchPollOptions[-1],'%H:%M')
    MaxActiveCombinedTime     = datetime.datetime.combine(datetime.datetime.now(),datetime.time(MaxActiveLunchPollHourMin.tm_hour,MaxActiveLunchPollHourMin.tm_min))
    MaxActiveLunchPollTime    = int(datetime.datetime.timestamp(MaxActiveCombinedTime))

    if message.from_user.id not in LeaveLunchUsers:

        if datetime.datetime.weekday(datetime.datetime.now()) < 5: #if it is Monday, Tuesday, Wednesday, Thursday or Friday

            if message.date < MaxActiveLunchPollTime:

                if (NonScheduledLunchPollFlag == True) or (ScheduledLunchPollFlag == True):

                    bot.reply_to(message,"There is a lunch poll going on! Please, wait until it finishes")

                else:

                    bot.reply_to(message,bot_config.LunchBanText1)

            else:

                if datetime.datetime.weekday(datetime.datetime.now()) < 4: #if it is Monday, Tuesday, Wednesday or Thursday

                    bot.reply_to(message,"Today's lunch is over! You must wait until tomorrow for banning hours...")

                else:

                    bot.reply_to(message,"Please, get a life and forget me during the weekend...")

        else:

            if datetime.datetime.weekday(datetime.datetime.now()) == 6: #if it is Sunday

                bot.reply_to(message,"You must wait until tomorrow for banning hours...")

            else:

                bot.reply_to(message,"Please, get a life and forget me during the weekend...")

    else:

        bot.reply_to(message,"You are already out of today's lunch! Please, add yourself again by typing /join_lunch")

@bot.message_handler(regexp=bot_config.LunchBanRegexp1,func=lambda message: ((hasattr(message.reply_to_message,'text') is True) and (message.reply_to_message.text == bot_config.LunchBanText1) and (message.reply_to_message.from_user.id == bot_config.BotID))) #Trigger: reply to /lunch_ban initial text and bot ID
def reply_to_lunch_ban_command(message):

    global ActiveLunchPollOptions
    global AlreadyBanned

    try:

        AlreadyBanned

    except NameError:

        AlreadyBanned = dict()

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    AuxLunchPollOptions = bot_config.LunchPollOptions.copy()
    ToBanList           = re.findall(bot_config.LunchBanRegexp1,message.text) #create a list of hours from the reply

    AlreadyBannedList = list()

    for i in range(len(AlreadyBanned)):

        if isinstance(list(AlreadyBanned.values())[i],list): #if the i-th ban is a list

            AlreadyBannedList.extend(list(hour for hour in list(A.values())[i])) #extend hours list

        else:

            AlreadyBannedList.append(hour) #append single hour

    for i in range(len(AlreadyBannedList)):

        AlreadyBannedHourMin = time.strptime(AlreadyBannedList[i],'%H:%M')
        AlreadyBannedList[i] = datetime.datetime.combine(NowDatetime,datetime.time(AlreadyBannedHourMin.tm_hour,AlreadyBannedHourMin.tm_min))

    AlreadyBannedList = sorted(list(set(AlreadyBannedList)))

    for i in range(len(AlreadyBannedList)):

        AlreadyBannedList[i] = AlreadyBannedList[i].strftime('%H:%M')

    InvalidList = list()

    if re.search('-',message.text) is not None: #if there is a time interval in the reply

        IntervalList      = re.findall(bot_config.LunchBanRegexp2,message.text) #list of intervals
        IntervalHourList  = list()
        IntervalHourList.extend((hour1,hour2) for (hour1,_,hour2) in IntervalList)

        for i in range(len(AuxLunchPollOptions)):

            AuxLunchPollOptionsStrHourMin = time.strptime(AuxLunchPollOptions[i],'%H:%M')
            AuxLunchPollOptions[i]        = datetime.datetime.combine(datetime.datetime.now(),datetime.time(AuxLunchPollOptionsStrHourMin.tm_hour,AuxLunchPollOptionsStrHourMin.tm_min))

        AuxLunchPollOptions = sorted(AuxLunchPollOptions)

        for i in range(len(ActiveLunchPollOptions)):

            ActiveLunchPollOptionsStrHourMin = time.strptime(ActiveLunchPollOptions[i],'%H:%M')
            ActiveLunchPollOptions[i]        = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ActiveLunchPollOptionsStrHourMin.tm_hour,ActiveLunchPollOptionsStrHourMin.tm_min))

        ActiveLunchPollOptions = sorted(ActiveLunchPollOptions)

        for i in range(len(ToBanList)):

            ToBanListStrHourMin = time.strptime(ToBanList[i],'%H:%M')
            ToBanList[i]        = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ToBanListStrHourMin.tm_hour,ToBanListStrHourMin.tm_min))

        ToBanList = sorted(ToBanList)

        for (FromStr,ToStr) in IntervalHourList:

            FromStrHourMin = time.strptime(FromStr,'%H:%M')
            FromHour       = datetime.datetime.combine(datetime.datetime.now(),datetime.time(FromStrHourMin.tm_hour,FromStrHourMin.tm_min))
            ToStrHourMin   = time.strptime(ToStr,'%H:%M')
            ToHour         = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ToStrHourMin.tm_hour,ToStrHourMin.tm_min))

            if FromHour > ToHour: #if interval hours are not [min, max]

                FromHour, ToHour = ToHour, FromHour #switch hours

            try:

                FromHourIndex = int(ActiveLunchPollOptions.index(FromHour)) #find index of from hour
                ToHourIndex   = int(ActiveLunchPollOptions.index(ToHour)) #find index of to hour

                ToBanList.extend(ActiveLunchPollOptions[FromHourIndex:ToHourIndex])

            except ValueError:

                try:

                    FromHourIndex = int(AuxLunchPollOptions.index(FromHour)) #find index of from hour

                except ValueError:

                    if FromHour < AuxLunchPollOptions[0]: #if from hour is out of range

                        FromHourIndex = 0

                    elif FromHour > AuxLunchPollOptions[-1]: #if from hour is out of range

                        FromHourIndex = -1

                try:

                    ToHourIndex = int(AuxLunchPollOptions.index(ToHour)) #find index of to hour

                except ValueError:

                    if ToHour < AuxLunchPollOptions[0]: #if to hour is out of range

                        ToHourIndex = 0

                    elif ToHour > AuxLunchPollOptions[-1]: #if to hour is out of range

                        ToHourIndex = -1

                try:

                    ToBanList.extend(AuxLunchPollOptions[FromHourIndex:ToHourIndex])

                except:

                    pass

        for i in range(len(ActiveLunchPollOptions)):

            ActiveLunchPollOptions[i] = ActiveLunchPollOptions[i].strftime('%H:%M')

        ToBanList = sorted(list(set(ToBanList)))

        for i in range(len(ToBanList)):

            ToBanList[i] = ToBanList[i].strftime('%H:%M')

        for hour in ToBanList:

            if hour in ActiveLunchPollOptions:

                ActiveLunchPollOptions.remove(hour)

            elif hour not in AlreadyBannedList:

                InvalidList.append(hour)

        AlreadyBanned[message.from_user.id] = sorted(list(set(ToBanList)-set(AlreadyBannedList)-set(InvalidList)))
        InvalidList                         = sorted(InvalidList)

        if len(AlreadyBanned[message.from_user.id]) == 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText3.format(', '.join(AlreadyBanned[message.from_user.id]),'has'))

        elif len(AlreadyBanned[message.from_user.id]) > 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText3.format(', '.join(AlreadyBanned[message.from_user.id]),'have'))

        if len(AlreadyBannedList) == 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText4.format(', '.join(AlreadyBannedList),'has'))

        elif len(AlreadyBannedList) > 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText4.format(', '.join(AlreadyBannedList),'have'))

        if len(InvalidList) == 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText5.format(', '.join(InvalidList),'is'))

        elif len(InvalidList) > 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText5.format(', '.join(InvalidList),'are'))

    elif re.search(bot_config.LunchBanRegexp1,message.text) is not None: #if there is an hour (H:M) in the reply (but no time interval)

        for hour in ToBanList:

            if hour in ActiveLunchPollOptions:

                ActiveLunchPollOptions.remove(hour) #remove item from list

            elif hour not in AlreadyBannedList:

                InvalidList.append(hour)

        AlreadyBanned[message.from_user.id] = sorted(list(set(ToBanList)-set(AlreadyBannedList)-set(InvalidList)))
        InvalidList                         = sorted(InvalidList)

        if len(AlreadyBanned[message.from_user.id]) == 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText3.format(', '.join(AlreadyBanned[message.from_user.id]),'has'))

        elif len(AlreadyBanned[message.from_user.id]) > 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText3.format(', '.join(AlreadyBanned[message.from_user.id]),'have'))

        if len(AlreadyBannedList) == 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText4.format(', '.join(AlreadyBannedList),'has'))

        elif len(AlreadyBannedList) > 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText4.format(', '.join(AlreadyBannedList),'have'))

        if len(InvalidList) == 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText5.format(', '.join(InvalidList),'is'))

        elif len(InvalidList) > 1:

            bot.send_message(message.chat.id,bot_config.LunchBanText5.format(', '.join(InvalidList),'are'))

    else:

        if re.findall(bot_config.LunchPollRegexp, message.text): #if trying to ban an invalid hour

            bot.reply_to(message,"You are only allowed to ban the following hours:\n\n{}".format(', '.join(sorted(ActiveLunchPollOptions))))

        else:

            bot.reply_to(message,bot_config.LunchBanText2)

# LUNCH_POLL COMMAND

@bot.message_handler(commands=[bot_config.LunchPollCommand]) #Trigger: /lunch_poll
def lunch_poll_command(message): #/lunch_poll function

    global ActiveLunchPollOptions
    global LeaveLunchUsers
    global LunchPollEndingTime
    global LunchPollStartingTime
    global NonScheduledLunchPollFlag
    global ScheduledLunchPollFlag

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    try:

        LeaveLunchUsers

    except NameError:

        LeaveLunchUsers = list()

    try:

        LunchPollEndingTime

    except NameError:

        LunchPollEndingTime = 0  #initialize LunchPollEndingTime

    try:

        LunchPollStartingTime

    except NameError:

        LunchPollStartingTime = 0 #initialize LunchPollStartingTime

    try:

        NonScheduledLunchPollFlag

    except NameError:

        NonScheduledLunchPollFlag = False

    try:

        ScheduledLunchPollFlag

    except NameError:

        ScheduledLunchPollFlag = False

    if datetime.datetime.weekday(datetime.datetime.now()) < 5: #if it is Monday, Tuesday, Wednesday, Thursday or Friday

        if ActiveLunchPollOptions: #if ActiveLunchPollOptions is not empty

            MaxActiveLunchPollHourMin = time.strptime(ActiveLunchPollOptions[-1],'%H:%M')
            MaxActiveCombinedTime     = datetime.datetime.combine(datetime.datetime.now(),datetime.time(MaxActiveLunchPollHourMin.tm_hour,MaxActiveLunchPollHourMin.tm_min))
            MaxActiveLunchPollTime    = int(datetime.datetime.timestamp(MaxActiveCombinedTime)) #first active lunch hour option (earliest hour)

            if int(datetime.datetime.now().timestamp()) < MaxActiveLunchPollTime: #if max lunch poll hour hasn't already passed

                if (ScheduledLunchPollFlag == False) and (NonScheduledLunchPollFlag == False): #if there isn't a poll going on

                    if message.from_user.id not in LeaveLunchUsers: #if the voter hasn't '/leave_lunch' today

                        MarkUp = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True) #create keyboard object

                        ActiveLunchOptionsFlag = False

                        for hour in ActiveLunchPollOptions.copy():

                            ActiveLunchPollHourMin = time.strptime(hour,'%H:%M')
                            ActiveCombinedTime     = datetime.datetime.combine(datetime.datetime.now(),datetime.time(ActiveLunchPollHourMin.tm_hour,ActiveLunchPollHourMin.tm_min))
                            ActiveLunchPollTime    = int(datetime.datetime.timestamp(ActiveCombinedTime))

                            if ActiveLunchOptionsFlag == False:

                                if message.date > ActiveLunchPollTime:

                                    ActiveLunchPollOptions.remove(hour)

                                else:

                                    MarkUp.add(telebot.types.KeyboardButton(hour)) #add button object to keyboard object

                                    ActiveLunchOptionsFlag = True

                            else:

                                MarkUp.add(telebot.types.KeyboardButton(hour)) #add button object to keyboard object

                        buffer = open(find_directory_path()+"/Images/Random/Sodexo.jpg",'rb') #binary buffer
                        buffer.seek(0) #starting position of the buffer

                        bot.send_photo(message.chat.id,buffer) #send image

                        bot.send_message(message.chat.id,bot_config.LunchPollText,reply_markup=MarkUp) #send keyboard to all users

                        LunchPollStartingTime              = message.date #define poll start time
                        NonScheduledLunchPollEndingTime1   = LunchPollStartingTime + (bot_config.LunchPollTimeout*60) #default lunch poll ending time (min)
                        NonScheduledLunchPollEndingHourMin = time.strptime(ActiveLunchPollOptions[0],'%H:%M')
                        NonScheduledCombinedTime           = datetime.datetime.combine(datetime.datetime.now(),datetime.time(NonScheduledLunchPollEndingHourMin.tm_hour,NonScheduledLunchPollEndingHourMin.tm_min))
                        NonScheduledLunchPollEndingTime2   = int(datetime.datetime.timestamp(NonScheduledCombinedTime)) #first active lunch hour option (earliest hour)

                        if abs(NonScheduledLunchPollEndingTime1-NonScheduledLunchPollEndingTime2) < (bot_config.LunchPollTimeout*60):

                            if NonScheduledLunchPollEndingTime1 > NonScheduledLunchPollEndingTime2: #if the lunch poll default ending time is later than the first active lunch hour option (earliest hour)

                                LunchPollEndingTime = NonScheduledLunchPollEndingTime2

                            else:

                                LunchPollEndingTime = NonScheduledLunchPollEndingTime1

                        else:

                            LunchPollEndingTime = NonScheduledLunchPollEndingTime1

                        NonScheduledLunchPollFlag = True

                    else:

                        bot.reply_to(message, "You are already out of today's lunch! Please, add yourself again by typing /join_lunch")

                else:

                    bot.reply_to(message, "There is already a lunch poll going on! Please, vote for an hour by replying to the latest _{}_ message".format(bot_config.LunchPollText),parse_mode='Markdown')

            else:

                bot.reply_to(message, "You will have to wait until tomorrow for voting...")

        else:

            bot.reply_to(message, "All hours have been already banned...")

    else:

        bot.reply_to(message,"Please, get a life and forget me during the weekend...")

# LUNCH_STATS COMMAND

@bot.message_handler(commands=[bot_config.LunchStatsCommand]) #Trigger: /lunch_stats
def lunch_stats_command(message): #/lunch_stats function

    global LunchHistory

    try: #test if there has been a poll before

        # Lunch Time Histogram

        LunchHistory      = dict(sorted(LunchHistory.items(),key=operator.itemgetter(0),reverse=True)) #descending sorting by time
        LunchHistogram    = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions)))
        AuxLunchHistogram = collections.Counter(LunchHistory.values())
        LunchHistogram.update(AuxLunchHistogram.items())

        Data              = (LunchHistogram.values())
        DataLength        = len(bot_config.LunchPollOptions) #length of data vector (number of different lunch time hours)
        YTicksPos         = numpy.arange(DataLength) #y ticks location as an array
        Fig               = plt.figure() #figure object
        LunchHistogramBar = plt.barh(YTicksPos, Data) #horizontal bars plot
        Ax                = LunchHistogramBar[0].axes #axes object
        Lim               = Ax.get_xlim()+Ax.get_ylim() #axes limit

        for bar in LunchHistogramBar:

            bar.set_zorder(1)
            bar.set_facecolor('none')
            x, y = bar.get_xy() #bar data
            w, h = bar.get_width(), bar.get_height() #bar size
            Grad = numpy.atleast_2d(numpy.linspace(0,1*w/max(Data),256)) #color gradient
            Ax.imshow(Grad, extent=[x,x+w,y,y+h], aspect="auto", zorder=0, norm=matplotlib.colors.NoNorm(vmin=0,vmax=1)) #apply color gradient into bar

        MaxPercentage = round((max(Data)/sum(Data))*100)
        Ax.axis(Lim) #limit the axis
        plt.title("Lunch Time Histogram") #figure title
        plt.xlabel("Most recurrent lunch time [%{}]: {}".format(MaxPercentage,max(LunchHistogram.items(), key=operator.itemgetter(1))[0])) #set x axis label
        plt.xticks((0,max(Data)),('0%','{}%'.format(MaxPercentage),2),fontsize=5) #figure x ticks (%)
        plt.yticks(YTicksPos, bot_config.LunchPollOptions, fontsize=5) #figure y ticks (lunch time hours)

        buffer = io.BytesIO() #binary buffer
        Fig.savefig(buffer) #save figure in buffer
        buffer.seek(0) #starting position of the buffer

        bot.send_photo(message.chat.id,photo=buffer) #send figure as photo

        # Lunch Time Histogram (months)

        for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']:

            LunchHistogramMonth    = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions)))
            AuxLunchHistogramMonth = dict()

            for key in LunchHistory.keys():

                if month == key.strftime('%B'): #if the month of the key (datetime) corresponds to the month in iteration

                    AuxLunchHistogramMonth[key] = LunchHistory[key]

            if not AuxLunchHistogramMonth: #if there isn't history about the month in iteration

                continue

            AuxLunchHistogramMonth = collections.Counter(LunchHistory.values())
            LunchHistogramMonth.update(AuxLunchHistogramMonth.items())

            Data                   = (LunchHistogramMonth.values())
            DataLength             = len(LunchHistogramMonth) #length of data vector (number of different months)
            YTicksPos              = numpy.arange(DataLength) #y ticks location as an array
            Fig                    = plt.figure() #figure object
            LunchHistogramMonthBar = plt.barh(YTicksPos, Data) #horizontal bars plot
            Ax                     = LunchHistogramMonthBar[0].axes #axes object
            Lim                    = Ax.get_xlim()+Ax.get_ylim() #axes limit

            for bar in LunchHistogramMonthBar:

                bar.set_zorder(1)
                bar.set_facecolor('none')
                x, y = bar.get_xy() #bar data
                w, h = bar.get_width(), bar.get_height() #bar size
                Grad = numpy.atleast_2d(numpy.linspace(0,1*w/max(Data),256)) #color gradient
                Ax.imshow(Grad, extent=[x,x+w,y,y+h], aspect="auto", zorder=0, norm=matplotlib.colors.NoNorm(vmin=0,vmax=1)) #apply color gradient into bar

            MaxPercentage = round((max(Data)/sum(Data))*100)
            Ax.axis(Lim) #limit the axis
            plt.title("Lunch Time Histogram in {}".format(month)) #figure title
            plt.xlabel("Most recurrent lunch time [%{}]: {}".format(MaxPercentage,max(LunchHistogramMonth.items(), key=operator.itemgetter(1))[0])) #set x axis label
            plt.xticks((0,max(Data)),('0%','{}%'.format(MaxPercentage),2),fontsize=5) #figure x ticks (%)
            plt.yticks(YTicksPos, bot_config.LunchPollOptions, fontsize=5) #figure y ticks (lunch time hours)

            buffer = io.BytesIO() #binary buffer
            Fig.savefig(buffer) #save figure in buffer
            buffer.seek(0) #starting position of the buffer

            bot.send_photo(message.chat.id,photo=buffer) #send figure as photo

        # Lunch Time Histogram (weekday)

        for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:

            LunchHistogramWeekday    = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions)))
            AuxLunchHistogramWeekday = dict()

            for key in LunchHistory.keys():

                if weekday == key.strftime('%A'): #if the weekday of the key (datetime) corresponds to the weekday in iteration

                    AuxLunchHistogramWeekday[key] = LunchHistory[key]

            if not AuxLunchHistogramWeekday: #if there isn't history about the weekday in iteration

                continue

            AuxLunchHistogramWeekday = collections.Counter(LunchHistory.values())
            LunchHistogramWeekday.update(AuxLunchHistogramWeekday.items())

            Data                     = (LunchHistogramWeekday.values())
            DataLength               = len(LunchHistogramWeekday) #length of data vector (number of different months)
            YTicksPos                = numpy.arange(DataLength) #y ticks location as an array
            Fig                      = plt.figure() #figure object
            LunchHistogramWeekdayBar = plt.barh(YTicksPos, Data) #horizontal bars plot
            Ax                       = LunchHistogramWeekdayBar[0].axes #axes object
            Lim                      = Ax.get_xlim()+Ax.get_ylim() #axes limit

            for bar in LunchHistogramWeekdayBar:

                bar.set_zorder(1)
                bar.set_facecolor('none')
                x, y = bar.get_xy() #bar data
                w, h = bar.get_width(), bar.get_height() #bar size
                Grad = numpy.atleast_2d(numpy.linspace(0,1*w/max(Data),256)) #color gradient
                Ax.imshow(Grad, extent=[x,x+w,y,y+h], aspect="auto", zorder=0, norm=matplotlib.colors.NoNorm(vmin=0,vmax=1)) #apply color gradient into bar

            MaxPercentage = round((max(Data)/sum(Data))*100)
            Ax.axis(Lim) #limit the axis
            plt.title("Lunch Time Histogram on {}".format(weekday)) #figure title
            plt.xlabel("Most recurrent lunch time [%{}]: {}".format(MaxPercentage,max(LunchHistogramWeekday.items(), key=operator.itemgetter(1))[0])) #set x axis label
            plt.xticks((0,max(Data)),('0%','{}%'.format(MaxPercentage),2),fontsize=5) #figure x ticks (%)
            plt.yticks(YTicksPos, bot_config.LunchPollOptions, fontsize=5) #figure y ticks (lunch time hours)

            buffer = io.BytesIO() #binary buffer
            Fig.savefig(buffer) #save figure in buffer
            buffer.seek(0) #starting position of the buffer

            bot.send_photo(message.chat.id,photo=buffer) #send figure as photo

    except NameError: #if there hasn't been a poll going on, initialize lunch history

        bot.reply_to(message,"There hasn't been any lunch time poll yet...")

@bot.message_handler(regexp=bot_config.LunchPollRegexp, func=lambda message: ((hasattr(message.reply_to_message,'text') is True) and (message.reply_to_message.text == bot_config.LunchPollText) and (message.reply_to_message.from_user.id == bot_config.BotID))) #Trigger: button text answer plus reply to /lunch_poll initial text and bot ID
def reply_to_lunch_poll_command(message):

    global ActiveLunchPollOptions
    global AlreadyVoted
    global LeaveLunchUsers
    global LunchPollChatID
    global LunchPollEndingTime
    global LunchPollStartingTime
    global LunchPollVotes
    global NonScheduledLunchPollFlag
    global ScheduledLunchPollFlag

    LunchPollChatID = message.chat.id

    try:

        ActiveLunchPollOptions

    except NameError:

        ActiveLunchPollOptions = bot_config.LunchPollOptions.copy() #list copy

    try:

        AlreadyVoted

    except NameError:

        AlreadyVoted = dict()

    try:

        LeaveLunchUsers

    except NameError:

        LeaveLunchUsers = list()

    try:

        LunchPollEndingTime

    except NameError:

        LunchPollEndingTime = 0  #initialize LunchPollEndingTime

    try:

        LunchPollStartingTime

    except NameError:

        LunchPollStartingTime = 0 #initialize LunchPollStartingTime

    try: #test if there is a poll going on

        LunchPollVotes

    except NameError: #if there isn't a poll going on, initialize votes counter

        LunchPollVotes = dict(zip(bot_config.LunchPollOptions,[0]*len(bot_config.LunchPollOptions)))

    try:

        NonScheduledLunchPollFlag

    except NameError:

        NonScheduledLunchPollFlag = False

    try:

        ScheduledLunchPollFlag

    except NameError:

        ScheduledLunchPollFlag = False

    if message.from_user.id not in LeaveLunchUsers: #if the voter hasn't '/leave_lunch' today

        if message.from_user.id not in AlreadyVoted: #if the voter didn't vote yet

            if (ScheduledLunchPollFlag == True) or (NonScheduledLunchPollFlag == True): #if there is a poll going on

                if (int(time.time()) >= LunchPollEndingTime) or (sum(LunchPollVotes.values()) >= (bot.get_chat_members_count(message.chat.id)-bot_config.NumBots-len(LeaveLunchUsers))): #if poll has ended by timeout or by voting all users

                    if ScheduledLunchPollFlag == True:

                        ScheduledLunchPollFlag = False

                    elif NonScheduledLunchPollFlag == True:

                        NonScheduledLunchPollFlag = False

                    bot.reply_to(message,"The lunch poll has already ended. No more votes are allowed") #response to vote

                else:

                    if re.findall(message.text,str(ActiveLunchPollOptions)): #if the vote is a valid hour

                        LunchPollVotes[message.text] += 1 #update votes counter
                        AlreadyVoted[message.from_user.id] = message.text #add voter to alreadyvoted dict
                        bot.reply_to(message,"Thank you! Your vote was successfully registered") #response to vote

                    else:

                        bot.reply_to(message,"That hour is not allowed! Please, vote again for one of the following hours:\n\n{}".format(', '.join(sorted(ActiveLunchPollOptions))))

                    if (int(time.time()) >= LunchPollEndingTime) or (sum(LunchPollVotes.values()) >= (bot.get_chat_members_count(message.chat.id)-bot_config.NumBots)): # if poll has ended

                        if ScheduledLunchPollFlag == True:

                            ScheduledLunchPollFlag = False

                        elif NonScheduledLunchPollFlag == True:

                            NonScheduledLunchPollFlag = False

                        if sum(LunchPollVotes.values()) > 0: #if someone has voted

                            lunch_poll_result()

                        del AlreadyVoted
                        del LunchPollChatID
                        del LunchPollEndingTime
                        del LunchPollStartingTime
                        del LunchPollVotes

            else:

                bot.reply_to(message,"There is no lunch poll going on! Please, create a new one by typing /lunch_poll") #response to vote

        else:

            bot.reply_to(message,"You have already voted, little rascal...") #response to vote

    else:

        bot.reply_to(message, "You are already out of today's lunch! Please, add yourself again by typing /join_lunch")

# LUNCH_TODAY COMMAND

@bot.message_handler(commands=[bot_config.LunchTodayCommand]) #Trigger: /lunch_today
def lunch_today_command(message): #/lunch_today function

    global LunchHistory

    if datetime.datetime.weekday(datetime.datetime.now()) < 5: #if it is Monday, Tuesday, Wednesday, Thursday or Friday

        try:

            LunchHistory = dict(sorted(LunchHistory.items(),key=operator.itemgetter(0),reverse=True)) #descending sorting by time

            if list(LunchHistory)[0].date() == datetime.datetime.now().date():

                bot.reply_to(message, "We are eating at *{}* today!".format(LunchHistory[list(LunchHistory)[0]]),parse_mode='Markdown')

            else:

                bot.reply_to(message,"There hasn't been a lunch poll yet. Please, create a new one by typing /lunch_poll")

        except: #if there hasn't been a poll going on

            bot.reply_to(message,"There hasn't been a lunch poll yet. Please, create a new one by typing /lunch_poll")

    else:

        bot.reply_to(message,"Please, get a life and forget me during the weekend...")

# M_RAJOY COMMAND

@bot.message_handler(commands=[bot_config.MarianoRajoyCommand]) #/m_rajoy trigger
def m_rajoy_command(message): #/m_rajoy function

    if re.fullmatch('/'+bot_config.MarianoRajoyCommand,message.text) or re.fullmatch('/'+bot_config.MarianoRajoyCommand+'@comms_gtf_bot',message.text):

        MarianoRajoySelectedVoice = random.choice(os.listdir(find_directory_path()+bot_config.MarianoRajoyPath)) #list of files

        buffer = open(find_directory_path()+bot_config.MarianoRajoyPath+MarianoRajoySelectedVoice,'rb') #binary buffer
        buffer.seek(0) #starting position of the buffer

        bot.send_voice(message.chat.id,buffer) #send voice
        
    else:
    
        pass
    
# NEWS COMMAND

@bot.message_handler(commands=[bot_config.AirbusNewsFeedCommand]) #/news trigger
def news_command(message): #/news function
    
    NewsContent  = googlenews.search('Airbus')
    InlineMarkUp = telebot.types.InlineKeyboardMarkup() #create keyboard object
    NewsTitles   = googlenews.gettext()
    NewsLinks    = googlenews.getlinks()
    
    if re.fullmatch('/'+bot_config.AirbusNewsFeedCommand,message.text) or re.fullmatch('/'+bot_config.AirbusNewsFeedCommand+'@comms_gtf_bot',message.text):
        
        for i in range(len(NewsLinks)):
        
            InlineMarkUp.add(telebot.types.InlineKeyboardButton(NewsTitles[i],url=NewsLinks[i])) #add inline button object to inline keyboard object
            
        bot.send_message(message.chat.id,'<b>AIRBUS NEWS</b>',reply_markup=InlineMarkUp,parse_mode='HTML') #send message with an inline keyboard
        
    elif re.fullmatch('/'+bot_config.AirbusNewsFeedCommand+' ([0-9]+)',message.text):
        
        SearchedNewsNum = re.search('[0-9]+',message.text)
        NewsNum         = int(SearchedNewsNum.group(0))
        
        if NewsNum < 50:
        
            NewsTitlesLen   = len(NewsTitles)
            i               = 1
            
            while NewsTitlesLen < NewsNum:
            
                i += 1
                googlenews.getpage(i)
            
            for i in range(0,NewsNum):
        
                InlineMarkUp.add(telebot.types.InlineKeyboardButton(NewsTitles[i],url=NewsLinks[i])) #add inline button object to inline keyboard object
                
            bot.send_message(message.chat.id,'<b>AIRBUS NEWS</b>',reply_markup=InlineMarkUp,parse_mode='HTML') #send message with an inline keyboard
                
        else:
            
            bot.reply_to(message,"Are you kidding me?")
    

# STOCK_PRICE COMMAND

@bot.message_handler(commands=[bot_config.StockPriceCommand]) #/stock_price trigger
def stock_price_command(message): #/stock_price function

    driver = webdriver.Chrome(); #open web browser
    driver.get("https://www.google.com/search?hl=en&q=airbus%20stock%20price"); #get website from which to extract the Airbus stock price information

    element = driver.find_element_by_id("knowledge-finance-wholepage__entity-summary"); #Airbus stock price graph element

    location = element.location; #get graph location
    size     = element.size; #get graph size

    driver.save_screenshot(find_directory_path()+bot_config.StockPricePath); #save graph as an image
    driver.quit() #close web browser

    x      = location['x']; #get x location of the image
    y      = location['y']; #get y location of the image
    width  = location['x']+size['width']; #get x width of the image
    height = location['y']+size['height']; #get y width of the image

    im = Image.open(find_directory_path()+bot_config.StockPricePath) #open image
    im = im.crop((int(x), int(y), int(width), int(height))) #crop image
    im.save(find_directory_path()+bot_config.StockPricePath) #save cropped image

    buffer = open(find_directory_path()+bot_config.StockPricePath,'rb') #binary buffer
    buffer.seek(0) #starting position of the buffer

    bot.send_photo(message.chat.id,buffer) #send image

'''SCHEDULER'''

#MONDAY

schedule.every().monday.at(bot_config.ScheduledLunchBanReminderTime).do(run_threaded,lunch_ban_reminder)
schedule.every().monday.at(bot_config.ScheduledLunchPollStartingTime).do(run_threaded,scheduled_lunch_poll)
schedule.every().monday.at(bot_config.ScheduledLunchPollReminderTime).do(run_threaded,lunch_poll_reminder)
schedule.every().monday.at(bot_config.ScheduledLunchPollEndingTime).do(run_threaded,reset_scheduled_lunch_poll)
schedule.every().monday.at(bot_config.ScheduledEmptyLeaveUsersTime).do(run_threaded,empty_leave_lunch)
schedule.every().monday.at(bot_config.ScheduledResetLunchBanTime).do(run_threaded,reset_lunch_ban)

#TUESDAY

schedule.every().tuesday.at(bot_config.ScheduledLunchBanReminderTime).do(run_threaded,lunch_ban_reminder)
schedule.every().tuesday.at(bot_config.ScheduledLunchPollStartingTime).do(run_threaded,scheduled_lunch_poll)
schedule.every().tuesday.at(bot_config.ScheduledLunchPollReminderTime).do(run_threaded,lunch_poll_reminder)
schedule.every().tuesday.at(bot_config.ScheduledLunchPollEndingTime).do(run_threaded,reset_scheduled_lunch_poll)
schedule.every().tuesday.at(bot_config.ScheduledEmptyLeaveUsersTime).do(run_threaded,empty_leave_lunch)
schedule.every().tuesday.at(bot_config.ScheduledResetLunchBanTime).do(run_threaded,reset_lunch_ban)

#WEDNESDAY

schedule.every().wednesday.at(bot_config.ScheduledLunchBanReminderTime).do(run_threaded,lunch_ban_reminder)
schedule.every().wednesday.at(bot_config.ScheduledLunchPollStartingTime).do(run_threaded,scheduled_lunch_poll)
schedule.every().wednesday.at(bot_config.ScheduledLunchPollReminderTime).do(run_threaded,lunch_poll_reminder)
schedule.every().wednesday.at(bot_config.ScheduledLunchPollEndingTime).do(run_threaded,reset_scheduled_lunch_poll)
schedule.every().wednesday.at(bot_config.ScheduledEmptyLeaveUsersTime).do(run_threaded,empty_leave_lunch)
schedule.every().wednesday.at(bot_config.ScheduledResetLunchBanTime).do(run_threaded,reset_lunch_ban)

#THURSDAY

schedule.every().thursday.at(bot_config.ScheduledLunchBanReminderTime).do(run_threaded,lunch_ban_reminder)
schedule.every().thursday.at(bot_config.ScheduledLunchPollStartingTime).do(run_threaded,scheduled_lunch_poll)
schedule.every().thursday.at(bot_config.ScheduledLunchPollReminderTime).do(run_threaded,lunch_poll_reminder)
schedule.every().thursday.at(bot_config.ScheduledLunchPollEndingTime).do(run_threaded,reset_scheduled_lunch_poll)
schedule.every().thursday.at(bot_config.ScheduledEmptyLeaveUsersTime).do(run_threaded,empty_leave_lunch)
schedule.every().thursday.at(bot_config.ScheduledResetLunchBanTime).do(run_threaded,reset_lunch_ban)

#FRIDAY

schedule.every().friday.at(bot_config.ScheduledLunchBanReminderTime).do(run_threaded,lunch_ban_reminder)
schedule.every().friday.at(bot_config.ScheduledLunchPollStartingTime).do(run_threaded,scheduled_lunch_poll)
schedule.every().friday.at(bot_config.ScheduledLunchPollReminderTime).do(run_threaded,lunch_poll_reminder)
schedule.every().friday.at(bot_config.ScheduledLunchPollEndingTime).do(run_threaded,reset_scheduled_lunch_poll)
schedule.every().friday.at(bot_config.ScheduledEmptyLeaveUsersTime).do(run_threaded,empty_leave_lunch)
schedule.every().friday.at(bot_config.ScheduledResetLunchBanTime).do(run_threaded,reset_lunch_ban)

#CONTINUOUS

schedule.every(10).seconds.do(run_threaded,lunch_poll_check)

'''MAIN'''

if __name__ == '__main__':

    try:

        threading.Thread(target=scheduled_jobs_run).start() #run scheduler in one thread
        threading.Thread(target=bot.polling(none_stop=True)).start() #run bot in another thread

    except:

        bot.send_message(bot_config.CommsGTFID,'An error occurred. Please, wait a second while I reset...') #error message
        exit()
