# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

__all__ = ['InvoiceLine']


class InvoiceLine:
    __name__ = 'account.invoice.line'

    list_price = fields.Numeric('List Price', digits=(16, 4),
        states={
            'invisible': ((Eval('type') != 'line') | ~Eval('product')),
            },
        depends=['type', 'product'])
    rebate = fields.Function(fields.Numeric('Rebate', digits=(16, 2),
            help='Rebate in percentage',
            states={
                'invisible': ((Eval('type') != 'line') | ~Eval('product')),
                },
            depends=['type', 'product']),
        'on_change_with_rebate', 'set_rebate')

    @fields.depends('list_price', 'unit_price')
    def on_change_with_rebate(self, name=None):
        if not self.list_price:
            rebate = Decimal(0)
        else:
            rebate = (1 - (self.unit_price or 0) / self.list_price) * 100
        return rebate.quantize(
            Decimal(str(10 ** -self.__class__.rebate.digits[1])))

    @fields.depends('list_price', 'rebate',
        # XXX: From on_change_with_amount
        # https://bugs.tryton.org/issue5191
        'type', 'quantity', 'invoice', '_parent_invoice.currency', 'currency')
    def on_change_rebate(self):
        if self.rebate is None or self.list_price is None:
            return
        unit_price = (1 - (self.rebate / 100)) * self.list_price
        self.unit_price = unit_price.quantize(
            Decimal(str(10 ** -self.__class__.unit_price.digits[1])))
        self.amount = self.on_change_with_amount()

    @classmethod
    def set_rebate(cls, invoices, name, value):
        pass
