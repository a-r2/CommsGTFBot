#TOKEN
BotToken = '637064932:AAHtkJJdgFiaVZVKo-BN0LchC067dgZdWOA' #BOT Token (https://api.telegram.org/bot[]/getUpdates)
BotID    = 637064932 #Unique BOT ID

#TIMEZONE
Timezone     = 'Europe/Madrid' #Bot timezone
TimezoneName = 'Madrid' #Bot timezone name

#GENERAL
CommsGTFDir = 'CommsGTFBot'
CommsGTFID  = None #group chat ID
NumBots     = 1 #Number of bots in CommsGTF group

#COMMANDS
EthicsComplianceCommand = 'ethics_compliance' #One must be good
HelpCommand             = 'help' #CommsGTFBot's help
JoinLunchCommand        = 'join_lunch' #Join today's lunch
LeaveLunchCommand       = 'leave_lunch' #Leave today's lunch
LunchActiveCommand      = 'lunch_active' #List of active lunch hours
LunchBanCommand         = 'lunch_ban' #Ban specific hours or time intervals for today's lunch
LunchPollCommand        = 'lunch_poll' #Poll to decide lunch time for today
LunchStatsCommand       = 'lunch_stats' #Statistics about past lunch times
LunchTodayCommand       = 'lunch_today' #When are we eating today?
AirbusNewsFeedCommand   = 'news' #Airbus news feed
MarianoRajoyCommand     = 'm_rajoy' #Mariano Rajoy at his best
StockPriceCommand       = 'stock_price' #Current Airbus stock price

#ETHICS_COMPLIANCE COMMAND
EthicsCompliancePath    = "/Images/Ethics and compliance/"
EthicsComplianceFolders = ['Alvarez Cascos','Angel Acebes','Carlos Fabra','Eduardo Zaplana','Esperanza Aguirre','Francisco Camps','Francisco Correa','Francisco Granados','Ignacio Gonzalez','Infanta Cristina','Isabel Pantoja','Jaime Mayor Oreja','Jaume Matas','Javier Arenas','Jesus Gil','Jordi Pujol','Jose Antonio Grinan','Julian Munoz','Luis Barcenas','Manuel Chaves','Mariano Rajoy','Rafael Gomez','Rey Juan Carlos','Rita Barbera','Rodrigo Rato','Ruiz Mateos','Urdangarin']

#LUNCH_BAN COMMAND
LunchBanText1   = 'Please, reply to this message specifying hours or intervals of time when you will be unable to have lunch'
LunchBanText2   = "I didn't understand a word you said..."
LunchBanText3   = '{} {} been successfully banned'
LunchBanText4   = '{} {} been already banned'
LunchBanText5   = '{} {} not valid...'
LunchBanRegexp1 = '[0-2][0-9]:[0-5][0-9]'
LunchBanRegexp2 = '([0-2][0-9]:[0-5][0-9])([- ]*)([0-2][0-9]:[0-5][0-9])'
LunchBanRegexp3 = '[- ]*'

#LUNCH_POLL COMMAND
LunchPollOptions = ['12:00','12:15','12:30','12:45','13:00','13:15','13:30','13:45','14:00','14:15','14:30','14:45','15:00'] #Cantine timetable
LunchPollTimeout = 30 #Lunch poll timeout (minutes)
LunchPollRegexp  = '[0-2][0-9]:[0-5][0-9]' #Cantine timetable regexp (based on LunchPollOptions)
LunchPollText    = 'A new lunch poll has just started. Please, vote!' #Lunch poll starting message

#M.RAJOY COMMANDS
MarianoRajoyPath = "/Audios/Mariano Rajoy/"

#STOCK_PRICE COMMAND
StockPricePath = "/Screenshots/Airbus_stock_price.png" #Airbus stock price screenshot saving path

#SCHEDULER
ScheduledLunchBanReminderTime  = '08:30'
ScheduledLunchPollStartingTime = '09:30' #Starting time of scheduled lunch time poll (from Monday to Friday)
ScheduledLunchPollReminderTime = '10:30'
ScheduledLunchPollEndingTime   = '11:30' #Ending time of scheduled lunch time poll (from Monday to Friday)
ScheduledEmptyLeaveUsersTime   = '00:00'
ScheduledResetLunchBanTime     = '00:00'
