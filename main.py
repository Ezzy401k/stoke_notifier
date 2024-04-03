import requests
from twilio.rest import Client
import os

# Constants
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_KEY = "STOCK_API_KEY"
NEWS_API_KEY = "NEWS_API_KEY"
GET_NEWS = False

# Twilio credentials
account_sid = "TWILIO_ACCOUNT_SID"
auth_token = "TWILIO_AUTH_TOKEN"

# Define API parameters for stock and news
tesla_api = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "outputsize": "full",
    "apikey": STOCK_API_KEY
}

news_api = {
    "q": COMPANY_NAME,
    "apiKey": NEWS_API_KEY
}

# Get stock data from Alpha Vantage API
stock_response = requests.get(url="https://www.alphavantage.co/query?", params=tesla_api)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]

# Function to get the nth key from a dictionary
def get_nth_key(dictionary, n=0):
    if n < 0:
        n += len(dictionary)
    for i, key in enumerate(dictionary.keys()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range")

# Calculate stock price difference and percentage change
today = stock_data[get_nth_key(stock_data)]
yesterday = stock_data[get_nth_key(stock_data, n=1)]
yesterday_price = float(yesterday["4. close"])
today_price = float(today["1. open"])
percentage = 0

if yesterday_price > today_price:
    difference = yesterday_price - today_price
    average = (yesterday_price + today_price) / 2
    percentage = round((difference / average) * 100, 2)
    GET_NEWS = True
    stock = "🔻"
elif today_price > yesterday_price:
    difference = today_price - yesterday_price
    average = (yesterday_price + today_price) / 2
    percentage = round((difference / average) * 100, 2)
    GET_NEWS = True
    stock = "🔺"

# If there is a price change, get news using News API
if GET_NEWS:
    news_response = requests.get(url="https://newsapi.org/v2/everything?", params=news_api)
    news_response.raise_for_status()
    news_data = news_response.json()

    # Extract news headlines, descriptions, and URLs
    news = news_data['articles']
    news_headlines = [news[i]["title"] for i in range(3)]
    news_description = [news[i]["description"] for i in range(3)]
    news_url = [news[i]["url"] for i in range(3)]

    # Send SMS using Twilio with stock information and top news headlines
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body=f"\nTSLA: {stock}{percentage}% \n"
             f"Headline: {news_headlines[0]}\n"
             f"Brief: {news_description[0]}\n"
             f"Link: {news_url[0]}\n"
             f"Headline: {news_headlines[1]}\n"
             f"Brief: {news_description[1]}\n"
             f"Link: {news_url[1]}\n"
             f"Headline: {news_headlines[2]}\n"
             f"Brief: {news_description[2]}\n"
             f"Link: {news_url[2]}",
        from_="TWILIO_FROM_NUMBER",
        to="TO_NUMBER"
    )
    print(message.status)
