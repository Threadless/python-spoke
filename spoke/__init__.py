'''
    Python interface to the Spoke API.  This is the reference documentation; see
    the included README for a higher level overview.
'''

from lxml import etree
import requests
from StringIO import StringIO

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
        d[k] = validator(v)

    validation_spec = dict((k, v) for k, v in validation_spec.items() if v.is_required)
    if validation_spec:
        first_key = sorted(validation_spec.keys())[0]
        raise ValidationError('Missing required parameter "%s"' % first_key)


# Actual spoke classes

class Image(object):
    '''
        Represents an image resource.  Use for PrintImage, QcImage, Logo, and PackSlip.
    '''

    def __init__(self, **kwargs):
        '''
            Requires: ImageType, Url
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
            Requires: Type (one of 'Printer', 'Packaging'), CommentText
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
            May take parameters Text1 - Text6.
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
            May specify DisplayOnPackingSlip, CurrencySymbol, TaxCents, ShippingCents, DiscountCents
        '''
        _validate(kwargs,
            DisplayOnPackingSlip = Optional(),
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
            State
            PostalCode
            CountryCode
            OrderDate
            PhoneNumber

            The following parameters are optional:

            Address2
            PurchaseOrderNumber
            GiftMessage
            PackSlipCustomInfo
            Prices
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
            CaseType       = Required(Enum('ph4bt', 'iph4tough', 'iph4vibe', 'iph3bt',
                'iph3tough', 'ipt4gbt', 'bb9900bt', 'kindlefirebt', 'ssgs3vibe',
                'iph5bt', 'iph5vibe', 'iph5xtreme', 'ipad4bt', 'ipadminitough',
                'ipt5gbt', 'ssgn2tough', 'bbz10tough', 'ssgs4bt', 'ssgs4vibe')),
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

class Transport(object):
    def __init__(self, url):
        self.url = url

    def send(self, request):
        res = requests.post(url, data=request)
        res.raise_for_status()
        return res.content

ARRAY_CHILDREN_NAMES = dict(
    Cases    = 'CaseInfo',
    Comments = 'Comment',
)

PRODUCTION_URL = 'http://api.spokecustom.com/order/submit'
STAGING_URL    = 'http://api-staging.spokecustom.com/order/submit'

class Spoke(object):
    '''
        The main spoke request object.  It contains any
        request parameters that won't change between requests.
    '''

    def __init__(self, **kwargs):
        '''
            The following fields are required:

            production
            transport
            Customer
            Key

            The following fields are optional:

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
            element      = etree.Element(tag_name)
            element.text = str(node)
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
        return etree.tostring(request, pretty_print=True)

    def _send_request(self, request):
        res    = self.transport.send(request)
        tree   = etree.parse(StringIO(res))
        result = tree.xpath('//result')[0].text

        if result == 'Success':
            immc_id = int(tree.xpath('//immc_id')[0].text)
            return dict(immc_id = immc_id)
        else:
            message = tree.xpath('//message')[0].text
            raise SpokeError(message)

    def new(self, **kwargs):
        '''
            The following fields are required:

            OrderId
            ShippingMethod
            OrderInfo
            Cases

            The following fields are optional:

            PackSlip
            Comments

            Throws an exception if the parameters don't validate

            Returns a dictionary of data.  It contains (at least) the following key-value pairs:

            immc_id
        '''
        shipping_method_map = dict(
            FirstClass      = 'FC',
            PriorityMail    = 'PM',
            TrackedDelivery = 'TD',
            SecondDay       = 'SD',
            Overnight       = 'ON',
        )
        _validate(kwargs,
            OrderId        = Required(), # XXX number
            ShippingMethod = Required(Enum('FirstClass', 'PriorityMail', 'TrackedDelivery', 'SecondDay', 'Overnight')),
            PackSlip       = Optional(Image),
            Comments       = Optional(Array(Comment)),
            OrderInfo      = Required(OrderInfo),
            Cases          = Required(Array(Case)),
        )
        kwargs['ShippingMethod'] = shipping_method_map[ kwargs['ShippingMethod'] ]
        # XXX OrderDate (date or datetime?)

        request = self._generate_request(
            RequestType = 'New',
            Order       = kwargs,
        )

        return self._send_request(request)


    def update(self, **kwargs):
        '''
            Both OrderId and OrderInfo are required.
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
            OrderId is the self-assigned order ID that corresponds
            to your order.
        '''
        request = self._generate_request(
            RequestType = 'Cancel',
            Order       = dict(OrderId = OrderId),
        )

        return self._send_request(request)
