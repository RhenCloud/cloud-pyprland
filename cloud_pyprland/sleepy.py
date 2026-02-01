"""A plugin to push app information to sleepy server."""

import contextlib
from typing import Any

import aiohttp
from pyprland.plugins.interface import Plugin
from pyprland.validation import ConfigField, ConfigItems


class Extension(Plugin):
    """A plugin to push app information to sleepy server."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._conf_name = name.split(":", 1)[1] if ":" in name else name
        config = self.load_config()
        self.base_api_url = config.get("server_url", "")
        self.device_name = config.get("device_name", "")
        self.device_id = config.get("device_id", "")
        self.token = config.get("token", "")

    async def load_config(self, config: dict[str, Any]) -> None:  # type: ignore[override]
        """Load configuration using base section name."""
        self.config.clear()
        with contextlib.suppress(KeyError):
            self.config.update(config[self._conf_name])
        if self.config_schema:
            self.config.set_schema(self.config_schema)

    environments = ["hyprland"]

    config_schema = ConfigItems(
        ConfigField("server_url", str, default="", required=True),
        ConfigField("device_name", str, default="", required=True),
        ConfigField("device_id", str, default="", required=True),
        ConfigField("token", str, default="", required=True),
    )

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

        json_body = {
            "id": self.config["device_id"],
            "show_name": self.config["device_name"],
            "using": True,
            "status": app_name,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.config['server_url']}/api/device/set",
                json=json_body,
            ) as response:
                if response.status == 200:
                    await self.log.debug(f"Set status to {app_name} successfully.")
                else:
                    await self.log.error(f"Failed to set status to {app_name}.")
