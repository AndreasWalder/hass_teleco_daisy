import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN
from .hub import DaisyHub

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[str] = ["light", "cover"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    daisy_hub = DaisyHub(hass, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    await hass.async_add_executor_job(daisy_hub.login)
    await hass.async_add_executor_job(daisy_hub.fetch_entities)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = daisy_hub

    async def handle_feed_command(call: ServiceCall):
        device_code = call.data["deviceCode"]
        id_device = call.data["idInstallationDevice"]
        command_action = call.data["commandAction"]
        command_id = call.data["commandId"]
        command_param = call.data["commandParam"]
        lowlevel = call.data.get("lowlevelCommand")

        command = {
            "commandAction": command_action,
            "commandId": command_id,
            "commandParam": command_param,
            "deviceCode": str(device_code),
            "idInstallationDevice": id_device,
        }
        if lowlevel:
            command["lowlevelCommand"] = lowlevel

        await hass.async_add_executor_job(daisy_hub.feed_command, command)

    hass.services.async_register(DOMAIN, "feed_command", handle_feed_command)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
