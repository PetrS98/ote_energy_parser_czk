import logging
from . import GlobalData

from homeassistant.components.binary_sensor import BinarySensorEntity

""" Constants """
DEVICE_CLASS = "monetary"

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([OTERateSensor_HighestPrice_Active(), OTERateSensor_LowestPrice_Active()], update_before_add=True)

class OTERateSensor_HighestPrice_Active(BinarySensorEntity):
    def __init__(self):
        """Initialize the sensor."""
        
        self._available = None
        self._active = None

        self.update()

    @property
    def name(self):
        return "OTE Energy CZK - Highest Price Active"

    @property
    def is_on(self):
        return self._active

    @property
    def available(self):
        return self._available

    @property
    def device_class(self):
        return DEVICE_CLASS

    @property
    def unique_id(self):
        return "OTE Energy CZK - Highest Price - Active MAIN"

    def update(self):

        if (GlobalData.OTEDataFiltredHP == None or len(GlobalData.OTEDataFiltredHP) <= 0): return

        try:
            if len(GlobalData.OTEDataFiltredHP) < 1:
                self._available = False
                return

            MaxPrice = max(GlobalData.OTEDataFiltredHP)

            if abs(MaxPrice - GlobalData.ActualPrice) < 0.000001:
                self._active = True
            else:
                self._active = False  
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz or recalculating data.")
            self._available = False

class OTERateSensor_LowestPrice_Active(BinarySensorEntity):
    def __init__(self):
        """Initialize the sensor."""
        
        self._available = None
        self._active = None

        self.update()

    @property
    def name(self):
        return "OTE Energy CZK - Lowest Price Active"

    @property
    def is_on(self):
        return self._active

    @property
    def available(self):
        return self._available

    @property
    def device_class(self):
        return DEVICE_CLASS

    @property
    def unique_id(self):
        return "OTE Energy CZK - Lowest Price - Active MAIN"

    def update(self):

        if (GlobalData.OTEDataFiltredLP == None or len(GlobalData.OTEDataFiltredLP) <= 0): return

        try:
            if len(GlobalData.OTEDataFiltredLP) < 1:
                self._available = False
                return

            MinPrice = min(GlobalData.OTEDataFiltredLP)

            if abs(MinPrice - GlobalData.ActualPrice) < 0.000001:
                self._active = True
            else:
                self._active = False
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz or recalculating data.")
            self._available = False