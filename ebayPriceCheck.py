from bs4 import BeautifulSoup
import requests
import numpy as np
import emoji
import csv
from ebayListing import Listing
from datetime import datetime

LINK = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=macbook+air+m1&_sacat=0"

def get_prices_by_link(link):
    # get source
    r = requests.get( link )
    # parse source
    page_parse = BeautifulSoup( r.text, 'html.parser' )
    # find all list items from search results
    search_results = page_parse.find( "ul", {"class":"srp-results"} ).find_all( "li", {"class":"s-item"} )

    item_prices = []

    for result in search_results:
        price_as_text = result.find( "span", {"class":"s-item__price"} ).text
        if "to" in price_as_text:
            continue
        price = float( price_as_text[1:].replace( ",","" ) )
        item_prices.append( price )
    return item_prices

def get_prices_from_link(link):
    # get source
    r = requests.get( link )
    # parse source
    page_parse = BeautifulSoup( r.text, 'html.parser' )
    # find all list items from search results
    search_results = page_parse.find( "ul", {"class":"srp-results"} ).find_all( "li", {"class":"s-item"} )

    items = []

    for result in search_results:
        name = result.find("div", {"class":"s-item__title"}).text
        hyperlink = result.find("a", {"class":"s-item__link"}).get("href")
        price_text = result.find( "span", {"class":"s-item__price"} ).text
        if "parts" in name:
            continue
        if "to" in price_text:
            continue
        price = float( price_text[1:].replace( ",","" ) )
        item = Listing(name, price, hyperlink)
        items.append(item)
    return items


def remove_outliers(prices, m = 2):
    data = np.array( prices )
    return data[ abs ( data - np.mean( data ) ) < m * np.std( data ) ]

def get_average_prices( prices ):
    return np.mean( prices )

def get_lowest_price( prices ):
    return np.min( prices )

def save_to_file(prices):
    fields = [ datetime.today().strftime( "%B-%D-%Y" ), np.around( get_average_prices( prices ), 2 ) ]
    with open ( 'prices.csv', 'a', newline = '' ) as f:
        writer = csv.writer( f )
        writer.writerow( fields )

def save_to_csv(items):
    header = [ "Date", "Listing Name", "Price", "Link" ]

    with open ('prices.csv', 'a', newline = '' ) as csvfile:
        writer = csv.writer( csvfile )
        writer.writerow(header)

        for item in items:
            fields = [ datetime.today().strftime( "%B-%D-%Y" ), emoji.demojize(item.title), str(item.price), str(item.link)]
            writer.writerow( fields )
        
    

if __name__ == "__main__":
    items = get_prices_from_link(LINK)

    items.sort(key=lambda item: item.price)

    save_to_csv(items)

    for item in items:
        print("---------------------------------")
        print("\nName: " + item.title)
        print("\nPrice: " + str( item.price ) )
        print("\nLink: " + str( item.link ) )
    # prices = get_prices_by_link(LINK)
    # prices_without_outliers =  remove_outliers( prices )
    # print( "This page's average: " + str( get_average_prices( prices_without_outliers ) ) )
    # print( "This is the lowest price: " + str( get_lowest_price( prices_without_outliers ) ) )
    # print( "\t Here is the link for the lowest priced item: " + str( get_lowest_price( prices_without_outliers ) ) )