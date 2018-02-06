======================
Account Invoice Rebate
======================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> today = datetime.date.today()

Activate account_invoice_rebate and invoice::

    >>> config = activate_modules('account_invoice_rebate')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> template = ProductTemplate()
    >>> template.name = "Product"
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('15')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> product, = template.products
    >>> product.cost_price = Decimal('5')
    >>> product.save()

Invoice products::

    >>> Invoice = Model.get('account.invoice')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.type = 'out'
    >>> invoice_line = invoice.lines.new()
    >>> invoice_line.product = product
    >>> invoice_line.quantity = 1
    >>> invoice_line.list_price = Decimal('15')
    >>> invoice_line.unit_price = Decimal('15')
    >>> invoice_line.rebate
    Decimal('0.00')
    >>> invoice.save()
    >>> invoice_line, = invoice.lines
    >>> invoice_line.rebate
    Decimal('0.00')
    >>> invoice_line.unit_price = Decimal('13')
    >>> invoice_line.rebate
    Decimal('13.33')
    >>> invoice.save()
    >>> invoice_line, = invoice.lines
    >>> invoice_line.rebate
    Decimal('13.33')
    >>> invoice_line.rebate = Decimal('0')
    >>> invoice_line.unit_price
    Decimal('15.0000')
    >>> invoice_line.rebate = Decimal('50')
    >>> invoice_line.unit_price
    Decimal('7.5000')
