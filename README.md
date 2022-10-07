# OTE Energy Cost Sensor for Home Assistant

This is an integration providing current price per kilowatt of energy based on the quote
from ote-cr.cz, attributes as solo sensors, lowest price sensor and highest price sensor.

### Installation

If you're using HACS - feel free to add https://github.com/PetrS98/ote_energy_parser_czk as custom repository.

Once you've installed the custom integration, add the following to your `configuration.yaml` file:

```yaml
sensor:
  platform: ote_energy_parser_czk
```
### Entity card

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