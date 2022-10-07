"""Platform for sensor integration."""
from operator import truediv
from pickle import FALSE
import string
from time import time
from typing import Any
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    DEVICE_CLASS_MONETARY,
    SensorEntity,
    SensorEntityDescription,
)

""" External Imports """
import requests
import json
import datetime
import logging
from enum import Enum

class MeassureUnit(Enum):
    kWh = True
    MWh = False

""" Constants """
NATIVE_UNIT_OF_MEASUREMENT = "Kč/kWh"
DEVICE_CLASS = "monetary"
COURSE_CODE = "EUR"
NAME = "Current OTE CZE PS"
DECIMAL_PLACE_AMOUNTH = 6
MEASSURE_UNIT = MeassureUnit.kWh

_LOGGER = logging.getLogger(__name__)

def BuildClasses():
    Classes = []

    for x in range(24):
        Classes.append(OTERateSensor_Attribut())

        Classes[x].AttIndex = x
        Classes[x].NativeUnits = NATIVE_UNIT_OF_MEASUREMENT
        Classes[x].DeviceClass = DEVICE_CLASS
        #Classes[x].CoastData = OTEDayData[x]
        Classes[x].DecPlace = DECIMAL_PLACE_AMOUNTH

    Classes.append(OTERateSensor_HighestPrice())
    Classes.append(OTERateSensor_LowestPrice())
    Classes.append(OTERateSensor_Actual())
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
        if Unit:
            RecalculateData.append((HourData * (float(ReqCourse[4].replace(",", ".")) / float(ReqCourse[2].replace(",", ".")))) / 1000.0)
            continue

        RecalculateData.append(HourData * (float(ReqCourse[4].replace(",", ".")) / float(ReqCourse[2].replace(",", "."))))

    return RecalculateData


class OTERateSensor_Actual(SensorEntity):

    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        self._value = None
        self._attr = None
        self._available = None

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
        return NATIVE_UNIT_OF_MEASUREMENT

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
            self.OTEData = RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
            self._value = round(GetActualEnergyPrice(self.OTEData), DECIMAL_PLACE_AMOUNTH)
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
            self._available = False   

class OTERateSensor_Attribut(SensorEntity):

            _value = None

            AttIndex = 0  
            DecPlace = 0
            NativeUnits = "" 
            DeviceClass = ""
            CoastData = 0.0

            def __init__(self):
                """Initialize the sensor."""

                self._value = None

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
                return self.NativeUnits

            @property
            def device_class(self):
                """Return the device class of the sensor."""
                return self.DeviceClass

            @property
            def available(self):
                """Return True if entity is available."""

                if len(self.CoastData) >= self.AttIndex + 1:
                    return True
                
                return False

            def update(self):
                """Fetch new state data for the sensor.
                This is the only method that should fetch new data for Home Assistant.
                """
                self._value = round(self.CoastData, self.DecPlace)
    
class OTERateSensor_HighestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        self.val = None
        self.avail = None

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
        return NATIVE_UNIT_OF_MEASUREMENT

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
        self.val = round(self.GetHighestPrice(), DECIMAL_PLACE_AMOUNTH) 

    def GetHighestPrice(self):
        OTEData = RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
        
        if len(OTEData) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return max(OTEData)
        
class OTERateSensor_LowestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        self.val = None
        self.avail = None

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
        return NATIVE_UNIT_OF_MEASUREMENT

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
        self.val = round(self.GetLowestPrice(), DECIMAL_PLACE_AMOUNTH) 

    def GetLowestPrice(self):
        OTEData = RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
        
        if len(OTEData) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return min(OTEData)
            

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities(BuildClasses(), update_before_add=True)