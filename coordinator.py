"""Polling coordinator for the ONT."""

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SCAN_INTERVAL_SECONDS
from .ont_status import OntClient, OntError

_LOGGER = logging.getLogger(__name__)


class OntCoordinator(DataUpdateCoordinator[dict[str, str]]):
    def __init__(self, hass, client: OntClient, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Telekom Glasfaser Modem 1",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, str]:
        try:
            return await self.client.async_get_status()
        except OntError as exc:
            raise UpdateFailed(str(exc)) from exc

