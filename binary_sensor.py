import logging
from . import OteLib
from . import GlobalData

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import BinarySensorEntity

#region Constant

DEVICE_CLASS = "monetary"

#endregion

#region Configuration

CONF_COURSE_CODE = "course_code"
CONF_HIGHEST_PRICE_FROM_HOUR = "highest_price_from_hour"
CONF_HIGHEST_PRICE_TO_HOUR = "highest_price_to_hour"
CONF_LOWEST_PRICE_FROM_HOUR = "lowest_price_from_hour"
CONF_LOWEST_PRICE_TO_HOUR = "lowest_price_to_hour"

#endregion

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COURSE_CODE): cv.string,
        vol.Required(CONF_HIGHEST_PRICE_FROM_HOUR): cv.positive_int,
        vol.Required(CONF_HIGHEST_PRICE_TO_HOUR): cv.positive_int,
        vol.Required(CONF_LOWEST_PRICE_FROM_HOUR): cv.positive_int,
        vol.Required(CONF_LOWEST_PRICE_TO_HOUR): cv.positive_int
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    CourseCode = config.get(CONF_COURSE_CODE)
    HighestPriceFromHour = config.get(CONF_HIGHEST_PRICE_FROM_HOUR)
    HighestPriceToHour = config.get(CONF_HIGHEST_PRICE_TO_HOUR)
    LowestPriceFromHour = config.get(CONF_LOWEST_PRICE_FROM_HOUR)
    LowestPriceToHour = config.get(CONF_LOWEST_PRICE_TO_HOUR)

    add_entities([OTERateSensor_HighestPrice_Active(CourseCode, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour), OTERateSensor_LowestPrice_Active()], update_before_add=True)

def GetOteData(courseCode, HPFromHour, HPToHour,  LPFromHour, LPToHour):

    try:
        GlobalData.OteData = OteLib.RecalculateActualOTEData(courseCode, True)
        GlobalData.ActualPrice = OteLib.GetActualEnergyPrice(GlobalData.OteData)
    except:
        _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")

    try:
        OTEDataFiltred = []

        for i in range(len(GlobalData.OteData)):
            if i >= HPFromHour and i <= HPToHour:
                OTEDataFiltred.append(GlobalData.OteData[i])

        GlobalData.OTEDataFiltredHP = OTEDataFiltred
        OTEDataFiltred.clear()

        for i in range(len(GlobalData.OteData)):
            if i >= LPFromHour and i <= LPToHour:
                OTEDataFiltred.append(GlobalData.OteData[i])

        GlobalData.OTEDataFiltredLP = OTEDataFiltred
    except:
        _LOGGER.exception("Error occured while filtering data.")

class OTERateSensor_HighestPrice_Active(BinarySensorEntity):
    def __init__(self, CourseCode, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour):
        """Initialize the sensor."""
        
        self._available = None
        self._active = None
        self._courseCode = CourseCode
        self._highestPriceFromHour = HighestPriceFromHour
        self._highestPriceToHour = HighestPriceToHour
        self._lowestPriceFromHour = LowestPriceFromHour
        self._lowestPriceToHour = LowestPriceToHour

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

        GetOteData(self._courseCode, self._highestPriceFromHour, self._highestPriceToHour, self._lowestPriceFromHour, self._lowestPriceToHour)

        if (GlobalData.OTEDataFiltredHP == None or len(GlobalData.OTEDataFiltredHP) <= 0): 
            self._available = False
            return

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

        if (GlobalData.OTEDataFiltredLP == None or len(GlobalData.OTEDataFiltredLP) <= 0): 
            self._available = False
            return

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
            