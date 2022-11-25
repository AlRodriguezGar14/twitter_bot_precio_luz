from datetime import date, datetime, timedelta
from deep_translator import GoogleTranslator
import maya
import time
import requests
import tweepy
import json, urllib.request

api_key = "alQF2DbpKFMaRifLa5RyZSosl"
api_secret = "zWSAt951YgDIo0dW9O4zBLsEg0r2fAbQzZpGYLkeFV7gR6a7O0"
bearer_token = r"AAAAAAAAAAAAAAAAAAAAAMB0iQEAAAAAXpo2%2FhXD%2F36t3oWGfvWfKq3crq8%3DVTNfN20DDcE85B4wIyOjscb2cfrHewQynNItp6bEjKtZ7EV3jZ"
access_token = "1582866237285175298-kEm1VWWL5DINGUtle5vn17rEtl32yj"
access_token_secret = "bqAkLoIkkeVl08KAEMo2gT1YgMkEal8cW3GQKYyyzAnZR"

client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)




def price_variation(a, b, average):
    if a > b:
        if average:
            return f'⬇️{round(((a-b)/a)*100, 2)}%'
        else:
            return("⬇️")
    else:
        if average:
            return f"⬆️{round(((b-a)/b)*100, 2)}%"
        else:
            return("⬆️")


    return prices_dict

def import_data(url):
    response = urllib.request.urlopen(url).read()
    data = json.loads(response)
    return data['included'][0]['attributes']['values']



def translator(target, language_from, language_to):
    return GoogleTranslator(source=language_from, target=language_to).translate(target)


class Time:
    def __init__(self, days, hours, past=False):
        if past == False:
            self.real_time = datetime.now() + timedelta(days = days, hours = hours)

        else:
            self.real_time = datetime.now() - timedelta(days = days) + timedelta(hours = hours)

        self.date = self.real_time.strftime('%Y-%m-%d')
        try:
            self.day_of_week = translator(self.real_time.strftime('%A'), 'en', 'es').lower()
        except:
            self.day_of_week = self.real_time.strftime('%A').lower()
        try:
            self.month = translator(self.real_time.strftime('%B'), 'en', 'es').lower()
        except:
            self.month = self.real_time.strftime('%B').lower()

        self.day = int(self.real_time.strftime('%d'))
        self.hour_mins = self.real_time.strftime('%H:%M')
        self.year = self.real_time.strftime('%Y')
        self.only_hour = self.real_time.strftime('%H')
        if len(str(self.only_hour)) == 1:
            self.only_hour = '0' + str(self.only_hour)



def order_prices(raw_data):
    prices_dict = {}
    prices_list = []

    for price in raw_data:
        per_hour = (maya.parse(price['datetime']).datetime() + timedelta(hours=1)).strftime('%H')
        prices_dict[per_hour] = round(price['value']/1000, 5)
        prices_list.append(round(price['value']/1000, 5))

    prices_list.sort()

    cheapest = prices_list[0]
    most_expensive = prices_list[len(prices_list)-1]


    editable_prices = prices_dict.copy()

    prices_dict['cheapest_hour'] = ''.join([hour for hour, price in editable_prices.items() if price == cheapest])
    prices_dict['cheapest_price'] = cheapest
    prices_dict['most_expensive_hour'] = ''.join([hour for hour, price in editable_prices.items() if price == most_expensive])
    prices_dict['most_expensive_price'] = most_expensive
    prices_dict['average'] = round(sum(prices_list)/len(prices_list), 5)

    return prices_dict


if __name__ == "__main__":

        while True:
            now = Time(0, 1)
            next = Time(0, 2)
            tomorrow = Time(1, 1)

            three_years_ago = Time(1095, 1, True)
            three_years_ago_plus_one_day = Time(1094, 1, True)
            yesterday = Time(1, 1, True)


            get_market_price_today = f'https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date={now.date}&end_date={tomorrow.date}&time_trunc=hour'

            get_market_three_years_ago = f'https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date={three_years_ago.date}&end_date={three_years_ago_plus_one_day.date}&time_trunc=hour'


            try:
                market_today = import_data(get_market_price_today)
                market_past = import_data(get_market_three_years_ago)

                today_prices = order_prices(market_today)
                three_years_ago_prices = order_prices(market_past)

                current_price = today_prices[now.only_hour]
                next_price = today_prices[next.only_hour]
                three_years_past_price = three_years_ago_prices[three_years_ago.only_hour]
                average = float(today_prices['average'])

                tweet_day = f'El {now.day_of_week} {now.day} de {now.month} de {now.year} a las {next.only_hour}:00 el precio de la luz será de {next_price}€/kWh.\n\nAhora: {current_price}€{price_variation(next_price, current_price, False)}\nEn {three_years_ago.year}: {three_years_past_price}€{price_variation(current_price, three_years_past_price, True)}\n\nMedia hoy: {average}€ {price_variation(next_price, average, False)}\nHora barata {today_prices["cheapest_hour"]}:00\nHora cara {today_prices["most_expensive_hour"]}:00\n\nCoste esperable en hogares al precio de hoy: {round(average*291)}€ (un consumo mensual de 291Kwh)'


                last_tweet = f'El {now.day_of_week} {now.day} de {now.month} de {now.year} termina con un precio de {current_price}€/kWh.\n\nPrecio más barato del día: {today_prices["cheapest_price"]}€ a las {today_prices["cheapest_hour"]}:00\nPrecio más caro: {today_prices["most_expensive_price"]}€ a las {today_prices["most_expensive_hour"]}:00\nMedia: {average}€\n\nCoste esperable en hogares al precio de hoy: {round(average*291)}€ (un consumo mensual de 291Kwh)'


                print(today_prices)

                if next.only_hour != '00':
                    print(tweet_day)
                    client.create_tweet(text=tweet_day)
                else:
                    print(last_tweet)
                    client.create_tweet(text=last_tweet)
            except:
                print("Not data, there has been some error")
                print(get_market_price_today)


            time.sleep(3600)

