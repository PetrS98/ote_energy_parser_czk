"""Platform for sensor integration."""
from operator import truediv
from pickle import FALSE
import string
from time import time
from typing import Any
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    DEVICE_CLASS_MONETARY,
    SensorEntity,
    SensorEntityDescription,
)

""" External Imports """
import logging
from enum import Enum
import requests
import datetime

class MeasureUnit(Enum):
    kWh = True
    MWh = False

""" Constants """
DEVICE_CLASS = "monetary"

CONF_COURSE_CODE = "course_code"
CONF_MEASURE_UNIT = "measure_unit"
CONF_DECIMAL_PLACES = "decimal_places"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COURSE_CODE): cv.string,
        vol.Required(CONF_MEASURE_UNIT): cv.positive_int,
        vol.Required(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Required(CONF_DECIMAL_PLACES): cv.positive_int
    }
)

def BuildClasses(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement):
    Classes = []

    for x in range(24):
        Classes.append(OTERateSensor_Attribut(x, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement))

    Classes.append(OTERateSensor_HighestPrice(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement))
    Classes.append(OTERateSensor_LowestPrice(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement))
    Classes.append(OTERateSensor_Actual(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement))
    Classes.append(OTERateSensor_HighestPriceHour(CourseCode, MeasureUnit))
    Classes.append(OTERateSensor_LowestPriceHour(CourseCode, MeasureUnit))
    return Classes

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
        if Unit == 0:
            RecalculateData.append(HourData * (float(ReqCourse[4].replace(",", ".")) / float(ReqCourse[2].replace(",", "."))))
        elif Unit == 1:
            RecalculateData.append((HourData * (float(ReqCourse[4].replace(",", ".")) / float(ReqCourse[2].replace(",", ".")))) / 1000.0)
        else:
            RecalculateData.append((HourData * (float(ReqCourse[4].replace(",", ".")) / float(ReqCourse[2].replace(",", ".")))) / 1000000.0)

    return RecalculateData

class OTERateSensor_Actual(SensorEntity):

    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement):
        """Initialize the sensor."""

        self._value = None
        self._attr = None
        self._available = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces
        self._unitOfMeasurement = UnitOfMeasurement

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return "OTE Energy CZK - Actual Price - MAIN"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Actual Price"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return self._unitOfMeasurement

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            self.OTEData = RecalculateOTEData(self._courseCode, self._measureUnit)
            self._value = round(GetActualEnergyPrice(self.OTEData), self._decimalPlaces)
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
            self._available = False   

class OTERateSensor_Attribut(SensorEntity):

    """Representation of a Sensor.""" 

    def __init__(self, AttributIndex, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement):
        """Initialize the sensor."""

        self._value = None
        self._available = None
        self.AttIndex = AttributIndex
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces  
        self._unitOfMeasurement = UnitOfMeasurement

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return "OTE Energy CZK - Attributs - "+ str(self.AttIndex)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Attribut " + str(self.AttIndex)

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return self._unitOfMeasurement

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""
        
        return self._available

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        OTEData = RecalculateOTEData(self._courseCode, self._measureUnit)

        if len(OTEData) >= self.AttIndex + 1:
            self._available = True
        else:
            self._available = False

        self._value = round(OTEData[self.AttIndex], self._decimalPlaces)
    
class OTERateSensor_HighestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces
        self._unitOfMeasurement = UnitOfMeasurement

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return "OTE Energy CZK - Highest Price - MAIN"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Highest Price"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.val

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return self._unitOfMeasurement

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""

        return self.avail

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.val = round(self.GetHighestPrice(), self._decimalPlaces) 

    def GetHighestPrice(self):
        OTEData = RecalculateOTEData(self._courseCode, self._measureUnit)
        
        if len(OTEData) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return max(OTEData)
        
class OTERateSensor_LowestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces
        self._unitOfMeasurement = UnitOfMeasurement

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return "OTE Energy CZK - Lowest Price - MAIN"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Lowest Price"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.val

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return self._unitOfMeasurement

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""

        return self.avail

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.val = round(self.GetLowestPrice(), self._decimalPlaces) 

    def GetLowestPrice(self):
        OTEData = RecalculateOTEData(self._courseCode, self._measureUnit)
        
        if len(OTEData) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return min(OTEData)

class OTERateSensor_HighestPriceHour(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return "OTE Energy CZK - Highest Price Hour - MAIN"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Highest Price Hour"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.val

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""

        return self.avail

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            OTEData = RecalculateOTEData(self._courseCode, self._measureUnit)
            MaxPrice = max(OTEData)
            DataIndex = OTEData.index(MaxPrice)
            self.val = format(f"{DataIndex:02d}") + ":00 - " + format(f"{DataIndex:02d}") + ":59"
            self.avail = True
        except:
            self.avail = False

class OTERateSensor_LowestPriceHour(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return "OTE Energy CZK - Lowest Price Hour - MAIN"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Lowest Price Hour"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.val

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""

        return self.avail

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            OTEData = RecalculateOTEData(self._courseCode, self._measureUnit)
            MinPrice = min(OTEData)
            DataIndex = OTEData.index(MinPrice)
            self.val = format(f"{DataIndex:02d}") + ":00 - " + format(f"{DataIndex:02d}") + ":59"
            self.avail = True
        except:
            self.avail = False   

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    CourseCode = config.get(CONF_COURSE_CODE)
    MeasureUnit = config.get(CONF_MEASURE_UNIT)
    UnitOfMeasurement = config.get(CONF_UNIT_OF_MEASUREMENT)
    DecimalPlaces = config.get(CONF_DECIMAL_PLACES)

    add_entities(BuildClasses(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement), update_before_add=True)