import logging
import datetime 

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import BinarySensorEntity

import requests
from enum import Enum

class MeassureUnit(Enum):
    kWh = True
    MWh = False

""" Constants """
DEVICE_CLASS = "monetary"
COURSE_CODE = "EUR"
MEASSURE_UNIT = MeassureUnit.kWh

CONF_HIGHEST_PRICE_FROM_HOUR = "highest_price_from_hour"
CONF_HIGHEST_PRICE_TO_HOUR = "highest_price_to_hour"
CONF_LOWEST_PRICE_FROM_HOUR = "lowest_price_from_hour"
CONF_LOWEST_PRICE_TO_HOUR = "lowest_price_to_hour"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HIGHEST_PRICE_FROM_HOUR): cv.positive_int,
        vol.Required(CONF_HIGHEST_PRICE_TO_HOUR): cv.positive_int,
        vol.Required(CONF_LOWEST_PRICE_FROM_HOUR): cv.positive_int,
        vol.Required(CONF_LOWEST_PRICE_TO_HOUR): cv.positive_int
    }
)

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    HighestPriceFromHour = config.get(CONF_HIGHEST_PRICE_FROM_HOUR)
    HighestPriceToHour = config.get(CONF_HIGHEST_PRICE_TO_HOUR)
    LowestPriceFromHour = config.get(CONF_LOWEST_PRICE_FROM_HOUR)
    LowestPriceToHour = config.get(CONF_LOWEST_PRICE_TO_HOUR)

    add_entities([OTERateSensor_HighestPrice_Active(HighestPriceFromHour, HighestPriceToHour), OTERateSensor_LowestPrice_Active(LowestPriceFromHour, LowestPriceToHour)], update_before_add=True)

def GetDataFromOTE():
    """Return data from ote-cr in [EUR/MWh]"""

    date = datetime.datetime.now()
    params = dict (date = date.strftime('%Y-%m-%d'))

    data = []
    response = requests.get(url="https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data", params=params).json()

    for i in range(len(response['data']['dataLine'][1]['point'])):
        data.append(float(response['data']['dataLine'][1]['point'][i]['y']))

    return data

def GetCZKCourses():
    """Return all czech croun cusrses. Data structure: Country|Currency|Amount|Code|Course"""

    data = []
    response = requests.get(url="https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt").text

    items = response.split("\n")

    del items[0]
    del items[0]
    del items[len(items) -1]

    for item in items:
        lineData = item.split("|")
        data.append(lineData)

    return data

def GetActualEnergyPrice(OTEData):
    DateTime = datetime.datetime.now()

    return OTEData[DateTime.hour]

def RecalculateOTEData(CourseCode, Unit):
    ReqCourse = []
    RecalculateData = []

    CZKCourses = GetCZKCourses()
    OTEDayDataEUR = GetDataFromOTE()

    for course in CZKCourses:
        if CourseCode == course[3]:
            ReqCourse = course
            break

    for HourData in OTEDayDataEUR:
        if Unit:
            RecalculateData.append((HourData * (float(ReqCourse[4].replace(",", ".")) / float(ReqCourse[2].replace(",", ".")))) / 1000.0)
            continue

        RecalculateData.append(HourData * (float(ReqCourse[4].replace(",", ".")) / float(ReqCourse[2].replace(",", "."))))

    return RecalculateData

class OTERateSensor_HighestPrice_Active(BinarySensorEntity):
    def __init__(self, HighestPriceFromHour, HighestPriceToHour):
        """Initialize the sensor."""
        
        self._available = None
        self._active = None
        self._highestPriceFromHour = HighestPriceFromHour
        self._highestPriceToHour = HighestPriceToHour

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
        try:
            OTEData = RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
            OTEDataFiltred = []

            for i in range(len(OTEData)):
                if i >= self._highestPriceFromHour and i <= self._highestPriceToHour:
                    OTEDataFiltred.append(OTEData[i])

            if len(OTEDataFiltred) < 1:
                self._available = False
                return

            MaxPrice = max(OTEDataFiltred)
            ActualPrice = GetActualEnergyPrice(OTEData)

            if abs(MaxPrice - ActualPrice) < 0.000001:
                self._active = True
            else:
                self._active = False  
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz or recalculating data.")
            self._available = False

class OTERateSensor_LowestPrice_Active(BinarySensorEntity):
    def __init__(self, LowestPriceFromHour, LowestPriceToHour):
        """Initialize the sensor."""
        
        self._available = None
        self._active = None
        self._lowestPriceFromHour = LowestPriceFromHour
        self._lowestPriceToHour = LowestPriceToHour

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
        try:
            OTEData = RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
            OTEDataFiltred = []

            for i in range(len(OTEData)):
                if i >= self._lowestPriceFromHour and i <= self._lowestPriceToHour:
                    OTEDataFiltred.append(OTEData[i])

            if len(OTEDataFiltred) < 1:
                self._available = False
                return

            MinPrice = min(OTEDataFiltred)
            ActualPrice = GetActualEnergyPrice(OTEData)

            if abs(MinPrice - ActualPrice) < 0.000001:
                self._active = True
            else:
                self._active = False
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz or recalculating data.")
            self._available = False