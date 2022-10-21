# OTE Energy Cost Sensor for Home Assistant

This is an integration providing price of energy from ote-cr.cz, attributes as solo sensors, lowest price sensor and highest price sensor.
And binary status sensors for lowest and highest price active.

### Installation

If you're using HACS - feel free to add https://github.com/PetrS98/ote_energy_parser_czk as custom repository.

Once you've installed the custom integration, add the following to your `configuration.yaml` file:

```yaml
sensor:
  - platform: ote_energy_parser_czk         # Name of the addons folder
    course_code: EUR                        # Currency code (ISO 4217) to be converted to CZK [string]
    measure_unit: 1                         # 0 = MWh, 1 = kWh, > 1 = Wh [int]
    unit_of_measurement: Kč/kWh             # Viewed unit [string]
    decimal_places: 5                       # Decimal places [int]
    scan_interval: 10                       # Refresh interval [int][sec]
    add_attribute_sensors: false            # true = Enable, false = Disable
    add_attributes_to_actual_price: false   # true = Enable, false = Disable
    highest_price_from_hour: 0              # Filter for highest price (FROM)
    highest_price_to_hour: 6                # Filter for highest price (TO)
    lowest_price_from_hour: 0               # Filter for lowest price (FROM)
    lowest_price_to_hour: 6                 # Filter for lowest price (TO) 

binary_sensor:
  - platform: ote_energy_parser_czk
    scan_interval: 10
    highest_price_from_hour: 0              # Filter for highest price (FROM)
    highest_price_to_hour: 6                # Filter for highest price (TO)
    lowest_price_from_hour: 0               # Filter for lowest price (FROM)
    lowest_price_to_hour: 6                 # Filter for lowest price (TO) 
```
### The Most Importent Parameters Card

```yaml
type: entities
title: OTE Energy CZK
entities:
  - entity: sensor.ote_energy_czk_actual_price
    name: Actual Price
  - entity: sensor.ote_energy_czk_highest_price
    name: Highest Price
  - entity: sensor.ote_energy_czk_highest_price_hour
    name: Highest Price Hour
  - entity: sensor.ote_energy_czk_lowest_price
    name: Lowest Price
  - entity: sensor.ote_energy_czk_lowest_price_hour
    name: Lowest Price Hour

```

### Lowest Highest Price Active Card

```yaml
type: entities
title: OTE Energy CZK
entities:
  - entity: binary_sensor.ote_energy_czk_highest_price_active
    name: Highest Price Active
  - entity: binary_sensor.ote_energy_czk_lowest_price_active
    name: Lowest Price Active

```

### Entity Card (Only if _add_attribute_sensors: true_)

```yaml
type: entities
title: OTE Energy CZK
entities:
  - entity: sensor.ote_energy_czk_attribut_0
    name: 00:00 - 00:59
  - entity: sensor.ote_energy_czk_attribut_1
    name: 01:00 - 01:59
  - entity: sensor.ote_energy_czk_attribut_2
    name: 02:00 - 02:59
  - entity: sensor.ote_energy_czk_attribut_3
    name: 03:00 - 03:59
  - entity: sensor.ote_energy_czk_attribut_4
    name: 04:00 - 04:59
  - entity: sensor.ote_energy_czk_attribut_5
    name: 05:00 - 05:59
  - entity: sensor.ote_energy_czk_attribut_6
    name: 06:00 - 06:59
  - entity: sensor.ote_energy_czk_attribut_7
    name: 07:00 - 07:59
  - entity: sensor.ote_energy_czk_attribut_8
    name: 08:00 - 08:59
  - entity: sensor.ote_energy_czk_attribut_9
    name: 09:00 - 09:59
  - entity: sensor.ote_energy_czk_attribut_10
    name: 10:00 - 10:59
  - entity: sensor.ote_energy_czk_attribut_11
    name: 11:00 - 11:59
  - entity: sensor.ote_energy_czk_attribut_12
    name: 12:00 - 12:59
  - entity: sensor.ote_energy_czk_attribut_13
    name: 13:00 - 13:59
  - entity: sensor.ote_energy_czk_attribut_14
    name: 14:00 - 14:59
  - entity: sensor.ote_energy_czk_attribut_15
    name: 15:00 - 15:59
  - entity: sensor.ote_energy_czk_attribut_16
    name: 16:00 - 16:59
  - entity: sensor.ote_energy_czk_attribut_17
    name: 17:00 - 17:59
  - entity: sensor.ote_energy_czk_attribut_18
    name: 18:00 - 18:59
  - entity: sensor.ote_energy_czk_attribut_19
    name: 19:00 - 19:59
  - entity: sensor.ote_energy_czk_attribut_20
    name: 20:00 - 20:59
  - entity: sensor.ote_energy_czk_attribut_21
    name: 21:00 - 21:59
  - entity: sensor.ote_energy_czk_attribut_22
    name: 22:00 - 22:59
  - entity: sensor.ote_energy_czk_attribut_23
    name: 23:00 - 23:59
```
