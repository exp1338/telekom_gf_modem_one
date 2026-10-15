"""Sensor entities for Telekom Glasfaser Modem 1."""

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class OntSensorDescription(SensorEntityDescription):
    pass


SENSORS = (
    OntSensorDescription(key="temperature", name="Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT),
    OntSensorDescription(key="voltage", name="Voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, state_class=SensorStateClass.MEASUREMENT),
    OntSensorDescription(key="cpu_usage", name="CPU usage", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC),
    OntSensorDescription(key="memory_usage", name="Memory usage", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, entity_category=EntityCategory.DIAGNOSTIC),
    OntSensorDescription(key="bias_current", name="Bias current", native_unit_of_measurement="mA", state_class=SensorStateClass.MEASUREMENT),
    OntSensorDescription(key="rx_power", name="RX optical power", native_unit_of_measurement="dBm", state_class=SensorStateClass.MEASUREMENT),
    OntSensorDescription(key="tx_power", name="TX optical power", native_unit_of_measurement="dBm", state_class=SensorStateClass.MEASUREMENT),
    OntSensorDescription(key="ont_status", name="ONT status"),
    OntSensorDescription(key="router_state", name="Router state", entity_category=EntityCategory.DIAGNOSTIC),
    OntSensorDescription(key="firmware_version", name="Firmware version", entity_category=EntityCategory.DIAGNOSTIC),
    OntSensorDescription(key="hardware_revision", name="Hardware revision", entity_category=EntityCategory.DIAGNOSTIC),
    OntSensorDescription(key="ui_version", name="UI version", entity_category=EntityCategory.DIAGNOSTIC),
)

GPON_STATES = {
    "O1": "Initialisierung / Keine GPON-Verbindung",
    "O2": "Suche nach GPON-Signal",
    "O3": "Seriennummernregistrierung",
    "O4": "Entfernungsmessung (Ranging)",
    "O5": "Verbunden / Betriebsbereit",
    "O6": "Verbindung unterbrochen (POPUP)",
    "O7": "Notabschaltung (Emergency Stop)",
}

NUMERIC_KEYS = {"temperature", "voltage", "cpu_usage", "memory_usage", "bias_current", "rx_power", "tx_power"}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(OntSensor(coordinator, entry.data["host"], description) for description in SENSORS)


class OntSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, host: str, description: OntSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{host}_{description.key}"
        data = coordinator.data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name="Telekom Glasfaser Modem 1",
            manufacturer="Deutsche Telekom",
            model=data.get("device_name", "Glasfaser-Modem"),
            sw_version=data.get("firmware_version"),
            hw_version=data.get("hardware_revision"),
            serial_number=data.get("serial_number"),
            configuration_url=f"http://{host}/ONT/client/html/content/overview/index.html",
        )

    @property
    def extra_state_attributes(self):
        if self.entity_description.key == "ont_status":
            return {"gpon_code": self.coordinator.data.get("ont_status")}
        return None

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self.entity_description.key)
        if raw is None or raw.strip() in ("", "--", "N/A"):
            return None
        if self.entity_description.key in NUMERIC_KEYS:
            try:
                return float(raw)
            except ValueError:
                return None
        if self.entity_description.key == "ont_status":
            return GPON_STATES.get(raw, f"Unbekannter GPON-Zustand ({raw})")
        return raw
