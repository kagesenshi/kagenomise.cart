from zope.interface import Interface, implements

class IProductSpecific(Interface):
    pass

class ICheckoutEvent(Interface):
    pass

class CheckoutEvent(object):
    implements(ICheckoutEvent)

    def __init__(self, context, data):
        self.context = context
        self.data = data

class IItemTitle(Interface):
    
    def getTitle(data):
        pass
