# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import datetime, timedelta

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def next_delivery_window_start_datetime(self, from_date=None):
        """Returns the next starting datetime in a preferred delivery window.
        If from_date is already in a delivery window, from_date is "the next"

        :param from_date: Datetime object (Leave empty to use now())
        :return: Datetime object
        """
        self.ensure_one()
        if not from_date:
            from_date = datetime.now()
        if self.is_in_delivery_window(from_date):
            return from_date
        # Sort by start time to ensure the window we'll find will be the first
        # one for the weekday
        windows = self.delivery_time_window_ids.sorted()
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
                if weekday not in win.time_window_weekday_ids:
                    continue
                # If we're here, it means we found the first time window for
                # this weekday
                start_time = win.get_time_window_start_time()
                return from_date.replace(
                    hour=start_time.hour, minute=start_time.minute, second=0
                ) + timedelta(days=i)
