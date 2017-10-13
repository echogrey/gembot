import time
import random
import datetime
import telepot
import xlrd
import urllib.request
import requests
from bs4 import BeautifulSoup
import gunicorn
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
import emoji

##    This is a program made for a Telegram bot that is supposed to give
##    the user a basic overview of specific exchange programmes available
##    to students studying at NTU, Singapore.
##
##    This bot includes things as custom keyboards, reading from excel files
##    and parsing the content of a given url to find images.
##
##    ----------------------------------------------------------
##       INITIALIZATION
##    ----------------------------------------------------------
##
##    The program reads an excel file from a given url and saves it's content using
##    xlrd and urllib.request. Storing the different cell values in different lists.
##    The code is done with the knowledge of what kind of information each column contains
##    in the excel file. 


workbook = xlrd.open_workbook(u'Result.xlsx') #read the excel file
table = workbook.sheets()[0]                  #use the first sheet of the excel file 
nrows = table.nrows                           #number of rows 
ncols = table.ncols                           #number of columns

# Dictionary: Define the countries in each continent, add to a list.

continent = ['Asia', 'Europe', 'North America', 'South America', 'Oceania']

contid = {}

contid['Asia'] = ['Brunei', 'China', 'Hong Kong', 'India', 'Indonesia', 'Israel', 
                'Japan', 'Korea', 'Malaysia', 'Philippines', 'Russia', 'Taiwan',
                'Thailand', 'Turkey','Vietnam']
contid['Europe'] = ['Austria', 'Crotia', 'Denmark',' France', 'Germany', 'Italy',
                  'Norway', 'Russia', 'Spain', 'Sweden', 'UK']
contid['North America'] = ['Canada', 'Costa Rica', 'Mexico', 'USA']
contid['South America'] = ['Peru', 'Uruguay']
contid['Oceania'] = ['Australia']

#Match each country with corresponding university or universities 
destid = {}

for i in range(1,nrows):
    desti = table.cell_value(i, 6)
    uniname = table.cell_value(i, 1)
    destid.setdefault(desti,[]).append(uniname)

#Match each university with it's programme information
uniinfo = {}
for i in range(1,nrows):
    desti = table.cell_value(i, 6)
    uniname = table.cell_value(i, 1)
    protype = table.cell_value(i, 4)
    procate = table.cell_value(i, 5)
    aunum = table.cell_value(i, 3)
    autype = table.cell_value(i, 0)
    procost = table.cell_value(i, 2)
    finanaid = table.cell_value(i, 7)
    uniinfo.setdefault(uniname,[]).append(
        [desti, uniname, protype, procate, aunum, autype, procost, finanaid])


##
##    --------------------
##        FUNCTIONS
##    --------------------
##
##


def on_chat_message(msg):
    """ Function used for the bot to interpret the
        user's chat messages. The input parameter 'msg'
        is identified. The chat number and chat id are obtained,
        making it possible for the bot to know who sent what and
        who to reply to. 
    Args:
        param1: the message sent from the user.
    Returns: 
        Depending on if the sent message contains a command, country name or
        university name, the bot's reply will vary:
        - If the user types in a country name (case sensitive), the bot will reply
        with a list of universities that offers exchange programmes in that specific country
        - If the user types in the beginning of a university name (case sensitive),
        the bot will reply with programme information for that specific university
        - If the user uses the command /start, the bot will reply with a custom keyboard
        that the user can use as an interface for the bot
        - If the user sends the command /random, a randomized picture of a university campus
        with corresponding university name will be sent by the bot
        - If the bot can't interpret the message, the bot will send a standard message to the user.
    """
    
    chat_id = msg['chat']['id']
    command = msg['text']

    print ('Got command: %s' % command)

    #interpret the user's message using function short(cmd)     
    shortuni = short(command)
    
    if command == '/start':

##    If the user sends the command /start --> create custom keyboard.
##    -> Define button labels and their corresponding callback data

             markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text=emoji.emojize('What is GEM?:eyes:'), callback_data='info')],
                     [dict(text=emoji.emojize('Check university list:books:'), callback_data='region')],
                     [dict(text=emoji.emojize('Explore a mysterious university:ghost:'), callback_data='photo')],
                     [dict(text=emoji.emojize('Official GEM Discoverer URL:sparkles:'), url='http://global.ntu.edu.sg/GMP/gemdiscoverer/Pages/index.aspx')],
                 ])

             global message_with_inline_keyboard
             message_with_inline_keyboard = bot.sendMessage(chat_id, emoji.emojize("Welcome to GEM bot:rocket:You're lovin' it!:love_letter:"), reply_markup=markup)

    elif command == '/random':

##    If the user sends the command /random --> use get_photo()
##    - returns a random university with a picture of it's building to the user
        
        search, photo = get_photo()
        bot.sendPhoto(chat_id,photo)
        bot.sendMessage(chat_id,emoji.emojize(":balloon:This is a picture of ")+search)
        bot.sendMessage(chat_id,'To find out more about the shown university, just reply with keywords of the university name')    

        
#Choose a university: 
    elif command in destid:

#   If the user types in a country name, the bot will
#   respond with a list of universities in that specific country
        
        des = sorted(set(destid[command]))
        uni = ''
        for n in des:
            uni = uni + n + '\n'
        bot.sendMessage(chat_id, emoji.emojize('>>> Okay:key:~ Here is a list of universities you can choose from: \n') + uni)
        bot.sendMessage(chat_id,'To find out more about a specific university, reply with keywords of the university name')

    elif shortuni== None:
        bot.sendMessage(chat_id,emoji.emojize("Ooooops!:pushpin:Something went wrong. Try again! "))
        
#Find the info for a specific university:
    elif shortuni[0]:

#   If the user types in a university name or something
#   that the bot will interpret as a university name,
#   the bot will reply with programme information for that specific university
        
        allinfo = uniinfo[shortuni[1]]
        search, photo = get_photo(shortuni[2])
        bot.sendPhoto(chat_id,photo)
        count = 0
        for info in allinfo:
            count += 1 
            desti = 'Destination: ' + info[0] + '\n'
            uniname = 'University Name: ' + info[1] + '\n'
            protype = 'Porgramme Type: ' + info[2] + '\n'
            procate = 'Programme Category: ' + info[3] + '\n'
            aunum = 'Number of AUs: ' + str(info[4]) + '\n'
            autype = 'Type of AUs: ' + info[5] + '\n'
            procost = 'Programme Cost: ' + str(info[6]) + '\n'
            finanaid = 'Type of Finalcial Aid Available: ' + str(info[7]) + '\n'
            message = '>>> Choice ' + str(count) + ': \n' + desti + uniname + protype + procate + aunum + autype + \
                      procost + finanaid
            bot.sendMessage(chat_id, message)


def short(cmd):
    """ A function used to interpret the users 
    chat message. If the message corresponds to any of the
    university names, the bot will interpret it
    as if the user wrote the complete university name and respond
    with programme information. 
    
    NOTE: the function will return the first match,
    even if there are multiple matches.
    SECOND NOTE: Why did someone define a function within a function?
    Args:
      cmd: the text contained in a message
    Return:
       True - bool const.
       k    - the item in the list that corresponds to the message
       i    - the index of the item
    """
    
    i=1
    for k in list(uniinfo.keys()):
        i=i+1
        if cmd.lower() in k.lower():
            # FOR DEBUGGING: print(i)
            return (True, k, i)
            

# Function to handle the queries from the buttons
# This will help 
            
def on_callback_query(msg):
    """ Function used to determine what action to take
        when a button on the custom keyboard is pressed.
        Using telepot.glance, the bot is able to see if the
        data in the recieved "message" has the flavor 'callback_query',
        and if so, if the callback data corresponds to any of the
        if-cases in on_callback_query.
        
    Args:
        msg: the message sent from the user.
    Returns:
        Depending on the callback data, either:
        - new custom keyboard with labels and callback data
        - a photo of a university building with it's corresponding
        name and programme information, sent by the bot
        - a message with information about the GEM discoverer,
        sent by the bot
        - 
    """    

    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)
    global message_with_inline_keyboard


    if data == 'photo':

#   see function get_photo(arg)

        search, photo = get_photo(0)
        bot.sendPhoto(from_id,photo)
        bot.sendMessage(from_id,emoji.emojize(":balloon:This is a picture of ")+search)
        bot.sendMessage(from_id,'To find out more about the shown university, just reply with keywords of the university name')
    
    elif data == 'info':

#   If the info button is pressed, the bot
#   replies with a message about the GEM Discoverer programme

        bot.sendMessage(from_id, emoji.emojize("Welcome to the GEM bot:two_men_holding_hands::two_women_holding_hands:! This is a bot "
                                "that\'s supposed to give you info regarding NTU's GEM Discoverer. "
                                "\nGEM Discoverer offers various programmes that place students globally for overseas internships, summer studies, business/cultural executive programmes and language training. All programmes are credit-bearing and designed to enhance your cross-cultural intelligence."
                                "\nTo start, use /start "
                                "\nIf you like this bot, please vote for GEM Saiko!!!:airplane::ticket::bus::tropical_drink:"))
        
    elif data == 'region':

#   University list - opens a new custom keyboard with buttons
#   for each region.

        msg_idf = telepot.message_identifier(message_with_inline_keyboard)


        my_keyboard = [[
            InlineKeyboardButton(text='Asia', callback_data='Asia'),
            InlineKeyboardButton(text='Europe', callback_data='Europe'),
        ], [
            InlineKeyboardButton(text='North America', callback_data='North America'),
            InlineKeyboardButton(text='South America', callback_data='South America'),
        ], [
            InlineKeyboardButton(text='Oceania', callback_data='Oceania'),
        ], [
            InlineKeyboardButton(text=emoji.emojize('Back to Main Menu:house:'), callback_data='main_menu'),
            ]]

        markup = InlineKeyboardMarkup(inline_keyboard=my_keyboard )
        bot.editMessageText(msg_idf,emoji.emojize('Where would you like to go?:paw_prints:'), reply_markup=markup)

    elif data == 'main_menu':

#   The main menu (custom keyboard) is opened 
        
        msg_idf = telepot.message_identifier(message_with_inline_keyboard)

        markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text=emoji.emojize('What is GEM?:eyes:'), callback_data='info')],
                     [dict(text=emoji.emojize('Check university list:books:'), callback_data='region')],
                     [dict(text=emoji.emojize('Explore a mysterious university:ghost:'), callback_data='photo')],
                     [dict(text=emoji.emojize('Official GEM Discoverer URL:sparkles:'), url='http://global.ntu.edu.sg/GMP/gemdiscoverer/Pages/index.aspx')],
                 ])
             
        bot.editMessageText(msg_idf,emoji.emojize("Welcome to GEM bot:rocket:You're lovin' it!:love_letter:"), reply_markup=markup)

    elif data in contid:

#   If the user presses one of the region buttons in the
#   university list, the bot replies with a list of countries
#   that offers exchange programmes for NTU students

        country = contid[data]
        message = ''
        for c in country:
            message = message + c + '\n'
        bot.sendMessage(from_id, emoji.emojize('>>> Well received!:palm_tree: Now pick one from the following countries: \n') + message)
        bot.sendMessage(from_id,'To see available universities in a specific country, reply with the desired country name (case sensitive!)')



        
def get_photo(rand=0):
    """Function used for retrieving an image of a university building
       given a university name. The photo is retrived by web crawling
       a given url (Yahoo Images for now, easily changed in the code).
       The search string contains the university name and the word building. 
       The function parses the search result and puts the 10 first image links
       in a list. A random number between 1 and 10 is then generated to choose
       one of the image links from the list. 
       Args:
           rand (optional) - If no input is given, rand is by default
                             set to 0. In this case, a university name
                             will be randomly generated from the excel file.
                            
       Returns:
           search_str - The university name used for searching the images
           myList[num] - A link to one of the 10 images found (string). 
    """
    
    if rand == 0:
        search_str = table.cell_value(random.randint(1,nrows-1), 1)
    else:
        search_str = table.cell_value(rand, 1)
        #NOTE - Google only gives thumbnails, don't know how to work around that. Use Yahoo Images for now
        
        #url = "https://www.google.com/search?tbm=isch&q=\""+search_str+"+building\""       

    url2 = "https://images.search.yahoo.com/search/images?p="+search_str+"+building\""
    page = requests.get(url2).text
    soup = BeautifulSoup(page, 'html.parser')
    i = 0
    myList=[]

    for raw_img in soup.find_all('img'):
          link = raw_img.get('src')
          if link:
                myList.append(link)
                i+=1
                if i > 10:
                  break

        #Return one of the first 10 items found from the image search
    num= random.randint(0,i-1)        
    return search_str, myList[num]

#--------------------------
# Bot setup
#--------------------------

token = '345657820:AAFI1hqiZMxbiAParFJU9judchccFQQi7Oo'  #GEMbot
##token2 = '340623043:AAHIHEOyfQwPU6KCqklaPIz8i5WEsGCiYVA' #testbot

bot = telepot.Bot(token)
MessageLoop(bot,{'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()

print ('I am listening ...')
while 1:
    time.sleep(10)
