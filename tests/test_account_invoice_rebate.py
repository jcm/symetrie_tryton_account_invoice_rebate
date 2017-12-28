# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountInvoiceRebateTestCase(ModuleTestCase):
    'Test AccountInvoiceRebate module'
    module = 'symetrie_account_invoice_rebate'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountInvoiceRebateTestCase))
    return suite
