from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from kagenomise.cart import MessageFactory as _

class ICartPortlet(IPortletDataProvider):
    """
    Define your portlet schema here
    """
    pass

class Assignment(base.Assignment):
    implements(ICartPortlet)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def title(self):
        return _('Cart Portlet')

class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('templates/cartportlet.pt')

    @property
    def available(self):
        return True

class AddForm(base.AddForm):
    form_fields = form.Fields(ICartPortlet)
    label = _(u"Add Cart Portlet")
    description = _(u"")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(ICartPortlet)
    label = _(u"Edit Cart Portlet")
    description = _(u"")
