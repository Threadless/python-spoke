# Spoke

Spoke (formerly known as Case-Mate) is a company that makes cases for phones
and tablets (ed: among other things).

They are kind enough to expose an API for others to use, and
this is a Python library that interacts with that API.  The API is XML-based (but
not SOAP).  The structure of this library is meant to reflect the structure of the
API calls and closely as possible; you should be able to read the API docs and use
this library comfortably.  Only parameters that do not change between requests are
omitted from each call; for example:

## Example API XML:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Request>
<Customer>CustomerName</Customer>
<RequestType>New</RequestType>
<Key>1234554321123450</Key>
<Logo>
  <ImageType>jpg</ImageType>
  <Url>http://MyLogoImage.com/logo.jpg</Url>
</Logo>
<Order>
  <OrderId>CustomerOrderNumber</OrderId>
  <ShippingMethod>FC</ShippingMethod>
  <PackSlip>
    <ImageType>jpg</ImageType>
    <Url>http://PackingSlipImage.com/packslip.jpg</Url>
  </PackSlip>
  <Comments>
    <Comment>
      <Type>Packaging</Type>
      <CommentText>Custom Sticker</CommentText>
    </Comment>
  </Comments>
  <OrderInfo>
    <FirstName>John</FirstName>
    <LastName>Customer</LastName>
    <Address1>1 Main Street</Address1>
    <Address2></Address2>
    <City>Atlanta</City>
    <State>GA</State>
    <PostalCode>30084</PostalCode>
    <CountryCode>US</CountryCode>
    <OrderDate>11/08/2011</OrderDate>
    <PhoneNumber>404-555-9000</PhoneNumber>
    <PurchaseOrderNumber>PO</PurchaseOrderNumber>
    <GiftMessage>Thanks for your purchase!</GiftMessage>
    <PackSlipCustomInfo>
      <Text1></Text1>
      <Text2></Text2>
      <Text3></Text3>
      <Text4></Text4>
      <Text5></Text5>
      <Text6></Text6>
    </PackSlipCustomInfo>
    <Prices>
      <DisplayOnPackingSlip>Yes</DisplayOnPackingSlip>
      <CurrencySymbol>$</CurrencySymbol>
      <TaxCents>245</TaxCents>
      <ShippingCents>450</ShippingCents>
      <DiscountCents>500</DiscountCents>
    </Prices>
  </OrderInfo>
  <Cases>
    <CaseInfo>
      <CaseId>10001</CaseId>
      <CaseType>iph4bt</CaseType>
      <Quantity>1</Quantity>
      <QcImage>
        <ImageType>jpg</ImageType>
        <Url>http://qcimage.com</Url>
      </QcImage>
      <Prices>
        <CurrencySymbol>$</CurrencySymbol>
        <RetailCents>1000</RetailCents>
        <DiscountCents>0</DiscountCents>
      </Prices>
    </CaseInfo>
    <CaseInfo>
      <CaseId>10002</CaseId>
      <CaseType>iph4tough</CaseType>
      <Quantity>1</Quantity>
      <PrintImage>
        <ImageType>tiff</ImageType>
        <Url>http://printimage.com</Url>
      </PrintImage>
      <QcImage>
        <ImageType>jpg</ImageType>
        <Url>http://qcimage.com</Url>
      </QcImage>
      <Prices>
        <CurrencySymbol>$</CurrencySymbol>
        <RetailCents>1500</RetailCents>
        <DiscountCents>500</DiscountCents>
      </Prices>
      <Comments>
        <Comment>
          <Type>Packaging</Type>
          <CommentText>Other Custom Sticker</CommentText>
        </Comment>
      </Comments>
    </CaseInfo>
  </Cases>
</Order>
</Request>
```

## Equivalent Python Code:

### Setup

```python
import spoke

s = spoke.Spoke(
    Customer='CustomerName',
    Key='1234554321123450',
    Logo={
        'ImageType' : 'jpg',
        'Url' : 'http://threadless.com/logo.jpg',
    },
)

### Create a new order:

result = s.new(
    OrderId='CustomerOrderNumber',
    ShippingMethod='FirstClass',
    PackSlip={
        'ImageType' : 'jpg',
        'Url' : 'http://PackingSlipImage.com/packslip.jpg',
    },
    Comments=[{
        'Type' : 'Packaging',
        'CommentText' : 'Custom Sticker',
    }],
    OrderInfo={
        'FirstName' : 'John',
        'LastName' : 'Customer',
        'Address1' : '1 Main Street',
        'City' : 'Atlanta',
        'State' : 'GA',
        'PostalCode' : '30084',
        'CountryCode' : 'US',
        'OrderDate' : '11/08/2011',
        'PhoneNumber' : '4045559000',
        'PurchaseOrderNumber' : 'PO',
        'GiftMessage' : 'Thanks for your purchase',
        'Prices' : {
            'DisplayOnPackingSlip' : 'Yes',
            'CurrencySymbol' : '$',
            'TaxCents' : '245',
            'ShippingCents' : '450',
            'DiscountCents' : '500',
        },
    },
    Cases=[{
        'CaseId' : '10001',
        'CaseType' : 'iph4bt',
        'Quantity' : '1',
        'QcImage' : {
            'ImageType' : 'jpg',
            'Url' : 'http://qcimage.com',
        },
        'Prices' : {
            'CurrencySymbol' : '$',
            'RetailCents' : '1000',
            'DiscountCents' : '0',
        },
    }, {
        'CaseId' : '10002',
        'CaseType' : 'iph4tough',
        'Quantity' : '1',
        'PrintImage' : {
            'ImageType' : 'tiff',
            'Url' : 'http://printimage.com',
        },
        'QcImage' : {
            'ImageType' : 'jpg',
            'Url' : 'http://qcimage.com',
        },
        'Prices' : {
            'CurrencySymbol' : '$',
            'RetailCents' : '1500',
            'DiscountCents' : '500',
        },
        'Comments' : {
            'Type' : 'Packaging',
            'CommentText' : 'Other Custom Sticker',
        }
    }]
)
```

### Update shipping info:

```python
s.update(
    OrderId='CustomerOrderNumber',
    OrderInfo={
        'FirstName': 'Bob',
        # ...
    }
)
```

### Cancel an order:

```python
s.cancel('CustomerOrderNumber')
```

# Conventions

Upper-case keyword arguments are passed directly to the API; lower-case ones
fiddle with the library's configuration.  Strings or numbers may be used.
Date objects may be specified for OrderDate, and instead of the two-character
shorthand specified by the API, ShippingMethod may be specified as a more human
readable string.
