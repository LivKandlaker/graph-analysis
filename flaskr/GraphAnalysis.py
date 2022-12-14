import logging
import os
import re
from numerize import numerize
from flask import Flask, request
import yagmail
from scipy.stats import linregress
import pandas as pd
import requests
from bs4 import BeautifulSoup
import wikipedia
from flask import render_template
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

# app = Flask('templates-index.html')
app = Flask(__name__, template_folder='../../flask_project/flaskr/templates')
GRAPH_FOLDER = os.path.join('flaskr')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = GRAPH_FOLDER


# Decorator defines a route
# https://localhost:5000/

@app.route('/')
@app.route('/index')
@app.route('/my-link-Fibonachi/')
@app.route('/plot.png')
@app.route('/')
# def index():
# """
# The link between python and HTML with flaskv - index page
#:return: index.html
# """
# return render_template("index.html")

@app.route('/')
def index():
    # Use the web scraping wiki page as our starting point
    FibonacciResponse = requests.get(
        url="https://en.wikipedia.org/wiki/Fibonacci_number",
    )
    TrendVolumeResponse = requests.get(
        url="https://en.wikipedia.org/wiki/Volume_analysis",
    )
    RocResponse = requests.get(
        url="https://en.wikipedia.org/wiki/Momentum_investing",
    )
    SMAResponse = requests.get(
        url="https://en.wikipedia.org/wiki/Moving_average",
    )
    CandleStickResponse = requests.get(
        url="https://en.wikipedia.org/wiki/Candlestick_chart",
    )

    # Find an element by the ID tag using Beautiful soup
    Fibonacci_title = BeautifulSoup(FibonacciResponse.content, 'html.parser').find(id="firstHeading")
    Fibo_data = Fibonacci_title.string
    Volume_title = BeautifulSoup(TrendVolumeResponse.content, 'html.parser').find(id="firstHeading")
    Vol_data = Volume_title.string
    Roc_title = BeautifulSoup(RocResponse.content, 'html.parser').find(id="firstHeading")
    Roc_data = Roc_title.string
    SMA_title = BeautifulSoup(SMAResponse.content, 'html.parser').find(id="firstHeading")
    SMA_data = SMA_title.string
    CandleStick_title = BeautifulSoup(CandleStickResponse.content, 'html.parser').find(id="firstHeading")
    CandleStick_data = CandleStick_title.string

    # Find an element by the name tag (img) using Beautiful soup
    URL = "https://www.wikihow.com/Read-a-Candlestick-Chart"  # Replace this with the website's URL
    getURL = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    img = BeautifulSoup(getURL.text, 'html.parser').find_all('img')

    # Specify the Wikipedia page
    Fibo_wiki = wikipedia.page('Fibonacci_number')
    Vol_wiki = wikipedia.page('Volume_analysis')
    Roc_wiki = wikipedia.page('Momentum_investing')
    SMA_wiki = wikipedia.page('Moving_average')
    CandleStick_wiki = wikipedia.page('Candlestick_chart')

    # Extract the plain text content of the page
    Fibo_text = Fibo_wiki.content
    Fibo_res = Fibo_text.partition("== Definition ==")[0]
    Vol_text = Vol_wiki.content
    Vol_res = Vol_text.partition("== Theory ==")[0]
    Roc_text = Roc_wiki.content
    Roc_res = Roc_text.partition("== History ==")[0]
    SMA_text = SMA_wiki.content
    SMA_res = SMA_text.partition("== Simple moving average ==")[0]
    CandleStick_text = CandleStick_wiki.content
    CandleStick_res = CandleStick_text.partition("== History ==")[0]

    # save in a variable only the img src
    imageSources = []
    for image in img:
        imageSources.append(image.get('src'))

    # extract substring between two characters to get the first img link
    pattern = "None\,(.*?)\, None,"
    CandleStickSubstring = re.search(pattern, str(imageSources)).group(1)
    CandleStickSubstring = CandleStickSubstring[2:-1]

    return render_template('index.html', FiboDataToRender=Fibo_data, FiboContentToRender=Fibo_res,
                           VolDataToRender=Vol_data, VolContentToRender=Vol_res,
                           RocDataToRender=Roc_data, RocContentToRender=Roc_res,
                           SMADataToRender=SMA_data, SMAContentToRender=SMA_res,
                           CandleStickDataToRender=CandleStick_data, CandleStickContentToRender=CandleStick_res,
                           CandleStickImage=CandleStickSubstring)


@app.route('/plots', methods=['GET', 'POST'])
def plots():
    """
    The link between python and HTML with flask
    :return: plots.html
    """
    return render_template("plots.html")


@app.route('/Send_To_Fibonacci', methods=['POST'])
def Send_To_Fibonacci():
    """
    handle data 2 save the details from the form in new varaibles and send to my Fibonacci function
    :return: message: "back to our website"
    """
    projectpath = request.form['projectFilepath']
    periodDateStart = request.form['periodDateStarted']
    periodDateEnd = request.form['periodDateEnd']
    fibonacci_graph = my_link_Fibonachi(projectpath, periodDateStart, periodDateEnd)

    # will print a message to the console
    logging.debug(fibonacci_graph)

    return fibonacci_graph


def my_link_Fibonachi(company_symbol, Date_start, Date_End):
    """
  Calculate all the Fibonacci level with the max&min to the chosen period, and show fibonacci
   plot with tha Adj Close plot.
  :param company_symbol: Known company or coin symbol at the stocks market
  :param Date_start: Day,Month and Year for Start
  :param Date_End: Day,Month and Year for the End
  :return: Fibonacci plots for the period that chosen
  """
    # Save the plot in Variable and return the plot to the HTML web

    # will print a message to the console
    logging.debug('I got clicked!')

    # Import specific data from the Yahoo Finance website
    data = yf.download(company_symbol, start=Date_start, end=Date_End)
    data['date_id'] = ((data.index.date - data.index.date.min())).astype('timedelta64[D]')
    data['date_id'] = data['date_id'].dt.days + 1

    # Finding the maximum price and finding the minimum price
    maximum_price = data['Adj Close'].max()
    minimum_price = data['Adj Close'].min()

    # Get the difference and calculate the Fibonacci level
    difference = maximum_price - minimum_price
    first_level = maximum_price - difference * 0.236
    second_level = maximum_price - difference * 0.382
    third_level = maximum_price - difference * 0.5
    fourth_level = maximum_price - difference * 0.618

    # Define the graph size
    plt.figure(figsize=(12.33, 4.5))

    # Define the graph name-graph title and for the Adj close information
    plt.title('Fibonnacci Plot')
    plt.plot(data.index, data['Adj Close'])

    # Create colored straight lines according to calculated Fibonacci levels
    plt.axhline(maximum_price, linestyle='--', alpha=0.3, color='red', label='maximum_price')
    plt.axhline(first_level, linestyle='--', alpha=0.3, color='orange', label='first_level')
    plt.axhline(second_level, linestyle='--', alpha=0.3, color='yellow', label='second_level')
    plt.axhline(third_level, linestyle='--', alpha=0.3, color='green', label='third_level')
    plt.axhline(fourth_level, linestyle='--', alpha=0.3, color='blue', label='fourth_level')
    plt.axhline(minimum_price, linestyle='--', alpha=0.3, color='purple', label='minimum_price')

    # Define the font size of x & y label (Date & close price)
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Close Price in USD', fontsize=18)
    plt.legend(loc="upper left")

    plt.savefig("myPlot.jpg")
    plt.show()
    return render_template('plots.html')


@app.route('/my-link-Trends/')
def my_link_Trends(company_symbol, periodDateStart, periodDateEnd):
    """
  Calculate the Trends-Lines - connect all the local minimum value together, and connect
  all the local maximum value together
  :param company_symbol:Known company or coin symbol at the stocks market
  :param periodDateStart:Day,Month and Year for Start
  :param periodDateEnd:Day,Month and Year for End
  :return: Two plot in one figure: 1)Adj close with Trends Line. 2) Volume plot
  """
    # will print a message to the console
    logging.debug('I got clicked!')

    # Import specific data from the Yahoo Finance website
    data = yf.download(company_symbol, start=periodDateStart, end=periodDateEnd)

    data['date_id'] = ((data.index.date - data.index.date.min())).astype('timedelta64[D]')
    data['date_id'] = data['date_id'].dt.days + 1

    # Create a linear line for high trend line in graph
    # will print the data table to the console
    logging.debug(data)

    Data_Trends = data.copy()
    while len(Data_Trends) > 3:
        reg = linregress(
            x=Data_Trends['date_id'],
            y=Data_Trends['High'],
        )
        Data_Trends = Data_Trends.loc[Data_Trends['High'] > reg[0] * Data_Trends['date_id'] + reg[1]]

    reg = linregress(
        x=Data_Trends['date_id'],
        y=Data_Trends['High'],
    )

    data['high_trend'] = reg[0] * data['date_id'] + reg[1]

    # Create a linear line for low trend line

    Data_Trends = data.copy()

    while len(Data_Trends) > 3:
        reg = linregress(
            x=Data_Trends['date_id'],
            y=Data_Trends['Low'],
        )
        Data_Trends = Data_Trends.loc[Data_Trends['Low'] < reg[0] * Data_Trends['date_id'] + reg[1]]

    reg = linregress(
        x=Data_Trends['date_id'],
        y=Data_Trends['Low'],
    )

    data['low_trend'] = reg[0] * data['date_id'] + reg[1]

    # Create place for 2 Plot in one output
    fig, ax = plt.subplots(2)

    # plot for Trends
    ax[0].plot(data['Adj Close'], label='Adj_Close')
    ax[0].plot(data['high_trend'], label='high_trend')
    ax[0].plot(data['low_trend'], label='low_trend')
    plt.legend(loc="upper left")

    # Plot for Volume
    ax[1].plot(data['Volume'], label='Volume')
    plt.legend(loc="upper left")

    # Save the plot in Variable and return the plot to the HTML web
    # plot_url = plt.show()
    # return render_template('plots.html', plot_url=plot_url)

    # Save the plot in Variable and return the plot to the HTML web
    fig = plt.savefig("myPlot")
    plt.show()
    return render_template('plots.html')


@app.route('/Send_to_Trend', methods=['POST'])
def Send_to_Trend():
    """
    handle data save the details from the form in new variables and send to my trends function
    :return: message: "back to our website"
    """
    projectpath = request.form['projectFilepath']
    periodDateStart = request.form['periodDateStarted']
    periodDateEnd = request.form['periodDateEnd']
    Trends_and_volume = my_link_Trends(projectpath, periodDateStart, periodDateEnd)
    return Trends_and_volume


@app.route('/my-link-ROC/')
def my_link_ROCtool(company_symbol, ROCperiodDateStart, ROCperiodDateEnd, ROCtermTrading):
    """
    Create a graph figure of the ROC tool from the HTML
    :param company_symbol:stocks symbol (TSLA - is the symbol for tesla company for example)
    :param ROCperiodDateStart:Date start user chose
    :param ROCperiodDateEnd:Date End user chose
    :param ROCtermTrading:Time of trading for
    :return:ROC tool from the HTML
    """

    def get_stock(company_symbol, Date_start, Date_End):
        """
        Get stock and period and create a data frame copy
        :param company_symbol: stocks symbol (TSLA - is the symbol for tesla company for example)
        :param Date_start: Date start user chose
        :param Date_End: Date End user chose
        :return: Data frame of Adj close
        """
        # Import specific data from the Yahoo Finance website
        data = yf.download(company_symbol, start=Date_start, end=Date_End)

        data['date_id'] = ((data.index.date - data.index.date.min())).astype('timedelta64[D]')
        data['date_id'] = data['date_id'].dt.days + 1

        # Return the Adj Close column
        return data['Adj Close']

    def ROC(df, n):
        """
        Calculate the Rate of change
        :param df: Copy of the data frame
        :param n: Time of trading for
        :return: ROC
        """
        M = df.diff(n - 1)
        N = df.shift(n - 1)
        ROC = pd.Series(((M / N) * 100))

        # Return the series of ROC tool
        return ROC

    # Send the specipic data to get stock for the Adj close column
    df = pd.DataFrame(get_stock(company_symbol, ROCperiodDateStart, ROCperiodDateEnd))

    # Send the Adj close plot and the time for term trading to ROC function
    df['ROC'] = ROC(df['Adj Close'], int(ROCtermTrading))
    df.tail()

    # Define the size of the plot and the name title of the plot. Create graph for the index un ROC data frame
    plt.figure(figsize=(12.33, 4.5))
    plt.title('ROC Plot')
    plt.plot(df.index, df['ROC'], label='ROC')
    plt.legend(loc="upper left")

    # Save the plot in Variable and return the plot to the HTML web
    # plot_url = plt.show()
    # return render_template('index.html', plot_url=plot_url)

    # Save the plot in Variable and return the plot to the HTML web
    fig = plt.savefig("myPlot")
    plt.show()
    return render_template('plots.html')


@app.route('/Send_To_ROC', methods=['POST'])
def Send_To_ROC():
    """
    handle data save the details from the form in new variables and send to my ROC tool function
    :return: message: "back to our website"
    """
    projectFilePath = request.form['projectFilepath']
    ROCperiodDateStart = request.form['ROCperiodDateStart']
    ROCperiodDateEnd = request.form['ROCperiodDateEnd']
    ROCtermTrading = request.form['termTrading']
    ROC_tool = my_link_ROCtool(projectFilePath, ROCperiodDateStart, ROCperiodDateEnd, ROCtermTrading)
    return ROC_tool


@app.route('/Send_To_SMA', methods=['POST'])
def Send_To_SMA():
    """
    handle data save the details from the form in new variables and send to my SMA tool function
    :return: message: "back to our website"
    """
    projectFilePath = request.form['projectFilepath']
    SMAperiodDateStart = request.form['SMAperiodDateStart']
    SMAperiodDateEnd = request.form['SMAperiodDateEnd']
    SMA_tool = my_link_SMAtool(projectFilePath, SMAperiodDateStart, SMAperiodDateEnd)
    return SMA_tool


@app.route('/my-link-SMA/')
def my_link_SMAtool(company_symbol, SMAperiodDateStart, SMAperiodDateEnd):
    """
    Create a graph figure of the SMA tool from the HTML
    (20 & 100 days)
    :param company_symbol:stocks symbol (TSLA - is the symbol for tesla company for example)
    :param SMAperiodDateStart:Date start user chose
    :param SMAperiodDateEnd:Date End user chose
    :return:SMA tool from the HTML
    """
    import matplotlib.pyplot as plt

    # set start and end dates
    start = SMAperiodDateStart
    end = SMAperiodDateEnd

    # extract the closing price data
    data = yf.download(company_symbol, start=start, end=end)

    data['date_id'] = ((data.index.date - data.index.date.min())).astype('timedelta64[D]')
    data['date_id'] = data['date_id'].dt.days + 1

    # create 20 days simple moving average column
    data['20_SMA'] = data['Adj Close'].rolling(window=20, min_periods=1).mean()

    # create 50 days simple moving average column
    data['100_SMA'] = data['Adj Close'].rolling(window=100, min_periods=1).mean()

    plt.figure(figsize=(20, 10))
    # plot close price, short-term and long-term moving averages
    data['Adj Close'].plot(color='black', label='Close Price')
    data['20_SMA'].plot(color='blue', label='20 - day SMA')
    data['100_SMA'].plot(color='green', label='100 - day SMA')
    plt.legend(loc="upper left")
    # Save the plot in Variable and return the plot to the HTML web
    # plot_url = plt.show()
    # return render_template('index.html', plot_url=plot_url)

    # Save the plot in Variable and return the plot to the HTML web
    fig = plt.savefig("myPlot")
    plt.show()
    return render_template('plots.html')


@app.route('/Send_To_Mail', methods=['POST'])
def Send_To_Mail():
    """
    handle data save the details from the form in new variables and send to my SMA tool function
    :return: message: "back to our website"
    """
    projectFilePath = request.form['projectFilepath']
    Mail_tool = my_link_Mail(projectFilePath)
    return "Thank you, please check your mail box"


@app.route('/my-link-Mail/')
def my_link_Mail(Mail_Address):
    """
    Ask for Email Adress from the user and send him the last plot
    :param Mail_Address: User Email Address
    :return:SEND Email with the plots attachments
    """

    # initiating connection with SMTP server
    # SMTP= Simple Mail Transfer Protocol

    yag = yagmail.SMTP("Enter your Email Address here!", "Enter your Email Password here!")

    try:
        yag.send(to=Mail_Address, cc="qndlqrlyb@gmail.com", bcc="kandalker.liv@gmail.com",
                 subject="Graph Analysis Attachment Plots",
                 contents=["<h2> Your Plot is: </h2>", "<p> We hope to see you soon</p>"],
                 attachments=[r"C:\Users\qndlq\PycharmProjects\pythonProject\flaskr\myPlot.png"])
        print("Email sent")

    except:
        print("Error, Email not Send")
    return render_template('plots.html')


@app.route('/Send_To_CandleStick', methods=['POST'])
def Send_To_CandleStick():
    """
    handle data save the details from the form in new variables and send to my SMA tool function
    :return: message: "back to our website"
    """
    projectFilePath = request.form['projectFilepath']
    candleStickPeriodDateStart = request.form['CandleStickPeriodDateStart']
    CandleStickPeriodDateEnd = request.form['CandleStickPeriodDateEnd']
    CandleStick_tool = my_link_Candle_Stick_tool(projectFilePath, candleStickPeriodDateStart, CandleStickPeriodDateEnd)
    return CandleStick_tool


@app.route('/my-link-CandleStick/')
def my_link_Candle_Stick_tool(company_symbol, candleStickPeriodDateStart, CandleStickPeriodDateEnd):
    """
    Create a graph figure of the Candle Stick tool from the HTML
    :param company_symbol:stocks symbol (TSLA - is the symbol for tesla company for example)
    :param candleStickPeriodDateStart:Date start user chose
    :param CandleStickPeriodDateEnd:Date End user chose
    :return:Candle Stick tool from the HTML
    """
    import plotly.graph_objects as go
    import yfinance as yf

    df = yf.download(company_symbol, start=candleStickPeriodDateStart, end=CandleStickPeriodDateEnd)
    df['date_id'] = ((df.index.date - df.index.date.min())).astype('timedelta64[D]')
    df['date_id'] = df['date_id'].dt.days + 1

    symbpl = yf.Ticker(company_symbol)

    fig = go.Figure(data=[go.Candlestick(x=df['date_id'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(
        title='The ' + company_symbol + ' charts ' + ' From : ' + candleStickPeriodDateStart + ' To : ' + CandleStickPeriodDateEnd + ' | Industry : ' +
              symbpl.info['industry'] + ' | Sector : ' + symbpl.info['sector'],
        yaxis_title=company_symbol + ' Stock',
        xaxis_title='The Market cap : ' + str(numerize.numerize(symbpl.info['marketCap'])) +
                    ' | The Net Income : ' + str(numerize.numerize(symbpl.info['netIncomeToCommon'])) +
                    ' | The Price to earnings ratio PE Multiple : ' + str(int(symbpl.info['marketCap'] /
                                                                              symbpl.info['netIncomeToCommon'])))

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()
    return render_template('plots.html')

@app.route('/Send_To_RSI', methods=['POST'])
def Send_To_RSI():
    """
    handle data 2 save the details from the form in new varaibles and send to my Fibonacci function
    :return: message: "back to our website"
    """
    projectpath = request.form['projectFilepath']
    periodDateStart = request.form['periodDateStarted']
    periodDateEnd = request.form['periodDateEnd']
    RSI_graph = my_link_RSI(projectpath, periodDateStart, periodDateEnd)

    # will print a message to the console
    logging.debug(RSI_graph)

    return RSI_graph

def my_link_RSI(company_symbol, Date_start, Date_End):
    """
  Calculate all the Fibonacci level with the max&min to the chosen period, and show fibonacci
   plot with tha Adj Close plot.
  :param company_symbol: Known company or coin symbol at the stocks market
  :param Date_start: Day,Month and Year for Start
  :param Date_End: Day,Month and Year for the End
  :return: Fibonacci plots for the period that chosen
  """
    # Save the plot in Variable and return the plot to the HTML web

    # will print a message to the console
    logging.debug('I got clicked!')

    # Import specific data from the Yahoo Finance website
    df = yf.download(company_symbol, start=Date_start, end=Date_End)
    ## 14_Day RSI
    df['Up Move'] = np.nan
    df['Down Move'] = np.nan
    df['Average Up'] = np.nan
    df['Average Down'] = np.nan
    # Relative Strength
    df['RS'] = np.nan
    # Relative Strength Index
    df['RSI'] = np.nan

    ## Calculate Up Move & Down Move
    for x in range(1, len(df)):
        df['Up Move'][x] = 0
        df['Down Move'][x] = 0

        if df['Adj Close'][x] > df['Adj Close'][x - 1]:
            df['Up Move'][x] = df['Adj Close'][x] - df['Adj Close'][x - 1]

        if df['Adj Close'][x] < df['Adj Close'][x - 1]:
            df['Down Move'][x] = abs(df['Adj Close'][x] - df['Adj Close'][x - 1])

    ## Calculate initial Average Up & Down, RS and RSI
    df['Average Up'][14] = df['Up Move'][1:15].mean()
    df['Average Down'][14] = df['Down Move'][1:15].mean()
    df['RS'][14] = df['Average Up'][14] / df['Average Down'][14]
    df['RSI'][14] = 100 - (100 / (1 + df['RS'][14]))

    ## Calculate rest of Average Up, Average Down, RS, RSI
    for x in range(15, len(df)):
        df['Average Up'][x] = (df['Average Up'][x - 1] * 13 + df['Up Move'][x]) / 14
        df['Average Down'][x] = (df['Average Down'][x - 1] * 13 + df['Down Move'][x]) / 14
        df['RS'][x] = df['Average Up'][x] / df['Average Down'][x]
        df['RSI'][x] = 100 - (100 / (1 + df['RS'][x]))

    print(df)

    ## Chart the stock price and RSI
    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))
    fig.suptitle(company_symbol + ' Stock Price (top) - 14 day RSI (bottom)')
    axs[0].plot(df['Adj Close'], alpha=0.3, color='black', linewidth=1.9)
    axs[1].plot(df['RSI'], alpha=0.3, color='blue', linewidth=1.9)
    axs[0].grid()
    axs[1].grid()

    plt.show()

@app.route('/Send_To_MACD', methods=['POST'])
def Send_To_MACD():
    """
    handle data 2 save the details from the form in new varaibles and send to my Fibonacci function
    :return: message: "back to our website"
    """
    projectpath = request.form['projectFilepath']
    periodDateStart = request.form['periodDateStarted']
    periodDateEnd = request.form['periodDateEnd']
    MACD_graph = my_link_MACD(projectpath, periodDateStart, periodDateEnd)

    # will print a message to the console
    logging.debug(MACD_graph)

    return MACD_graph

def my_link_MACD(company_symbol, Date_start, Date_End):
    """
  Calculate all the Fibonacci level with the max&min to the chosen period, and show fibonacci
   plot with tha Adj Close plot.
  :param company_symbol: Known company or coin symbol at the stocks market
  :param Date_start: Day,Month and Year for Start
  :param Date_End: Day,Month and Year for the End
  :return: Fibonacci plots for the period that chosen
  """
    # Save the plot in Variable and return the plot to the HTML web

    # will print a message to the console
    logging.debug('I got clicked!')

    # Import specific data from the Yahoo Finance website
    df = yf.download(company_symbol, start=Date_start, end=Date_End)

    # Calculate the MACD and Signal Line indicators
    # Calculate the Short Term Exponential Moving Average
    ShortEMA = df.Close.ewm(span=12, adjust=False).mean()

    # Calculate the Long Term Exponential Moving Average
    LongEMA = df.Close.ewm(span=26, adjust=False).mean()

    # Calculate the Moving Average Convergence/Divergence (MACD)
    MACD = ShortEMA - LongEMA

    # Plot the Chart
    plt.figure(figsize=(14, 8))
    plt.style.use('classic')
    plt.plot(df.index, MACD, label=company_symbol + ' MACD', color='blue')

    # plt.plot(df.index, signal, label='Signal Line', color='red')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.show()

if __name__ == '__main__':
    app.run(debug=True)

