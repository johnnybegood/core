"""This component provides support for Lares motion/door events."""
import asyncio
import datetime
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    EVENT_DATA_RECEIVED,
    ZONE_STATUS_ALARM,
    ZONE_STATUS_NOT_USED,
    ZONE_BYPASS_ON,
)
from .base import LaresBase

_LOGGER = logging.getLogger(__name__)

DEFAULT_DEVICE_CLASS = "motion"
DOOR_DEVICE_CLASS = "door"


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up binary sensors attached to a Lares alarm device from a config entry."""

    client = LaresBase(config_entry.data)
    descriptions = await client.zoneDescriptions()
    zones = await client.zones()

    async_add_devices(
        [LaresSensor(client, descriptions[idx], zone) for idx, zone in enumerate(zones)]
    )


class LaresSensor(BinarySensorEntity):
    """An implementation of a Lares door/window/motion sensor."""

    def __init__(self, client, description, zone):
        """Initialize a the switch."""
        BinarySensorEntity.__init__(self)

        self._event_state = False
        self._last_motion = datetime.datetime.min
        self._client = client
        self._description = description
        self._zone = zone

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"lares_zones_{self._description}"

    @property
    def name(self):
        """Return the name of this camera."""
        return self._description

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._zone["status"] == ZONE_STATUS_ALARM

    @property
    def available(self):
        """Return True if entity is available."""
        return (
            self._zone["status"] != ZONE_STATUS_NOT_USED
            or self._zone["status"] == ZONE_BYPASS_ON
        )

    @property
    def device_class(self):
        """Return the class of this device."""
        return DEFAULT_DEVICE_CLASS