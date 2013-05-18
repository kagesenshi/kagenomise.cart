from Acquisition import aq_inner
from zope.interface import Interface
from five import grok
from zope.component import getMultiAdapter
from Products.CMFCore.interfaces import IContentish
from plone.app.layout.viewlets import interfaces as manager
from kagenomise.cart.interfaces import IProductSpecific

grok.templatedir('templates')

class CartMetadata(grok.Viewlet):
    grok.context(IContentish)
    grok.viewletmanager(manager.IHtmlHead)
    grok.template('cartmetadata')
    grok.layer(IProductSpecific)

    def available(self):
        return True
