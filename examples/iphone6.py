#!/usr/bin/env python
"""
This example creates one order containing 4 items.  In this case a couple
different iPhone 6 cases.

To run this code just edit your CUSTOMER_CODE and API_KEY
for Spoke Custom below and type:

    python iphone6.py

"""


import datetime
import pprint

import spoke


CUSTOMER_CODE = ...
API_KEY = ...


api = spoke.Spoke(
    production=True,
    Customer=CUSTOMER_CODE,
    Key=API_KEY,
    Logo={
        'ImageType' : 'svg',
        'Url' : "https://d1s82l1atzspzx.cloudfront.net/threadless-media/static/imgs/global/threadless-logo.svg",
    },
)

order_id = 2
shipment_id = 2
shipping_address = {
    'FirstName' : 'Mister',
    'LastName' : 'Mittens',
    'Address1' : '1260 W Madison St',
    'City' : 'Chicago',
    'State' : 'IL',
    'PostalCode' : '60607',
    'CountryCode' : 'US',
    'OrderDate' : datetime.datetime.now().strftime("%m/%d/%Y"),
    'PhoneNumber' : '555-555-5555',
    'PurchaseOrderNumber' : shipment_id,
    'GiftMessage' : '',
    'Prices':dict(
        DisplayOnPackingSlip="No",
        CurrencySymbol="$",
        TaxCents='0',
        ShippingCents='0',
        DiscountCents='0'
    ),
}


def get_image(filename):
    return "https://d1s82l1atzspzx.cloudfront.net/threadless-media/{}?rot=270&q=95".format(filename)


items = [
    dict(stock_id=1,
         quantity=1,
         print_image=get_image('artist_designs/1680000-1760000/1713600-1715200/1714912-1714944/1714928/1714928-3938-star_iphone2.jpg'),
         case_type="iph6tough"
     ),
    dict(stock_id=2,
         quantity=1,
         print_image=get_image('artist_designs/1520000-1600000/1547200-1548800/1547424-1547456/1547453/1547453-5376-attack_iphone.JPG'),
         case_type="iph6tough"
     ),
    dict(stock_id=3,
         quantity=1,
         print_image=get_image('artist_designs/1840000-1920000/1883200-1884800/1884544-1884576/1884551/1884551-4709-iphonemythunderstood.jpg'),
         case_type="iph6bt"
     ),
    dict(stock_id=4,
         quantity=1,
         print_image=get_image('artist_designs/1680000-1760000/1729600-1731200/1730048-1730080/1730078/1730078-5430-iphone.jpg'),
         case_type="iph6bt"
     ),
]


data = dict(
    OrderId=order_id,
    ShippingMethod='Overnight',
    OrderInfo=shipping_address,
    Cases=[
        {
            'CaseId': item['stock_id'],
            'CaseType': item["case_type"],
            'Quantity': item['quantity'],
        'PrintImage': {
            'ImageType': 'jpg',
            'Url': item['print_image'],
        },
        } for item in items
    ],
)



pprint.pprint(data)

api.new(**data)
