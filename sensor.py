"""Platform for sensor integration."""
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity

""" External Imports """
import logging
from . import OteLib
from . import ActualData

""" Constants """
DEVICE_CLASS = "monetary"

CONF_COURSE_CODE = "course_code"
CONF_MEASURE_UNIT = "measure_unit"
CONF_DECIMAL_PLACES = "decimal_places"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_ADD_ATTRIBUTE_SENSORS = "add_attribute_sensors"
CONF_ADD_ATTRIBUTES_TO_ACTUAL_PRICE = "add_attributes_to_actual_price"
CONF_HIGHEST_PRICE_FROM_HOUR = "highest_price_from_hour"
CONF_HIGHEST_PRICE_TO_HOUR = "highest_price_to_hour"
CONF_LOWEST_PRICE_FROM_HOUR = "lowest_price_from_hour"
CONF_LOWEST_PRICE_TO_HOUR = "lowest_price_to_hour"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COURSE_CODE): cv.string,
        vol.Required(CONF_MEASURE_UNIT): cv.positive_int,
        vol.Required(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Required(CONF_DECIMAL_PLACES): cv.positive_int,
        vol.Required(CONF_ADD_ATTRIBUTE_SENSORS): cv.boolean,
        vol.Required(CONF_ADD_ATTRIBUTES_TO_ACTUAL_PRICE): cv.boolean,
        vol.Required(CONF_HIGHEST_PRICE_FROM_HOUR): cv.positive_int,
        vol.Required(CONF_HIGHEST_PRICE_TO_HOUR): cv.positive_int,
        vol.Required(CONF_LOWEST_PRICE_FROM_HOUR): cv.positive_int,
        vol.Required(CONF_LOWEST_PRICE_TO_HOUR): cv.positive_int
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    CourseCode = config.get(CONF_COURSE_CODE)
    MeasureUnit = config.get(CONF_MEASURE_UNIT)
    UnitOfMeasurement = config.get(CONF_UNIT_OF_MEASUREMENT)
    DecimalPlaces = config.get(CONF_DECIMAL_PLACES)
    AddAttributeSensors = config.get(CONF_ADD_ATTRIBUTE_SENSORS)
    AddAttributesToActualPrice = config.get(CONF_ADD_ATTRIBUTES_TO_ACTUAL_PRICE)
    HighestPriceFromHour = config.get(CONF_HIGHEST_PRICE_FROM_HOUR)
    HighestPriceToHour = config.get(CONF_HIGHEST_PRICE_TO_HOUR)
    LowestPriceFromHour = config.get(CONF_LOWEST_PRICE_FROM_HOUR)
    LowestPriceToHour = config.get(CONF_LOWEST_PRICE_TO_HOUR)

    add_entities(BuildClasses(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributeSensors, AddAttributesToActualPrice,
                              HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour), update_before_add=True)

def BuildClasses(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributeSensors, AddAttributesToActualPrice, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour):
    Classes = []

    Classes.append(OTERateSensor_Actual(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributesToActualPrice, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour))

    if AddAttributeSensors:

        for x in range(24):
            Classes.append(OTERateSensor_Attribut(x, DecimalPlaces, UnitOfMeasurement))

    Classes.append(OTERateSensor_HighestPrice(DecimalPlaces, UnitOfMeasurement))
    Classes.append(OTERateSensor_LowestPrice(DecimalPlaces, UnitOfMeasurement))
    Classes.append(OTERateSensor_HighestPriceHour())
    Classes.append(OTERateSensor_LowestPriceHour())
    return Classes

class OTERateSensor_Actual(SensorEntity):

    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributesToActualPrice, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour):
        """Initialize the sensor."""

        self._value = None
        self._attr = None
        self._available = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces
        self._unitOfMeasurement = UnitOfMeasurement
        self._addAttributesToActualPrice = AddAttributesToActualPrice
        self._highestPriceFromHour = HighestPriceFromHour
        self._highestPriceToHour = HighestPriceToHour
        self._lowestPriceFromHour = LowestPriceFromHour
        self._lowestPriceToHour = LowestPriceToHour
        self._valueDict = dict()

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
    def extra_state_attributes(self):
        if self._addAttributesToActualPrice:
            return self._valueDict

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            self.OTEData = OteLib.RecalculateOTEData(self._courseCode, self._measureUnit)
            self._value = round(OteLib.GetActualEnergyPrice(self.OTEData), self._decimalPlaces)

            ActualData.OteData = self.OTEData
            ActualData.ActualPrice = self._value

            if self._addAttributesToActualPrice:
                for x in range(len(self.OTEData)):
                    self._valueDict[format(f"{x:02d}") + ":00 - " + format(f"{x:02d}") + ":59"] = self.OTEData[x]

            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
            self._available = False  

        try:
            OTEDataFiltred = []

            for i in range(len(self.OTEData)):
                if i >= self._highestPriceFromHour and i <= self._highestPriceToHour:
                    OTEDataFiltred.append(self.OTEData[i])

            ActualData.OTEDataFiltredHP = OTEDataFiltred
            OTEDataFiltred.clear()

            for i in range(len(ActualData.OteData)):
                if i >= self._lowestPriceFromHour and i <= self._lowestPriceToHour:
                    OTEDataFiltred.append(ActualData.OteData[i])

            ActualData.OTEDataFiltredLP = OTEDataFiltred

        except:
            _LOGGER.exception("Error occured while filtering data.")

class OTERateSensor_Attribut(SensorEntity):

    """Representation of a Sensor.""" 

    def __init__(self, AttributIndex, DecimalPlaces, UnitOfMeasurement):
        """Initialize the sensor."""

        self._value = None
        self._available = None
        self.AttIndex = AttributIndex
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

        if (ActualData.OteData == None or len(ActualData.OteData) <= 0): return

        try:

            if len(ActualData.OteData) >= self.AttIndex + 1:
                self._available = True
            else:
                self._available = False

            self._value = round(ActualData.OteData[self.AttIndex], self._decimalPlaces)
        except:
            _LOGGER.exception("Error in attribute sensors")
    
class OTERateSensor_HighestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, DecimalPlaces, UnitOfMeasurement):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
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

        if (ActualData.OteData == None or len(ActualData.OteData) <= 0): return
        if (ActualData.OTEDataFiltredHP == None or len(ActualData.OTEDataFiltredHP) <= 0): return

        self.val = round(self.GetHighestPrice(), self._decimalPlaces) 

    def GetHighestPrice(self):
        
        if len(ActualData.OteData) < 1:
            self.avail = False
            return 0.0

        if len(ActualData.OTEDataFiltredHP) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return max(ActualData.OTEDataFiltredHP)
        
class OTERateSensor_LowestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, DecimalPlaces, UnitOfMeasurement):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
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

        if (ActualData.OteData == None or len(ActualData.OteData) <= 0): return
        if (ActualData.OTEDataFiltredLP == None or len(ActualData.OTEDataFiltredLP) <= 0): return

        self.val = round(self.GetLowestPrice(), self._decimalPlaces) 

    def GetLowestPrice(self):
        
        if len(ActualData.OteData) < 1:
            self.avail = False
            return 0.0

        if len(ActualData.OTEDataFiltredLP) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return min(ActualData.OTEDataFiltredLP)

class OTERateSensor_HighestPriceHour(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        self.val = None
        self.avail = None

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

        if (ActualData.OteData == None or len(ActualData.OteData) <= 0): return
        if (ActualData.OTEDataFiltredHP == None or len(ActualData.OTEDataFiltredHP) <= 0): return

        try:
            if len(ActualData.OTEDataFiltredHP) < 1:
                self.avail = False
                return 0.0

            MaxPrice = max(ActualData.OTEDataFiltredHP)
            DataIndex = ActualData.OteData.index(MaxPrice)
            self.val = format(f"{DataIndex:02d}") + ":00 - " + format(f"{DataIndex:02d}") + ":59"
            self.avail = True
        except:
            self.avail = False

class OTERateSensor_LowestPriceHour(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        self.val = None
        self.avail = None

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

        if (ActualData.OteData == None or len(ActualData.OteData) <= 0): return
        if (ActualData.OTEDataFiltredLP == None or len(ActualData.OTEDataFiltredLP) <= 0): return

        try:
            if len(ActualData.OTEDataFiltredLP) < 1:
                self.avail = False
                return

            MinPrice = min(ActualData.OTEDataFiltredLP)
            DataIndex = ActualData.OteData.index(MinPrice)
            self.val = format(f"{DataIndex:02d}") + ":00 - " + format(f"{DataIndex:02d}") + ":59"
            self.avail = True
        except:
            self.avail = False   