#################################
##### Name: Hiroyuki Makino #####
##### Uniqname: mhiro       #####
#################################

import sqlite3
import plotly.graph_objs as go

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'

# Part 1: Implement logic to process user commands

def organize_command(command):
    '''Organize inputted command to make it easy to handle it.
    
    Parameters
    ----------
    command: strings
        e.g., "bars country=BR source ratings bottom 8"
    
    Returns
    -------
    list
        a list of inputs
        [high level command, none/country=/region=, sell/source, ratings/cocoa/number_of_bars, top/bottom, integer]
    '''
    list_inputs = command.split(" ")
    organized_inputs = ["", "", "sell", "ratings", "top", 10] # Default
    organized_inputs[0] = list_inputs[0]

    for inp in list_inputs:
        try:
            organized_inputs[5] = int(inp)
        except:
            if inp.startswith("country=") or inp.startswith("region=") or inp == 'none':
                organized_inputs[1] = inp
            if inp in ["sell", "source"]:
                organized_inputs[2] = inp
            if inp in ["ratings", "cocoa", "number_of_bars"]:
                organized_inputs[3] = inp
            if inp in ["top", "bottom"]:
                organized_inputs[4] = inp
    return organized_inputs

def get_where(list_inputs):
    '''Make WHERE command
    
    Parameters
    ----------
    list_inputs: list
        a list of inputs
        [high level command, none/country=/region=, sell/source, ratings/cocoa/number_of_bars, top/bottom, integer]
    
    Returns
    -------
    str
        WHERE command
    '''    

    if list_inputs[1].startswith("country="):
        country = '"' + list_inputs[1][-2:] + '"'
        where = f"WHERE {list_inputs[2]}.Alpha2 = {country} "
    elif list_inputs[1].startswith("region="):
        region = '"' + list_inputs[1][7:] + '"'
        where = f"WHERE {list_inputs[2]}.Region = {region} "
    elif list_inputs[1] == "none" or list_inputs[1] == "":
        where = ""
    return where

def get_limit(list_inputs):
    '''Make LIMIT command
    
    Parameters
    ----------
    list_inputs: list
        a list of inputs
        [high level command, none/country=/region=, sell/source, ratings/cocoa/number_of_bars, top/bottom, integer]
    
    Returns
    -------
    str
        LIMIT command
    '''    

    if list_inputs[4] == "top":
        limit = "DESC LIMIT " + str(list_inputs[5])
    elif list_inputs[4] == "bottom":
        limit = "ASC LIMIT " + str(list_inputs[5])
    
    return limit

def get_agg(list_inputs):
    '''Return what <agg> will become
    
    Parameters
    ----------
    list_inputs: list
        a list of inputs
        [high level command, none/country=/region=, sell/source, ratings/cocoa/number_of_bars, top/bottom, integer]
    
    Returns
    -------
    str
        <agg: avg rating, avg cocoa, or number_of_bars>
    '''

    if list_inputs[3] == "ratings":
        agg = "AVG(Rating)"
    elif list_inputs[3] == "cocoa":
        agg = "AVG(CocoaPercent)"
    elif list_inputs[3] == "number_of_bars":
        agg = "COUNT(*)"  
    return agg

def get_sgho(list_inputs):
    '''Return SELECT, GROUP, HAVING, ORDER commands
    
    Parameters
    ----------
    list_inputs: list
        a list of inputs
        [high level command, none/country=/region=, sell/source, ratings/cocoa/number_of_bars, top/bottom, integer]
    
    Returns
    -------
    tuple
        tuple of strings (SELECT, GROUP, HAVING, ORDER)
    '''
    if list_inputs[0] == "bars":
        group = ""
        having = ""
        select = "SELECT SpecificBeanBarName, Company, sell.EnglishName, Rating, CocoaPercent, source.EnglishName "
        if list_inputs[3] == "ratings":
            order = "ORDER BY Rating "
        elif list_inputs[3] == "cocoa":
            order = "ORDER BY CocoaPercent "

    elif list_inputs[0] == "companies":
        group = "GROUP BY Company "

        agg = get_agg(list_inputs)
        select = f"SELECT Company, sell.EnglishName, {agg} "
        order = f"ORDER BY {agg} "
        having = "HAVING COUNT(*)>4 "

    elif list_inputs[0] == "countries":
        group = f"GROUP BY {list_inputs[2]}.Id "
        agg = get_agg(list_inputs)
        select = f"SELECT {list_inputs[2]}.EnglishName, {list_inputs[2]}.Region, {agg} "
        order = f"ORDER BY {agg} "
        having = "HAVING COUNT(*)>4 "

    elif list_inputs[0] == "regions":
        group = f"GROUP BY {list_inputs[2]}.Region "
        agg = get_agg(list_inputs)
        select = f"SELECT {list_inputs[2]}.Region, {agg} "
        order = f"ORDER BY {agg} "
        having = "HAVING COUNT(*)>4 "

    return select, group, having, order

def process_command(command):
    '''Process inputted command.
    
    Parameters
    ----------
    command: strings
        e.g., "bars country=BR source ratings bottom 8"
    
    Returns
    -------
    list
        a list of tuple records of choc.sqlite
    '''

    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()

    # Organize inputted commands
    list_inputs = organize_command(command)

    from_ = "FROM Bars "

    # Make JOIN commands
    join = "JOIN Countries as sell ON Bars.CompanyLocationId = sell.Id "
    join2 = "JOIN Countries as source ON Bars.BroadBeanOriginId = source.Id "

    # Get SELECT, GROUP, HAVING, ORDER commands
    select, group, having, order = get_sgho(list_inputs)

    # Get WHERE command using Option1 [none/country=/region=]
    where = get_where(list_inputs)

    # Get LIMIT command using Option4 [top/bottom]
    limit = get_limit(list_inputs)

    query = select + from_ + join + join2 + where + group + having + order + limit
    
    result = cursor.execute(query).fetchall()
    connection.close()
    
    return result

def check_int(s):
    '''Check if input can be converted to int.

    Parameters
    ----------
    s: strings
    
    Returns
    -------
    bool
        True: int, False: not int
    '''
    try:
        int(s)
        return True
    except:
        return False

def valid_command(command):
    '''Check the validity of the command.
    
    Parameters
    ----------
    command: strings
        e.g., "bars country=BR source ratings bottom 8"
    
    Returns
    -------
    bool
        True: valid command, False: invalid command
    '''
    list_inputs = command.split(" ")

    option1 = 0
    option2 = 0
    option3 = 0
    option4 = 0
    option5 = 0
    others = 0

    # Check high level command
    if list_inputs[0] not in ["bars", "companies", "countries", "regions"]:
        return False
    else:
        for input in list_inputs:
            if input.startswith('none') or input.startswith('country=') or input.startswith('region='):
                option1 += 1
            elif input in ['sell', 'source']:
                option2 += 1
            elif input in ['ratings', 'cocoa', 'number_of_bars']:
                option3 += 1
            elif input in ['top', 'bottom']:
                option4 += 1
            elif check_int(input):
                option5 += 1
            else:
                others += 1
        if option1 >= 2 or option2 >= 2 or option3 >= 2 or option4 >= 2 or option5 >= 2 or others >= 2:
            return False
    
    organized_inputs = organize_command(command)

    if organized_inputs[0] == "bars":
        if organized_inputs[3] == 'number_of_bars':
            return False
    elif organized_inputs[0] == "companies":
        if organized_inputs[2] == "source":
            return False
    elif organized_inputs[0] == "countries":
        if organized_inputs[1].startswith('country='):
            return False
    elif organized_inputs[0] == "regions":
        if organized_inputs[1] != "":
            return False

    return True
        

def cut_str12(s):
    '''Trim strings to be 12 characters + "...".
    
    Parameters
    ----------
    s: strings
    
    Returns
    -------
    strings
        First 12 characters + "..." (e.g., United State...)
    '''
    if len(s) > 12:
        s = s[:12] + "..."
    else:
        s = "{:<15s}".format(s)
    return s
    


def print_result(command):
    '''Print results like example outputs.
    
    Parameters
    ----------
    command: strings
        e.g., "bars country=BR source ratings bottom 8"
    
    Returns
    -------
    None

    '''

    list_inputs = organize_command(command)
    list_results = process_command(command)

    if list_results == []:
        print('No results')

    for result in list_results:
        formatted_result =list()
        formatted_result.append(cut_str12(result[0]))
        if list_inputs[0] == "bars":
            formatted_result.append(cut_str12(result[1]))
            formatted_result.append(cut_str12(result[2]))
            formatted_result.append("{:.1f}".format(result[3]))
            formatted_result.append("{:.0%}".format(result[4]))
            formatted_result.append(cut_str12(result[5]))
        
        else:
            if  list_inputs[0] in ["companies", "countries"]:
                formatted_result.append(cut_str12(result[1])) 

            if list_inputs[3] == "ratings":
                formatted_result.append("{:.1f}".format(result[-1]))
            elif list_inputs[3] == "cocoa":
                formatted_result.append("{:.0%}".format(result[-1]))
            elif list_inputs[3] == "number_of_bars":
                formatted_result.append(str(result[-1]))

        print(" ".join(formatted_result))

def plot_result(command):
    '''Plot results like example outputs.
    
    Parameters
    ----------
    command: strings
        e.g., "bars country=BR source ratings bottom 8"
    
    Returns
    -------
    None

    '''

    list_inputs = organize_command(command)
    list_results = process_command(command)

    if list_results == []:
        print('No results')


    xvals = list()
    yvals = list()
    for result in list_results:
        xvals.append(result[0])
        if list_inputs[0] == "bars":
            if list_inputs[3] == 'ratings':
                yvals.append(result[3])
            elif list_inputs[3] == 'cocoa':
                yvals.append(result[4])
        elif list_inputs[0] in ["companies", "countries"]:
            yvals.append(result[2])
        elif  list_inputs[0] == "regions":
            yvals.append(result[1])

    bar_data = go.Bar(x=xvals, y=yvals)
    fig = go.Figure(data=bar_data)
    fig.show()

def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')
        if response == 'help':
            print(help_text)
            continue
        elif response == "exit":
            pass
        elif response.endswith(' barplot'):
            response = response.replace(' barplot','')
            if valid_command(response):
                print('Generating a plot...')
                plot_result(response)
                print()
            else:
                print('Command not recognized (invalid command): ', response)
                print()
        else:
            if valid_command(response):
                print_result(response)
                print()
            else:
                print('Command not recognized (invalid command): ', response)
                print()    

    print('Bye!')

# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()
