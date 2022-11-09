"""Platform for sensor integration."""
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity

""" External Imports """
import logging
from . import OteLib
from . import GlobalData

#region Constant

DEVICE_CLASS = "monetary"
STATE_CLASS = "measurement"

#endregion

#region Configuration

CONF_COURSE_CODE = "course_code"
CONF_MEASURE_UNIT = "measure_unit"
CONF_DECIMAL_PLACES = "decimal_places"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_ADD_ATTRIBUTE_SENSORS_ACTUAL = "add_attribute_sensors_actual"
CONF_ADD_ATTRIBUTE_SENSORS_NEXT_DAY = "add_attribute_sensors_next_day"
CONF_ADD_ATTRIBUTES_TO_ACTUAL_PRICE = "add_attributes_to_actual_price"
CONF_HIGHEST_PRICE_FROM_HOUR = "highest_price_from_hour"
CONF_HIGHEST_PRICE_TO_HOUR = "highest_price_to_hour"
CONF_LOWEST_PRICE_FROM_HOUR = "lowest_price_from_hour"
CONF_LOWEST_PRICE_TO_HOUR = "lowest_price_to_hour"

#endregion

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COURSE_CODE): cv.string,
        vol.Required(CONF_MEASURE_UNIT): cv.positive_int,
        vol.Required(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Required(CONF_DECIMAL_PLACES): cv.positive_int,
        vol.Required(CONF_ADD_ATTRIBUTE_SENSORS_ACTUAL): cv.boolean,
        vol.Required(CONF_ADD_ATTRIBUTE_SENSORS_NEXT_DAY): cv.boolean,
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
    AddAttributeSensorsActual = config.get(CONF_ADD_ATTRIBUTE_SENSORS_ACTUAL)
    AddAttributeSensorsNextDay = config.get(CONF_ADD_ATTRIBUTE_SENSORS_NEXT_DAY)
    AddAttributesToActualPrice = config.get(CONF_ADD_ATTRIBUTES_TO_ACTUAL_PRICE)
    HighestPriceFromHour = config.get(CONF_HIGHEST_PRICE_FROM_HOUR)
    HighestPriceToHour = config.get(CONF_HIGHEST_PRICE_TO_HOUR)
    LowestPriceFromHour = config.get(CONF_LOWEST_PRICE_FROM_HOUR)
    LowestPriceToHour = config.get(CONF_LOWEST_PRICE_TO_HOUR)

    add_entities(BuildClasses(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributeSensorsActual, AddAttributesToActualPrice,
                              HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour, AddAttributeSensorsNextDay), update_before_add=True)

def BuildClasses(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributeSensorsActual, AddAttributesToActualPrice, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour, AddAttributeSensorsNextDay):
    Classes = []

    Classes.append(OTERateSensor_Actual(CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributesToActualPrice, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour, AddAttributeSensorsNextDay))

    if AddAttributeSensorsActual:
        for x in range(24):
            Classes.append(OTERateSensor_Attribut_Actual(x, DecimalPlaces, UnitOfMeasurement))

    if AddAttributeSensorsNextDay:
        for x in range(24):
            Classes.append(OTERateSensor_Attribut_Next_Day(x, DecimalPlaces, UnitOfMeasurement))

    Classes.append(OTERateSensor_HighestPrice(DecimalPlaces, UnitOfMeasurement))
    Classes.append(OTERateSensor_LowestPrice(DecimalPlaces, UnitOfMeasurement))
    Classes.append(OTERateSensor_HighestPriceHour())
    Classes.append(OTERateSensor_LowestPriceHour())
    return Classes

class OTERateSensor_Actual(SensorEntity):

    """Representation of a Sensor."""

    def __init__(self, CourseCode, MeasureUnit, DecimalPlaces, UnitOfMeasurement, AddAttributesToActualPrice, HighestPriceFromHour, HighestPriceToHour, LowestPriceFromHour, LowestPriceToHour, AddAttributeSensorsNextDay):
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
        self._addAttributeSensorsNextDay = AddAttributeSensorsNextDay
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
    def state_class (self):
        """Return True if entity is available."""
        return STATE_CLASS

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
            self.OTEData = OteLib.RecalculateActualOTEData(self._courseCode, self._measureUnit)
            self._value = round(OteLib.GetActualEnergyPrice(self.OTEData), self._decimalPlaces)

            GlobalData.OteData = self.OTEData
            GlobalData.ActualPrice = self._value

            if self._addAttributesToActualPrice:
                for x in range(len(GlobalData.OteData)):
                    self._valueDict[format(f"{x:02d}") + ":00 - " + format(f"{x:02d}") + ":59"] = GlobalData.OteData[x]

            self._available = True
        except:
            _LOGGER.exception("Error occured while retrieving data from ote-cr.cz.")
            self._available = False  

        try:
            OTEDataFiltredHP = []

            for i in range(len(GlobalData.OteData)):
                if i >= self._highestPriceFromHour and i <= self._highestPriceToHour:
                    OTEDataFiltredHP.append(GlobalData.OteData[i])

            GlobalData.OTEDataFiltredHP = OTEDataFiltredHP
            OTEDataFiltredLP = []

            for i in range(len(GlobalData.OteData)):
                if i >= self._lowestPriceFromHour and i <= self._lowestPriceToHour:
                    OTEDataFiltredLP.append(GlobalData.OteData[i])

            GlobalData.OTEDataFiltredLP = OTEDataFiltredLP
        except:
            _LOGGER.exception("Error occured while filtering data.")

        try:
            if (self._addAttributeSensorsNextDay):
                GlobalData.NextDayOteData = OteLib.RecalculateNextDayOTEData(self._courseCode, self._measureUnit)
        except:
            _LOGGER.exception("Error occured while retrieving next day data from ote-cr.cz.")

class OTERateSensor_Attribut_Actual(SensorEntity):

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
        return "OTE Energy CZK - Actual Attributs - "+ str(self.AttIndex)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Actual Attribut " + str(self.AttIndex)

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
    def state_class (self):
        """Return True if entity is available."""
        return STATE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""
        
        return self._available

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        if (GlobalData.OteData == None or len(GlobalData.OteData) <= 0): return

        try:

            if len(GlobalData.OteData) >= self.AttIndex + 1:
                self._available = True
            else:
                self._available = False

            self._value = round(GlobalData.OteData[self.AttIndex], self._decimalPlaces)
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
    def state_class (self):
        """Return True if entity is available."""
        return STATE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""

        return self.avail

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """

        if (GlobalData.OteData == None or len(GlobalData.OteData) <= 0): return
        if (GlobalData.OTEDataFiltredHP == None or len(GlobalData.OTEDataFiltredHP) <= 0): return

        self.val = round(self.GetHighestPrice(), self._decimalPlaces) 

    def GetHighestPrice(self):
        
        if len(GlobalData.OteData) < 1:
            self.avail = False
            return 0.0

        if len(GlobalData.OTEDataFiltredHP) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return max(GlobalData.OTEDataFiltredHP)
        
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
    def state_class (self):
        """Return True if entity is available."""
        return STATE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""

        return self.avail

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """

        if (GlobalData.OteData == None or len(GlobalData.OteData) <= 0): return
        if (GlobalData.OTEDataFiltredLP == None or len(GlobalData.OTEDataFiltredLP) <= 0): return

        self.val = round(self.GetLowestPrice(), self._decimalPlaces) 

    def GetLowestPrice(self):
        
        if len(GlobalData.OteData) < 1:
            self.avail = False
            return 0.0

        if len(GlobalData.OTEDataFiltredLP) < 1:
            self.avail = False
            return 0.0

        self.avail = True
        return min(GlobalData.OTEDataFiltredLP)

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

        if (GlobalData.OteData == None or len(GlobalData.OteData) <= 0): return
        if (GlobalData.OTEDataFiltredHP == None or len(GlobalData.OTEDataFiltredHP) <= 0): return

        try:
            if len(GlobalData.OTEDataFiltredHP) < 1:
                self.avail = False
                return 0.0

            MaxPrice = max(GlobalData.OTEDataFiltredHP)
            DataIndex = GlobalData.OteData.index(MaxPrice)
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

        if (GlobalData.OteData == None or len(GlobalData.OteData) <= 0): return
        if (GlobalData.OTEDataFiltredLP == None or len(GlobalData.OTEDataFiltredLP) <= 0): return

        try:
            if len(GlobalData.OTEDataFiltredLP) < 1:
                self.avail = False
                return

            MinPrice = min(GlobalData.OTEDataFiltredLP)
            DataIndex = GlobalData.OteData.index(MinPrice)
            self.val = format(f"{DataIndex:02d}") + ":00 - " + format(f"{DataIndex:02d}") + ":59"
            self.avail = True
        except:
            self.avail = False  

class OTERateSensor_Attribut_Next_Day(SensorEntity):

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
        return "OTE Energy CZK - Next Day Attributs - "+ str(self.AttIndex)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "OTE Energy CZK - Next Day Attribut " + str(self.AttIndex)

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
    def state_class (self):
        """Return True if entity is available."""
        return STATE_CLASS

    @property
    def available(self):
        """Return True if entity is available."""
        
        return self._available

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        if (GlobalData.NextDayOteData == None or len(GlobalData.NextDayOteData) <= 0): return

        try:

            if len(GlobalData.NextDayOteData) >= self.AttIndex + 1:
                self._available = True
            else:
                self._available = False

            self._value = round(GlobalData.NextDayOteData[self.AttIndex], self._decimalPlaces)
        except:
            _LOGGER.exception("Error in attribute sensors")
            