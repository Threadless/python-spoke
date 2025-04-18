'''
    Python interface to the Spoke API.  This is the reference documentation; see
    the included README for a higher level overview.
'''

import re

from lxml import etree
import requests
import six

__version__ = '1.0.29'

__all__ = ['Case', 'Comment', 'Image', 'OrderInfo', 'PackSlipCustomInfo', 'Spoke', 'ValidationError', 'SpokeError']

# Validation code

class ValidationError(Exception):
    '''
        An exception that represents the case that parameter validation failed.
    '''
    pass


def passthrough(v):
    return v


class Validator(object):
    is_required = True
    is_conditional = False

    def __init__(self, inner=None):
        if inner is None:
            inner = passthrough
        elif isinstance(inner, type):
            t = inner
            def type_validator(value):
                if isinstance(value, t):
                    return value
                return t(**value)
            # XXX func name?
            inner = type_validator
        elif not isinstance(inner, Validator):
            raise TypeError('inputs to validators must be None, types, or validators')
        self.inner = inner


    def __call__(self, value):
        return self.inner(value)


class Required(Validator):
    pass

class RequiredOnlyIfNot(Required):
    """ This validator will require the key ONLY IF other keys are NOT present in 
    the payload.

    This validator was added because threadless.com payloads use "ShippingMethod" whereas
    Artist Shops payloads use "ShippingAccount" and "ShippingMethodId"

    An example would be that SomeKey is only required if SomeOtherKey is not present in the payload:
    "SomeKey" = RequiredOnlyIfNot(['SomeOtherKey'])

    """
    is_required = True
    is_conditional = True
    other_keys = []

    def __init__(self, other_keys=[], inner=None):
        if not isinstance(other_keys, (tuple, list)):
            other_keys = [other_keys]
        self.other_keys = other_keys

        super(RequiredOnlyIfNot, self).__init__(inner)

    def __call__(self, value, d):
        # if all of other_keys are present in the payload,
        # then require don't require this field
        if all([key in d.keys() for key in self.other_keys]):
            self.is_required = False

        return super(RequiredOnlyIfNot, self).__call__(value)

class Optional(Validator):
    is_required = False


class Array(Validator):
    def __call__(self, value):
        if isinstance(value, list):
            if len(value) == 0:
                raise ValidationError('Empty array found where array required')
            return [ self.inner(v) for v in value ]
        else:
            return [ self.inner(value) ]


class Enum(Validator):
    def __init__(self, *values):
        self.values = set(values)

    def __call__(self, value):
        if value not in self.values:
            raise ValidationError('value "%s" not in enum' % str(value))
        return value


def _validate(d, **validation_spec):
    for k, v in d.items():
        validator = validation_spec.pop(k, None)
        if validator is None:
            raise ValidationError('parameter "%s" not allowed' % k)
        if validator.is_conditional: # conditional validators need the whole dictionary to look at other keys
            d[k] = validator(v, d)
        else:
            d[k] = validator(v)

    # it's possible that there's some conditional validators still in the validation_spec
    # because their corresponding key isn't in the payload, so look over them and if all 
    # of their other_keys are present in the payload, then this conditional validator isn't required
    for k, v in validation_spec.items():
        if v.is_conditional and all([key in d.keys() for key in v.other_keys]):
            v.is_required = False

    validation_spec = dict((k, v) for k, v in validation_spec.items() if v.is_required)
    if validation_spec:
        first_key = sorted(validation_spec.keys())[0]
        raise ValidationError('Missing required parameter "%s"' % first_key)


# Actual spoke classes

class Image(object):
    '''
        Represents an image resource.  Used for PrintImage, QcImage, Logo, and PackSlip.
    '''

    def __init__(self, **kwargs):
        '''
            Required parameters:

            ImageType - The type of image referenced (ex. jpg, png, etc)
            Url       - The URL of the image referenced.
        '''
        _validate(kwargs,
            ImageType = Required(),
            Url       = Required(),
        )
        self.__dict__ = kwargs


class Comment(object):
    '''
        Represents a comment.  Used for comments on Case objects.
    '''

    def __init__(self, **kwargs):
        '''
            Required parameters:

            Type        - One of 'Printer', 'Packaging'
            CommentText - The actual comment text
        '''
        _validate(kwargs,
            Type        = Required(Enum('Printer', 'Packaging')),
            CommentText = Required(),
        )
        self.__dict__ = kwargs


class PackSlipCustomInfo(object):
    '''
        Represents custom information for a pack slip.
    '''

    def __init__(self, **kwargs):
        '''
            Optional parameters:

            Text1
            Text2
            Text3
            Text4
            Text5
            Text6
        '''
        _validate(kwargs,
            Text1 = Optional(),
            Text2 = Optional(),
            Text3 = Optional(),
            Text4 = Optional(),
            Text5 = Optional(),
            Text6 = Optional(),
        )
        self.__dict__ = kwargs


class Prices(object):
    '''
        Specifies pricing data.
    '''

    def __init__(self, **kwargs):
        '''
            Optional parameters:

            DisplayOnPackingSlip - Whether or not to show prices on the packing slip
            CurrencySymbol       - The symbol for the currency used
            TaxCents             - The tax price, expressed in cents
            ShippingCents        - The shipping price, expressed in cents
            DiscountCents        - The discount price (if any), expressed in cents
        '''
        _validate(kwargs,
            DisplayOnPackingSlip = Optional(Enum('Yes', 'No')),
            CurrencySymbol       = Optional(),
            TaxCents             = Optional(),
            ShippingCents        = Optional(),
            DiscountCents        = Optional(),
        )
        self.__dict__ = kwargs


class OrderInfo(object):
    '''
        Specifies order information.
    '''

    def __init__(self, **kwargs):
        '''
            The following parameters are required:

            FirstName
            LastName
            Address1
            City
            State - If the given country doesn't have states/provinces, send the city
            PostalCode
            CountryCode
            OrderDate - May be a datetime.datetime object
            PhoneNumber

            The following parameters are optional:

            Address2
            PurchaseOrderNumber - internal PO number
            GiftMessage
            PackSlipCustomInfo - A PackSlipCustomInfo object
            Prices - A Prices object
            ShippingLabelReference1
            ShippingLabelReference2
        '''
        _validate(kwargs,
            FirstName               = Required(),
            LastName                = Required(),
            Address1                = Required(),
            Address2                = Optional(),
            City                    = Required(),
            State                   = Required(),
            PostalCode              = Required(),
            CountryCode             = Required(),
            OrderDate               = Required(),
            PhoneNumber             = Required(),
            PurchaseOrderNumber     = Optional(),
            GiftMessage             = Optional(),
            PackSlipCustomInfo      = Optional(PackSlipCustomInfo),
            Prices                  = Optional(Prices),
            ShippingLabelReference1 = Optional(),
            ShippingLabelReference2 = Optional(),

        )
        self.__dict__ = kwargs


class Case(object):
    '''
        A case represents a phone or tablet cover in the order.
    '''
    def __init__(self, **kwargs):
        '''
            The following parameters are required:

            CaseId
            CaseType
            Quantity
            PrintImage

            The following parameters are optional:

            QcImage
            Prices
            CurrencySymbol
            RetailCents
            DiscountCents
            Comments
        '''
        _validate(kwargs,
            CaseId         = Required(),
            CaseType       = Required(Enum(
                'bb9900bt', 'bbz10tough', 'kindlefirebt',
                # apple / iphone
                'iph3bt', 'iph3tough', 'iph4bt', 'iph4tough', 'iph4tough2', 
                'ipt4gbt',  'iph5bt', 'iph5vibe', 'iph5cbt', 'ipt5gbt', 
                'iph5xtreme', 'iph6bt', 'iph6tough', 'iph655bt', 'iph655tough',
                'ipad4bt', 'ipadminitough', 'iph6sbtpresale', 
                'iph6stoughpresale', 'iph6splusbtpresale', 
                'iph6splustoughpresale', 'iph7bt', 'iph7tough', 'iph7plusbt',
                'iph7plustough', 'iph8bt', 'iph8tough', 'iph10bt', 
                'iph10tough', 'iphxsmaxbt', 'iphxsmaxtough', 'iphxrbt', 
                'iphxrtough', 'iph11bt', 'iph11tough', 'iph11probt', 
                'iph11protough', 'iph11promaxbt', 'iph11promaxtough',
                'iph12minibt', 'iph12minitough', 'iph12probt',
                'iph12protough', 'iph12promaxbt', 'iph12promaxtough',
                'iph13bt', 'iph13tough', 'iph13minibt', 'iph13minitough',
                'iph13probt', 'iph13protough', 'iph13promaxbt', 'iph13promaxtough',
                'iph14snapps', 'iph14prosnapps', 'iph14plussnapps', 'iph14promaxsnapps',
                'iph14toughps', 'iph14protoughps', 'iph14plustoughps', 'iph14promaxtoughps',
                'SP10599', # iphone 15 slim
                'SP10603', # iphone 15 tough
                'SP10601', # iphone 15 plus slim
                'SP10605', # iphone 15 plus tough
                'SP10600', # iphone 15 pro slim
                'SP10604', # iphone 15 pro tough
                'SP10602', # iphone 15 pro max slim
                'SP10606', # iphone 15 pro max tough
                'SP10625', # iphone 16 slim
                'SP10629', # iphone 16 tough
                'SP10627', # iphone 16 plus slim
                'SP10631', # iphone 16 plus tough
                'SP10626', # iphone 16 pro slim
                'SP10630', # iphone 16 pro tough
                'SP10628', # iphone 16 pro max slim
                'SP10632', # iphone 16 pro max tough
                # buttons
                'button-round-125', 'button-round-225',
                # samsung / galaxy
                'ssgn2tough', 'ssgs3vibe', 'ssgs4bt', 'ssgs4vibe',
                'ssgs5bt', 'ssgn4bt', 'ssgs6vibe', 'ssgs6bt', 'ssgs7bt', 'ssgs8bt',
                # magnets
                '3x3-magnet', '4x4-magnet', '6x6-magnet',
                # mugs
                'mug11oz', 'mug15oz', 'mug12ozlatte', 'mug15oztravel', 
                # notebooks
                'journal5x7blank', 'journal5x7ruled', 'spiral6x8ruled',  
                # stickers
                '2x2-white', '3x3-white', '4x4-white', '6x6-white',
                '2x2-clear', '3x3-clear', '4x4-clear', '6x6-clear',
                # socks
                'sock-small', 'sock-medium', 'sock-large',
                # face masks
                'facemasksmall', 'facemasklarge',
                # puzzles
                '8x10-puzzle', '11x14-puzzle', '16x20-puzzle',
                # mouse pad / desk mat
                '9x7mousepad', 'smallmat', 'largemat', 'xlargemat',
                )),
            Quantity       = Required(),
            PrintImage     = Required(Image),
            QcImage        = Optional(Image),
            Prices         = Optional(),
            CurrencySymbol = Optional(),
            RetailCents    = Optional(),
            DiscountCents  = Optional(),
            Comments       = Optional(Array(Comment)),
        )
        self.__dict__ = kwargs


class SpokeError(Exception):
    '''
    Represents an error received from the spoke API.
    '''
    pass


class SpokeDuplicateOrder(SpokeError):
    '''
    Represents a duplicate order error returned from the Spoke API
    '''


ERROR_REGEX = [
    (re.compile(r"duplicate orderid", re.I), SpokeDuplicateOrder),
]



class Transport(object):
    def __init__(self, url):
        self.url = url

    def send(self, request):
        res = requests.post(self.url, data=request)
        res.raise_for_status()
        return res.content

ARRAY_CHILDREN_NAMES = dict(
    Cases    = 'CaseInfo',
    Comments = 'Comment',
)

PRODUCTION_URL = 'https://api.spokecustom.com/order/submit'
STAGING_URL    = 'https://api-staging.spokecustom.com/order/submit'

class Spoke(object):
    '''
        The main spoke request object.  It contains any
        request parameters that won't change between requests.
    '''

    def __init__(self, **kwargs):
        '''
            The following fields are required:

            production - Whether or not to use the production API
            Customer   - Your customer ID
            Key        - Your customer key

            The following fields are optional:

            transport - A custom transport object.  Used mainly for testing and debugging; be warned, here be dragons
            Logo
        '''
        _validate(kwargs,
            production = Required(),
            transport  = Optional(),
            Customer   = Required(),
            Key        = Required(),
            Logo       = Optional(Image),
        )
        self.__dict__ = kwargs
        self.transport = self._create_transport()

    def _create_transport(self):
        if hasattr(self, 'transport'):
            return self.transport
        elif self.production:
            return Transport(PRODUCTION_URL)
        else:
            return Transport(STAGING_URL)

    def _generate_tree(self, tag_name, serializers, node):
        if isinstance(node, list):
            elements = etree.Element(tag_name)
            for child in node:
                elements.append(self._generate_tree(ARRAY_CHILDREN_NAMES[tag_name], serializers, child))
            return elements
        elif isinstance(node, dict):
            parent = etree.Element(tag_name)

            for tag_name, subtree in node.items():
                parent.append(self._generate_tree(tag_name, serializers, subtree))
            return parent
        elif type(node) in serializers:
            serializer = serializers[type(node)]
            return serializer(tag_name, node)
        else:
            element = etree.Element(tag_name)

            if not isinstance(node, str):
                node = str(node)
            element.text = node

            return element

    def _generate_request(self, RequestType, Order):
        def serialize_it(tag_name, value):
            return self._generate_tree(tag_name, serializers, value.__dict__)

        serializers = {
            Case               : serialize_it,
            Image              : serialize_it,
            OrderInfo          : serialize_it,
            Comment            : serialize_it,
            PackSlipCustomInfo : serialize_it,
            Prices             : serialize_it,
        }

        request = self._generate_tree('Request', serializers, dict(
            Customer    = self.Customer,
            RequestType = RequestType,
            Key         = self.Key,
            Order       = Order,
        ))
        return etree.tostring(request, encoding='utf-8', pretty_print=True)

    def _send_request(self, request):
        res    = self.transport.send(request)
        tree   = etree.fromstring(res.decode('utf-8'))
        result = tree.xpath('//result')[0].text

        if result == 'Success':
            immc_id = int(tree.xpath('//immc_id')[0].text)
            return dict(immc_id = immc_id)
        else:
            message = tree.xpath('//message')[0].text
            for regex, exception_class in ERROR_REGEX:
                if regex.match(message):
                    raise exception_class(message)
            raise SpokeError(message)

    def new(self, **kwargs):
        '''
            Creates a new order.  If there is a problem creating the order,
            a SpokeError is raised.  Otherwise, a dictionary is returned.  The
            returned dictionary is guaranteed to have an immc_id key-value pair,
            which contains the Spoke ID for your order.  More key-value pairs may
            be present, but they are not guaranteed and their presence may change
            in successive versions of this module.  Any key-value pairs that appear
            in this documentation, however, are guaranteed to appear in successive
            versions, barring any changes in the Spoke API itself.

            The following fields are required:

            OrderId         - An internal order ID
            ShippingMethod  - The shipping method to use; must be one of 'FirstClass', 'PriorityMail', 'TrackedDelivery', 'SecondDay', 'Overnight'
            OrderInfo       - An OrderInfo object
            Cases           - A list of Case objects

            The following fields are optional:

            PackSlip - A PackSlip object
            Comments - A list of Comments objects
        '''
        shipping_method_map = dict(
            FirstClass      = 'FC',
            PriorityMail    = 'PM',
            TrackedDelivery = 'TD',
            SecondDay       = 'SD',
            Overnight       = 'ON',
        )
        _validate(kwargs,
            OrderId          = Required(), # XXX number
            ShippingMethod   = RequiredOnlyIfNot(['ShippingAccount', 'ShippingMethodId'], Enum('FirstClass', 'PriorityMail', 'TrackedDelivery', 'SecondDay', 'Overnight')),
            ShippingMethodId = RequiredOnlyIfNot(['ShippingMethod']),
            ShippingAccount  = RequiredOnlyIfNot(['ShippingMethod']),
            PackSlip         = Optional(Image),
            Comments         = Optional(Array(Comment)),
            OrderInfo        = Required(OrderInfo),
            Cases            = Required(Array(Case)),
        )
        if "ShippingMethod" in kwargs:
            kwargs['ShippingMethod'] = shipping_method_map[ kwargs['ShippingMethod'] ]
        # XXX OrderDate (date or datetime?)

        request = self._generate_request(
            RequestType = 'New',
            Order       = kwargs,
        )

        return self._send_request(request)


    def update(self, **kwargs):
        '''
            Updates an existing order.  If there is a problem
            updating the order, a SpokeError is raised.  Otherwise,
            a dictionary of key-value pairs of the same form as the
            one returned by new is returned.

            Required parameters:

            OrderId
            OrderInfo
        '''
        _validate(kwargs,
            OrderId   = Required(), # XXX number
            OrderInfo = Required(OrderInfo)
        )

        request = self._generate_request(
            RequestType = 'Update',
            Order       = kwargs,
        )

        return self._send_request(request)


    def cancel(self, OrderId):
        '''
            Cancels an existing order.  If there is a problem,
            raises a SpokeError.  Otherwise, returns a dictionary
            of the same form as the one returned by new.
        '''
        request = self._generate_request(
            RequestType = 'Cancel',
            Order       = dict(OrderId = OrderId),
        )

        return self._send_request(request)
