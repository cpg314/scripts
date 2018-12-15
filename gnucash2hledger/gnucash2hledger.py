#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gnucash2ledger

Usage:
  gnucash2ledger <input>
  gnucash2ledger <input> [--out <file>]

"""
import records
import arrow
from docopt import docopt
import sys


def account_name(db, guid):
    a = db.query("select * from accounts where guid='{}'".format(guid)).all()
    if len(a) > 0:
        a = a[0]
        p = account_name(db, a.parent_guid)
        if p is None or p == "Root Account":
            return a.name
        else:
            return p + ":" + a.name


# Currencies
def exportCurrencies(db, f):
    currencies = []
    for c in db.query("select * from commodities where namespace='CURRENCY'"):
        currencies.append({"name": c.mnemonic, "id": c.guid})
    print("; Default currency", file=f)
    print("D CHF 1'000.00", file=f)
    return currencies


# Accounts
def exportAccounts(db, currencies, f):
    accounts = []
    print("\n; Accounts\n", file=f)
    for a in db.query("select * from accounts where account_type!='ROOT' and commodity_scu!=1"):
        accounts.append({
            "name": account_name(db, a.guid),
            "id": a.guid,
            "currency": next(filter(lambda c: c['id'] == a.commodity_guid, currencies))["name"],
            "type": a.account_type, "virtual": bool(a.placeholder)})
        print(u"; account {}".format(accounts[-1]["name"]), file=f)
        print(u"; currency {}".format(accounts[-1]["currency"]), file=f)
        print("", file=f)
    return accounts


# Transactions
def exportTransactions(db, accounts, currencies, f):
    print("\n; Transactions\n", file=f)
    for t in db.query("SELECT transactions.* FROM transactions ORDER BY post_date ASC"):
        # Date
        date = arrow.get(t.post_date, "YYYYMMDDHHmmss").to("local")  # Important to convert timezones
        print(date.format('YYYY/MM/DD') + " " + t.description, file=f)
        # Currency
        t_currency = next(filter(lambda c: c['id'] == t.currency_guid, currencies))["name"]
        # Splits
        for s in db.query("SELECT * from splits WHERE tx_guid='{}' AND value_num!=0".format(t.guid)):
            # Account
            account = next(filter(lambda a: a["id"] == s.account_guid, accounts))
            print(u"    {:<60} ".format(account_name(db, s.account_guid)), end="", file=f)
            # Amounts
            s_currency = account["currency"]
            print("{} {:> }".format(s_currency if (t_currency != "CHF" or s_currency != "CHF") else ' ' * 3, s.quantity_num / 100.0), end="", file=f)
            print("@@ {} {:>}".format(t_currency, s.value_num / 100.0) if t_currency != s_currency else "", file=f)
            # Memo
            if s.memo != "":
                print(u"    ; {}".format(s.memo), file=f)
        print("", file=f)


def main():
    args = docopt(__doc__)
    output = args["<file>"]
    if output is not None:
        f = open(output, "w")
    else:
        f = sys.stdout
    db = records.Database('sqlite:///' + args["<input>"])
    currencies = exportCurrencies(db, f)
    # Recurring
    # for s in db.query("SELECT * FROM schedxactions"):
    #     print arrow.get(s.start_date,"YYYYMMDD"),arrow.get(s.last_occur,"YYYYMMDD"),s.instance_count
    accounts = exportAccounts(db, currencies, f)
    exportTransactions(db, accounts, currencies, f)
    f.close()


if __name__ == "__main__":
    main()
