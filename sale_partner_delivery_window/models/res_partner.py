# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import datetime, timedelta

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def next_delivery_window_start_datetime(self):
        self.ensure_one()
        now = datetime.now()
        if self.is_in_delivery_window(now):
            return now
        windows = self.get_delivery_windows()
        # Loop over weekdays starting from today in order to find next delivery
        # window
        for i, weekday_number in enumerate(range(now.weekday(), now.weekday() + 6)):
            # target weekday is the day number as returned by weekday method
            target_weekday = weekday_number % 7
            # Filter out windows for this day
            weekday = self.env["time.weekday"].search(
                [("name", "=", target_weekday)], order="start"
            )
            day_windows = windows.filtered(lambda w: w.weekday_ids in weekday)
            for dw in day_windows:
                start_time = dw.get_start_time()
                # As soon as now in in a window, return the start datetime
                if start_time <= now.time() <= dw.get_end_time():
                    return now.replace(
                        hour=start_time.hour, minute=start_time.minute
                    ) + timedelta(days=i)
