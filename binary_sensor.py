import logging
import datetime 
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

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([OTERateSensor_HighestPrice_Active(), OTERateSensor_LowestPrice_Active()], update_before_add=True)

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
        try:
            OTEData = RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
            MaxPrice = max(OTEData)
            ActualPrice = GetActualEnergyPrice(OTEData)

            if MaxPrice == ActualPrice:
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
        try:
            OTEData = RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
            MaxPrice = min(OTEData)
            ActualPrice = GetActualEnergyPrice(OTEData)

            if MaxPrice == ActualPrice:
                self._active = True
            else:
                self._active = False
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz or recalculating data.")
            self._available = False