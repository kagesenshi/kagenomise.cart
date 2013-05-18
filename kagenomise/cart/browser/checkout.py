from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility
from kagenomise.cart.interfaces import ICheckoutProcessor
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from plone.directives import dexterity, form
from kagenomise.cart import MessageFactory as _
import z3c.form.button

import re
grok.templatedir('templates')

optionspattern = re.compile('(.*):(.*)')

class ICheckoutSchema(form.Schema):

    recipient_name = schema.TextLine(
        title=_(u'Name'),
    )

    recipient_email = schema.TextLine(
        title=_(u'Email'),
    )

    recipient_phone = schema.TextLine(
        title=_(u'Phone'),
    )

    shipment_address = schema.Text(
        title=_(u'Shipment Address'),
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

    def tablerows(self):
        rows = []

        for item in self.items():
            row = {
                'title': '%s (%s)' % (item['name'], item['size']),
                'quantity': item['quantity'],
                'unit_price': '%s %s' % (item['currency'], item['price']),
                'total': '%s %s' % (item['currency'], item['price'] * item['quantity'])
            }
            rows.append(row)
        return rows

    def items(self):
        items = []

        item_count = int(self.request.get('itemCount', 0))
        
        for i in range(1, item_count+1):
            item = {
                'name': self.request.get('item_name_%s' % i),
                'price': float(self.request.get('item_price_%s' % i)),
                'quantity': int(self.request.get('item_quantity_%s' % i)),
                'currency': self.request.get('currency'),
            }

            options = self.request.get('item_options_%s' % i).strip()
            if options:
                for entry in options.split(','):
                    match = optionspattern.match(entry)
                    if match:
                        key, value = match.groups()
                        item[key.strip()] = value.strip()

            items.append(item)

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
            self.status = self.formErrorsMessage
            return

        checkoutdata = {
            'recipient_name': data['recipient_name'],
            'shipment_address': data['shipment_address'],
            'recipient_email': data['recipient_email'],
            'recipient_phone': data['recipient_phone'],
            'items': self.items()
        }

        checkout = getUtility(ICheckoutProcessor)
        checkout.checkout(checkoutdata)
