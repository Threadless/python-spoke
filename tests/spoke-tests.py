import spoke
import unittest2
from datetime import datetime

CUSTOMER_NAME   = 'abc123'
CUSTOMER_KEY    = 'abc123'
FAUX_ADDRESS    = '123 Fake St'
FAUX_CITY       = 'Funkytown'
FAUX_FIRST_NAME = 'Xavier'
FAUX_LAST_NAME  = 'Ample'
FAUXN_NUMBER    = '555 555 5555'
FAUX_ZIP        = '12345'
FAUX_STATE      = 'IL'

class SpokeTests(unittest2.TestCase):
    def test_constructor_required_fields(self):
        params = dict(
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
        )

        for k in params.iterkeys():
            copy = params.copy()
            del copy[k]

            self.assertRaises(spoke.ValidationError, spoke.Spoke, **copy)


    def test_constructor_optional_fields(self):
        spoke.Spoke(
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
            Logo       = spoke.Image(
                ImageType = 'jpg',
                Url       = 'file:///tmp/test.jpg',
            ),
        )


    def test_constructor_extra_fields(self):
        self.assertRaises(spoke.ValidationError, spoke.Spoke,
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
            Extra      = 17,
        )


    def test_new_required_fields(self):
        sp = spoke.Spoke(
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
        )

        params = dict(
            Cases = [dict(
                CaseId     = 1234,
                CaseType   = 'iph4tough',
                PrintImage = dict(
                    ImageType = 'jpg',
                    Url       = 'http://threadless.com/nothing.jpg',
                ),
                Quantity = 1,
            )],
            OrderId   = 2,
            OrderInfo = dict(
                Address1    = FAUX_ADDRESS,
                City        = FAUX_CITY,
                CountryCode = 'US',
                FirstName   = FAUX_FIRST_NAME,
                LastName    = FAUX_LAST_NAME,
                OrderDate   = datetime.now(),
                PhoneNumber = FAUXN_NUMBER,
                PostalCode  = FAUX_ZIP,
                State       = FAUX_STATE,
            ),
            ShippingMethod = 'FirstClass',
        )

        for k in params.iterkeys():
            copy = params.copy()
            del copy[k]

            self.assertRaises(spoke.ValidationError, spoke.Spoke, **copy)


    def test_new_optional_fields(self):
        sp = spoke.Spoke(
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
        )

        sp.new(
            Cases = [dict(
                CaseId     = 1234,
                CaseType   = 'iph4tough',
                PrintImage = dict(
                    ImageType = 'jpg',
                    Url       = 'http://threadless.com/nothing.jpg',
                ),
                Quantity = 1,
            )],
            OrderId   = 2,
            OrderInfo = dict(
                Address1    = FAUX_ADDRESS,
                City        = FAUX_CITY,
                CountryCode = 'US',
                FirstName   = FAUX_FIRST_NAME,
                LastName    = FAUX_LAST_NAME,
                OrderDate   = datetime.now(),
                PhoneNumber = FAUXN_NUMBER,
                PostalCode  = FAUX_ZIP,
                State       = FAUX_STATE,
            ),
            ShippingMethod = 'FirstClass',
            PackSlip       = spoke.Image(
                ImageType = 'jpg',
                Url       = 'file:///tmp/nothing.jpg',
            ),
            Comments = [dict(
                Type        = 'Printer',
                CommentText = 'testing',
            )]
        )


    def test_new_extra_fields(self):
        sp = spoke.Spoke(
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
        )

        self.assertRaises(spoke.ValidationError, sp.new,
            Cases = [dict(
                CaseId     = 1234,
                CaseType   = 'iph4tough',
                PrintImage = dict(
                    ImageType = 'jpg',
                    Url       = 'http://threadless.com/nothing.jpg',
                ),
                Quantity = 1,
            )],
            OrderId   = 2,
            OrderInfo = dict(
                Address1    = FAUX_ADDRESS,
                City        = FAUX_CITY,
                CountryCode = 'US',
                FirstName   = FAUX_FIRST_NAME,
                LastName    = FAUX_LAST_NAME,
                OrderDate   = datetime.now(),
                PhoneNumber = FAUXN_NUMBER,
                PostalCode  = FAUX_ZIP,
                State       = FAUX_STATE,
            ),
            ShippingMethod = 'FirstClass',
            PackSlip       = spoke.Image(
                ImageType = 'jpg',
                Url       = 'file:///tmp/nothing.jpg',
            ),
            Comments = [dict(
                Type        = 'Printer',
                CommentText = 'testing',
            )],
            Extra = 'foo',
        )


    def test_update_required_fields(self):
        sp = spoke.Spoke(
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
        )

        params = dict(
            OrderId   = 1,
            OrderInfo = dict(
                Address1    = FAUX_ADDRESS,
                City        = FAUX_CITY,
                CountryCode = 'US',
                FirstName   = FAUX_FIRST_NAME,
                LastName    = FAUX_LAST_NAME,
                OrderDate   = datetime.now(),
                PhoneNumber = FAUXN_NUMBER,
                PostalCode  = FAUX_ZIP,
                State       = FAUX_STATE,
            ),
        )

        for k in params.iterkeys():
            copy = params.copy()
            del copy[k]
            self.assertRaises(spoke.ValidationError, sp.update, **copy)


    def test_update_extra_fields(self):
        sp = spoke.Spoke(
            Customer   = CUSTOMER_NAME,
            Key        = CUSTOMER_KEY,
            production = False,
        )

        self.assertRaises(spoke.ValidationError, sp.update,
            OrderId   = 1,
            OrderInfo = dict(
                Address1    = FAUX_ADDRESS,
                City        = FAUX_CITY,
                CountryCode = 'US',
                FirstName   = FAUX_FIRST_NAME,
                LastName    = FAUX_LAST_NAME,
                OrderDate   = datetime.now(),
                PhoneNumber = FAUXN_NUMBER,
                PostalCode  = FAUX_ZIP,
                State       = FAUX_STATE,
            ),
            Extra = 'foo',
        )