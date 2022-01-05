from private.config import slack_key
from private.config import gwsic_ticker
from slack import WebClient
from slack.errors import SlackApiError
from datetime import datetime
from datetime import date
import yfinance as yf
import stockquotes

def slacker(post_message):
    client = WebClient(token=slack_key)
    try:
        response = client.chat_postMessage(
            channel='#random',
            text=post_message
        )
        assert response["message"]["text"] == post_message
    except SlackApiError as e:
        # Error will be thrown if SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # let's us see what the error is
        print(f"Got the following error: {e.response['error']}")

def stock_update():
    for ticker_id, ticker_info in gwsic_ticker.items():
        report_header ="******* BEGIN {0} UPDATE **********\nDAILY REPORT for: {0} as of {1} \n -------------------------------".format(ticker_id, datetime.now().strftime("%m-%d-%Y %H:%M:%S"))

        stock = stockquotes.Stock(ticker_id)
        current_value = (stock.current_price * gwsic_ticker[ticker_id]['qty'])
        stock_value = current_value - gwsic_ticker[ticker_id]['total']

        stock_change = (stock_value / gwsic_ticker[ticker_id]['total']) * 100


        stock_history = "{0} shares of {1} was purchased on {2} at the market price of ${3} for a total value of ${4}".format(
            gwsic_ticker[ticker_id]['qty'], gwsic_ticker[ticker_id]['name'], gwsic_ticker[ticker_id]['pur_date'],
            gwsic_ticker[ticker_id]['pur_price'], gwsic_ticker[ticker_id]['total'])

        stock_current = "GWSIC's holdings of {0} at {1} share(s) at today's price of ${2} is valued at ${3}".format(
            gwsic_ticker[ticker_id]['name'], gwsic_ticker[ticker_id]['qty'], stock.current_price, round(current_value,2))

        stock_diff = None
        if(round(stock_value,2) >= 0):
            stock_diff = "That is an increase of +${0}, or +{1}%".format(round(stock_value,2), round(stock_change,2))
        else:
            stock_diff = "That is a decrease of -${0}, or -{1}%".format(round(stock_value,2), round(stock_change,2))

        message = "{0} \n {1} \n {2} \n {3} \n******* END UPDATE ************ \n".format(report_header,stock_history,stock_current,stock_diff)
        slacker(message)

if __name__ == '__main__':
    ## Checking if today is a Friday, if so then we run our week-ending report
    if date.today().weekday() == 4:
        stock_update()
    else:
        print("nothing to report")
