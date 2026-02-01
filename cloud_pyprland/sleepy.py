"""A plugin to push app information to sleepy server."""

import aiohttp
from pyprland.plugins.interface import Plugin
from pyprland.validation import ConfigField


class Extension(Plugin):
    """A plugin to push app information to sleepy server."""

    config_schema = [
        ConfigField("server_url", str, default=""),
        ConfigField("device_name", str, default=""),
        ConfigField("device_id", str, default=""),
        ConfigField("token", str, default=""),
    ]

    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def on_reload(self) -> None:
        """Apply configuration values after config is (re)loaded."""
        # Ensure the instance attributes reflect current config
        self.server_url = self.config["server_url"]
        self.device_name = self.config["device_name"]
        self.device_id = self.config["device_id"]
        self.token = self.config["token"]

    environments = ["hyprland"]

    async def event_activewindowv2(self, _addr: str) -> None:
        """Push app information to sleepy server.

        Args:
            _addr: The address of the active window

        """
        _addr = "0x" + _addr

        clients = await self.get_clients()

        for client in clients:
            if client["address"] == _addr:
                # Hyprland client dict uses 'class_' key
                # cls = client.get("class") or ""
                title = client.get("title") or ""
                await self._set_status(title)

    async def _set_status(self, app_name: str):
        """Pass the active app name to sleepy server."""
        # Ensure required configuration is present
        if not (self.device_id and self.device_name and self.server_url):
            self.log.error(
                "Missing sleepy configuration: device_id/device_name/server_url"
            )
            return

        json_body = {
            "id": self.device_id,
            "show_name": self.device_name,
            "using": True,
            "status": app_name,
        }

        headers: dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/api/device/set",
                json=json_body,
                headers=headers or None,
            ) as response:
                if response.status == 200:
                    self.log.debug(f"Set status to {app_name} successfully.")
                else:
                    self.log.error(
                        f"Failed to set status to {app_name}. HTTP {response.status}"
                    )
