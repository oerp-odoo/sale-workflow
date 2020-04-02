# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import datetime, timedelta

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def next_delivery_window_start_datetime(self, from_date=None):
        self.ensure_one()
        if not from_date:
            from_date = datetime.now()
        if self.is_in_delivery_window(from_date):
            return from_date
        windows = self.delivery_time_window_ids
        # Loop over weekdays starting from today in order to find next delivery
        # window
        for i, weekday_number in enumerate(range(from_date.weekday(), from_date.weekday() + 6)):
            # target weekday is the day number as returned by weekday method
            target_weekday = weekday_number % 7
            # Filter out windows for this day
            weekday = self.env["time.weekday"].search(
                [("name", "=", target_weekday)]
            )
            for win in windows:
                if weekday not in win.weekday_ids:
                    continue
                start_time = win.get_start_time()
                # As soon as now in in a window, return the start datetime
                if start_time <= from_date.time() <= win.get_end_time():
                    return from_date.replace(
                        hour=start_time.hour, minute=start_time.minute, second=0
                    ) + timedelta(days=i)
