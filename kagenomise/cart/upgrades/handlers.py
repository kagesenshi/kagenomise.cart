from collective.grok import gs
from Products.CMFCore.utils import getToolByName

# -*- extra stuff goes here -*- 


@gs.upgradestep(title=u'Upgrade kagenomise.cart to 1001',
                description=u'Upgrade kagenomise.cart to 1001',
                source='1', destination='1001',
                sortkey=1, profile='kagenomise.cart:default')
def to1001(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-kagenomise.cart.upgrades:to1001')
