from collective.grok import gs
from kagenomise.cart import MessageFactory as _

@gs.importstep(
    name=u'kagenomise.cart', 
    title=_('kagenomise.cart import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('kagenomise.cart.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
