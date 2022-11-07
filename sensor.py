"""Platform for sensor integration."""
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity

""" External Imports """
import logging
from . import OteLib

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

def BuildClasses(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributeSensors, AddAttributesToActualPrice, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour):
    Classes = []

    if AddAttributeSensors:

        for x in range(24):
            Classes.append(OTERateSensor_Attribut(x, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement))

    Classes.append(OTERateSensor_HighestPrice(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, HighestPriceFromHour, HighestPriceToHour))
    Classes.append(OTERateSensor_LowestPrice(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, LowestPriceFromHour, LowestPriceToHour))
    Classes.append(OTERateSensor_Actual(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributesToActualPrice))
    Classes.append(OTERateSensor_HighestPriceHour(CourseCode, MeasureUnit, HighestPriceFromHour, HighestPriceToHour))
    Classes.append(OTERateSensor_LowestPriceHour(CourseCode, MeasureUnit, LowestPriceFromHour, LowestPriceToHour))
    return Classes

class OTERateSensor_Actual(SensorEntity):

    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributesToActualPrice):
        """Initialize the sensor."""

        self._value = None
        self._attr = None
        self._available = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces
        self._unitOfMeasurement = UnitOfMeasurement
        self._addAttributesToActualPrice = AddAttributesToActualPrice
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

            if self._addAttributesToActualPrice:
                for x in range(len(self.OTEData)):
                    self._valueDict[format(f"{x:02d}") + ":00 - " + format(f"{x:02d}") + ":59"] = self.OTEData[x]

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
        OTEData = OteLib.RecalculateOTEData(self._courseCode, self._measureUnit)

        if len(OTEData) >= self.AttIndex + 1:
            self._available = True
        else:
            self._available = False

        self._value = round(OTEData[self.AttIndex], self._decimalPlaces)
    
class OTERateSensor_HighestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, HighestPriceFromHour, HighestPriceToHour):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces
        self._unitOfMeasurement = UnitOfMeasurement
        self._highestPriceFromHour = HighestPriceFromHour
        self._highestPriceToHour = HighestPriceToHour

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
        OTEData = OteLib.RecalculateOTEData(self._courseCode, self._measureUnit)
        OTEDataFiltred = []
        
        if len(OTEData) < 1:
            self.avail = False
            return 0.0

        for i in range(len(OTEData)):
            if i >= self._highestPriceFromHour and i <= self._highestPriceToHour:
                OTEDataFiltred.append(OTEData[i])

        if len(OTEDataFiltred) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return max(OTEDataFiltred)
        
class OTERateSensor_LowestPrice(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, LowestPriceFromHour, LowestPriceToHour):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._decimalPlaces = DecimalPlaces
        self._unitOfMeasurement = UnitOfMeasurement
        self._lowestPriceFromHour = LowestPriceFromHour
        self._lowestPriceToHour = LowestPriceToHour

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
        OTEData = OteLib.RecalculateOTEData(self._courseCode, self._measureUnit)
        OTEDataFiltred = []
        
        if len(OTEData) < 1:
            self.avail = False
            return 0.0

        for i in range(len(OTEData)):
            if i >= self._lowestPriceFromHour and i <= self._lowestPriceToHour:
                OTEDataFiltred.append(OTEData[i])

        if len(OTEDataFiltred) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return min(OTEDataFiltred)

class OTERateSensor_HighestPriceHour(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, HighestPriceFromHour, HighestPriceToHour):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._highestPriceFromHour = HighestPriceFromHour
        self._highestPriceToHour = HighestPriceToHour

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
            OTEData = OteLib.RecalculateOTEData(self._courseCode, self._measureUnit)
            OTEDataFiltred = []

            for i in range(len(OTEData)):
                if i >= self._highestPriceFromHour and i <= self._highestPriceToHour:
                    OTEDataFiltred.append(OTEData[i])

            if len(OTEDataFiltred) < 1:
                self.avail = False
                return 0.0

            MaxPrice = max(OTEDataFiltred)
            DataIndex = OTEData.index(MaxPrice)
            self.val = format(f"{DataIndex:02d}") + ":00 - " + format(f"{DataIndex:02d}") + ":59"
            self.avail = True
        except:
            self.avail = False

class OTERateSensor_LowestPriceHour(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, LowestPriceFromHour, LowestPriceToHour):
        """Initialize the sensor."""

        self.val = None
        self.avail = None
        self._courseCode = CourseCode
        self._measureUnit = MeasureUnit
        self._lowestPriceFromHour = LowestPriceFromHour
        self._lowestPriceToHour = LowestPriceToHour

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
            OTEData = OteLib.RecalculateOTEData(self._courseCode, self._measureUnit)
            OTEDataFiltred = []

            for i in range(len(OTEData)):
                if i >= self._lowestPriceFromHour and i <= self._lowestPriceToHour:
                    OTEDataFiltred.append(OTEData[i])

            if len(OTEDataFiltred) < 1:
                self.avail = False
                return

            MinPrice = min(OTEDataFiltred)
            DataIndex = OTEData.index(MinPrice)
            self.val = format(f"{DataIndex:02d}") + ":00 - " + format(f"{DataIndex:02d}") + ":59"
            self.avail = True
        except:
            self.avail = False   

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
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
