# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

from decimal import Decimal

def charge(price: Decimal, qty: int) -> Decimal:
    return price * qty
