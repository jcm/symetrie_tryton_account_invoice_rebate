#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import copy
from decimal import Decimal
from trytond.model import Model, fields
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond.pool import PoolMeta, Pool

__all__ = ['InvoiceLine']

class InvoiceLine:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice.line'

    list_price = fields.Numeric('List Price', digits=(16, 4),
        states={
            'invisible': ((Eval('type') != 'line') | ~Eval('product')),
            'readonly': True, # to get it saved by the client
            },
        depends=['type', 'product'])
    rebate = fields.Function(fields.Numeric('Rebate', digits=(16, 2),
            help='Rebate in percentage',
#            on_change=['list_price', 'rebate'],
            states={
                'invisible': ((Eval('type') != 'line') | ~Eval('product')),
                },
            depends=['type', 'product']),
        'get_rebate', 'set_rebate')

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()
        for field in (cls.quantity, cls.unit):
            if field.on_change:
                field.on_change = copy.copy(field.on_change)
            else:
                field.on_change = []
            for value in ('list_price', 'unit_price'):
                if value not in field.on_change:
                    field.on_change.append(value)
#        cls._rpc.setdefault('on_change_quantity', False)
#        cls._rpc.setdefault('on_change_unit', False)
        if cls.unit_price.on_change:
            cls.unit_price.on_change = copy.copy(cls.unit_price.on_change)
        else:
            cls.unit_price.on_change = []
        for fname in ('unit_price', 'list_price'):
            if fname not in cls.unit_price.on_change:
                cls.unit_price.on_change.append(fname)
#        cls._rpc.setdefault('on_change_unit_price', False)
        if 'rebate' not in cls.amount.on_change_with:
            cls.amount= copy.copy(cls.amount)
            cls.amount.on_change_with = copy.copy(cls.amount.on_change_with)
            cls.amount.on_change_with.append('rebate')
        cls._reset_columns()

    @fields.depends('list_price', 'rebate')
    def on_change_rebate(cls):
        if cls.rebate is None or cls.list_price is None:
            return result
        unit_price = (1 - (cls.rebate / 100)) * cls.list_price
        unit_price.quantize(Decimal(str(10 ** -cls.unit_price.digits[1])))
        cls.unit_price = unit_price

    def _compute_rebate(cls, list_price, unit_price):
        if not unit_price:
            unit_price = Decimal('0')
        if not list_price:
            value = Decimal('0')
        else:
            value = (1 - unit_price / list_price) * 100
        return value.quantize(Decimal(str(10 ** -cls.rebate.digits[1])))

    def get_rebate(cls, ids, name):
        result = {}
        for line in cls.browse(ids):
            result[line.id] = cls._compute_rebate(line.list_price,
                line.unit_price)
        return result

    def set_rebate(cls, ids, name, value):
        pass

    def _compute_list_price(cls, product, currency, date, type_):
        pool = Pool()
        user_obj = pool.get('res.user')
        date_obj = pool.get('ir.date')
        currency_obj = pool.get('currency.currency')

        today = date_obj.today()
        if type_ in ('in_invoice', 'in_credit_note'):
            list_price = product.cost_price
        else:
            list_price = product.list_price
        user = user_obj.browse(Transaction().user)
        if currency and user.company:
            if user.company.currency.id != currency.id:
                date = date or today
                with Transaction().set_context(date=date):
                    list_price = currency_obj.compute(user.company.currency.id,
                        list_price, currency.id)
        return list_price

    @fields.depends('product', 'unit_price', 'list_price')
    def on_change_product(cls):
        product_obj = Pool().get('product.product')
        currency_obj = Pool().get('currency.currency')

        result = super(InvoiceLine, cls).on_change_product(values)
        list_price = Decimal('0')
        if values.get('product'):
            product = product_obj.browse(values['product'])
            currency = None
            if values.get('_parent_invoice.currency'):
                currency = currency_obj.browse(
                    values['_parent_invoice.currency'])
            list_price = cls._compute_list_price(product, currency,
                values.get('_parent_invoice.currency_date'),
                values.get('_parent_invoice.type') or
                values.get('invoice_type'))
        result['list_price'] = list_price
        result['rebate'] = cls._compute_rebate(list_price,
            result['unit_price'])

    @fields.depends('quantity', 'unit_price', 'list_price')
    def on_change_quantity(cls):
        try:
            super(InvoiceLine, cls).on_change_quantity()
        except AttributeError:
            pass
#            result = {}
        cls.rebate = cls._compute_rebate(cls.list_price, cls.unit_price)

    @fields.depends('unit_price', 'list_price')
    def on_change_unit_price(cls):
        try:
            super(InvoiceLine, cls).on_change_unit_price()
        except AttributeError:
            pass
#            result = {}
        cls.rebate = cls._compute_rebate(cls.list_price, cls.unit_price)
