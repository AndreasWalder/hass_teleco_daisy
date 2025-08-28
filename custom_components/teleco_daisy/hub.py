from __future__ import annotations
from homeassistant.core import HomeAssistant

from teleco_daisy import (
    TelecoDaisy,
    DaisyWhiteLight,
    DaisyRGBLight,
    DaisyAwningsCover,
    DaisySlatsCover,
    DaisyInstallation,  # hinzufügen
)


class DaisyHub(TelecoDaisy):
    manufacturer = "Teleco Automation"
    lights = []
    covers = []

    def __init__(self, hass: HomeAssistant, email: str, password: str) -> None:
        super().__init__(email, password)

        self._hass = hass
        self._name = "Teleco DaisyHub"
        self._id = "Teleco DaisyHub".lower()

        self.installation: DaisyInstallation | None = None
        self.online = True

    def fetch_entities(self):
        self.lights = []
        self.covers = []
        installations = self.get_account_installation_list()
        if installations:
            self.installation = installations[0]  # nur die erste Installation
            for room in self.get_room_list(self.installation):
                for device in room.deviceList:
                    if isinstance(device, DaisyWhiteLight | DaisyRGBLight):
                        self.lights += [device]
                    elif isinstance(device, DaisyAwningsCover | DaisySlatsCover):
                        self.covers += [device]

    def feed_command(self, command: dict):
        if self.installation is None:
            raise RuntimeError("Installation not loaded")
        return self.feed_the_commands(self.installation, [command])

    @property
    def hub_id(self) -> str:
        return self._id

    async def test_connection(self) -> bool:
        # TODO: echte Prüfung
        return True
