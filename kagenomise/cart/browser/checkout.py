from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility
from kagenomise.cart.interfaces import CheckoutEvent, IItemTitle
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from plone.directives import dexterity, form
from kagenomise.cart import MessageFactory as _
import z3c.form.button
from zope.event import notify
import re
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.interfaces import IContentish

grok.templatedir('templates')

optionspattern = re.compile('(.*):(.*)')

class ICheckoutSchema(form.Schema):

    recipient_name = schema.TextLine(
        title=_(u'Name'),
    )

    recipient_email = schema.TextLine(
        title=_(u'Email'),
    )

    verify_email = schema.TextLine(
        title=_(u'Verify Email'),
        description=_(u'Type your email address here again for verification'),
    )

    recipient_phone = schema.TextLine(
        title=_(u'Phone'),
    )

    shipping_address = schema.Text(
        title=_(u'Shipping Address'),
    )

class Checkout(form.SchemaForm):
    grok.context(ISiteRoot)
    grok.name('checkout')
    grok.require('zope2.View')
    grok.template('checkout')

    label = _(u'Checkout')
    enable_form_tabbing = False
    ignoreContext = True
    css_class = 'kagenomise-checkout-form'
    schema = ICheckoutSchema

    template = ViewPageTemplateFile('templates/checkout.pt')

    def status(self):
        messages = IStatusMessage(self.request)
        return messages.show()

    def tablerows(self):
        rows = []

        for item in self.items():
            if item.has_key('path'):
                obj = self.context.unrestrictedTraverse(str(item['path']))
                title = IItemTitle(obj).getTitle(item)
            else:
                title = item['name']
            row = {
                'title': title,
                'quantity': item['quantity'],
                'unit_price': '%s %.2f' % (item['currency'], item['price']),
                'total': '%s %.2f' % (item['currency'], item['price'] * item['quantity'])
            }
            rows.append(row)
        return rows

    def price_total(self):
        total = 0.0
        for item in self.items():
            total += item['price'] * item['quantity']
        return '%s %.2f' % (self.request.get('currency'), total)

    def items(self):
        items = []

        item_count = int(self.request.get('itemCount', 0))
        
        for i in range(1, item_count+1):
            item = {
                'name': self.request.get('item_name_%s' % i),
                'price': float(self.request.get('item_price_%s' % i)),
                'quantity': int(self.request.get('item_quantity_%s' % i)),
                'currency': self.request.get('currency'),
                'meta_type': 'product'
            }

            options = self.request.get('item_options_%s' % i).strip()
            if options:
                for entry in options.split(','):
                    match = optionspattern.match(entry)
                    if match:
                        key, value = match.groups()
                        if key not in ['meta_type']:
                            item[key.strip()] = value.strip()

            items.append(item)

        # shipment
        # XXX: FIXME: shipment right now is calculated only for clothing
        totalshirts = 0
        for i in items:
            totalshirts += item['quantity']

        if totalshirts >= 3:
            items.append({
                'name': 'FREE Shipment',
                'price': 0.0,
                'quantity': 1,
                'currency': self.request.get('currency'),
                'meta_type': 'shipment'
            })
        elif totalshirts in [1, 2]:
            items.append({
                'name': 'Shipment',
                'price': 7.0,
                'quantity': 1,
                'currency': self.request.get('currency'),
                'meta_type': 'shipment'
            })
        return items

    def cart_hiddeninput(self):
        elements = []

        item_count = int(self.request.get('itemCount', 0))

        def _h(name, value):
            return '<input type="hidden" name="%s" value="%s"/>' % (name, value)

        for i in range(1, item_count+1):
            for k in ['item_name', 'item_options',
                        'item_quantity', 'item_price']:
                key = '%s_%s' % (k, i)
                value = self.request.get(key)
                elements.append(_h(key, value))

        for k in ['currency','itemCount','shipping','tax','taxRate']:
            value = self.request.get(k)
            elements.append(_h(k, value))

        return '\n'.join(elements)

    @z3c.form.button.buttonAndHandler(_(u'Submit'), name='submit')
    def submit(self, action):
        data, errors = self.extractData()
        if errors: 
            return

        if data['recipient_email'] != data['verify_email']:
            IStatusMessage(self.request).add(u'Emails did not match',
                            type='error')
            return

        if not self.context.restrictedTraverse('@@captcha').verify():
            IStatusMessage(self.request).add(u'Invalid Captcha', type='error')
            return

        checkoutdata = {
            'recipient_name': data['recipient_name'],
            'shipping_address': data['shipping_address'],
            'recipient_email': data['recipient_email'],
            'recipient_phone': data['recipient_phone'],
            'items': self.items()
        }

        notify(CheckoutEvent(self.context, checkoutdata))

class CheckoutSuccess(grok.View):
    grok.context(ISiteRoot)
    grok.name('checkout_success')
    grok.require('zope2.View')
    grok.template('checkout_success')

class DefaultItemTitle(grok.Adapter):
    grok.context(IContentish)
    grok.implements(IItemTitle)

    def __init__(self, context):
        self.context = context

    def getTitle(self, data):
        return self.context.Title()

