from lxml import etree
import requests
from StringIO import StringIO

__all__ = ['Case', 'Comment', 'Image', 'OrderInfo', 'PackSlipCustomInfo', 'Spoke', 'ValidationError', 'SpokeError']

# Validation code

class ValidationError(Exception):
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
    for k, v in d.iteritems():
        validator = validation_spec.pop(k, None)
        if validator is None:
            raise ValidationError('parameter "%s" not allowed' % k)
        d[k] = validator(v)

    validation_spec = dict((k, v) for k, v in validation_spec.iteritems() if v.is_required)
    if validation_spec:
        first_key = sorted(validation_spec.keys())[0]
        raise ValidationError('Missing required parameter "%s"' % first_key)


# Actual spoke classes

class Image(object):
    '''

    '''

    def __init__(self, **kwargs):
        _validate(kwargs,
            ImageType = Required(),
            Url       = Required(),
        )
        self.__dict__ = kwargs


class Comment(object):
    '''

    '''

    def __init__(self, **kwargs):
        _validate(kwargs,
            Type        = Required(Enum('Printer', 'Packaging')),
            CommentText = Required(),
        )
        self.__dict__ = kwargs


class PackSlipCustomInfo(object):
    '''

    '''

    def __init__(self, **kwargs):
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
    '''

    def __init__(self, **kwargs):
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
    '''

    def __init__(self, **kwargs):
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
    def __init__(self, **kwargs):
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
    pass

class Spoke(object):
    '''
        The main spoke requestor object
    '''

    def __init__(self, **kwargs):
        _validate(kwargs,
            production = Required(),
            Customer   = Required(),
            Key        = Required(),
            Logo       = Optional(Image),
        )
        self.__dict__ = kwargs

    def _generate_tree(self, tag_name, serializers, node):
        if isinstance(node, list):
            elements = etree.Element(tag_name)
            for child in node:
                # XXX hardcoded tag_name
                elements.append(self._generate_tree('CaseInfo', serializers, child))
            return elements
        elif isinstance(node, dict):
            parent = etree.Element(tag_name)

            for tag_name, subtree in node.iteritems():
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

    def new(self, **kwargs):
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

        request = self._generate_request(
            RequestType = 'New',
            Order       = kwargs,
        )

    def update(self, **kwargs):
        _validate(kwargs,
            OrderId   = Required(), # XXX number
            OrderInfo = Required(OrderInfo)
        )

        request = self._generate_request(
            RequestType = 'Update',
            Order       = kwargs,
        )

    def cancel(self, OrderId):
        request = self._generate_request(
            RequestType = 'Cancel',
            Order       = dict(OrderId = OrderId),
        )
