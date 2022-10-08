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
import lib.OteLib as OteLib
import logging
from enum import Enum

class MeassureUnit(Enum):
    kWh = True
    MWh = False

""" Constants """
NATIVE_UNIT_OF_MEASUREMENT = "Kč/kWh"
DEVICE_CLASS = "monetary"
COURSE_CODE = "EUR"
DECIMAL_PLACE_AMOUNTH = 6
MEASSURE_UNIT = MeassureUnit.kWh

_LOGGER = logging.getLogger(__name__)

def BuildClasses():
    Classes = []

    for x in range(24):
        Classes.append(OTERateSensor_Attribut(x))

    Classes.append(OTERateSensor_HighestPrice())
    Classes.append(OTERateSensor_LowestPrice())
    Classes.append(OTERateSensor_Actual())
    return Classes

class OTERateSensor_Actual(SensorEntity):

    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        self._value = None
        self._attr = None
        self._available = None

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
            self.OTEData = OteLib.RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
            self._value = round(OteLib.GetActualEnergyPrice(self.OTEData), DECIMAL_PLACE_AMOUNTH)
            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
            self._available = False   

class OTERateSensor_Attribut(SensorEntity):

    """Representation of a Sensor.""" 

    def __init__(self, AttributIndex):
        """Initialize the sensor."""

        self._value = None
        self._available = None
        self.AttIndex = AttributIndex

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
        OTEData = OteLib.RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)

        if len(OTEData) >= self.AttIndex + 1:
            self._available = True
        else:
            self._available = False

        self._value = round(OTEData[self.AttIndex], DECIMAL_PLACE_AMOUNTH)
    
class OTERateSensor_HighestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        self.val = None
        self.avail = None

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
        OTEData = OteLib.RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
        
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
        OTEData = OteLib.RecalculateOTEData(COURSE_CODE, MEASSURE_UNIT)
        
        if len(OTEData) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return min(OTEData)
            

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities(BuildClasses(), update_before_add=True)