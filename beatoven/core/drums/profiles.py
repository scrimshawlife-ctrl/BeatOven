"""
BeatOven Drums RigProfile Storage (ADAPTER LAYER)

Filesystem-based storage for RigProfile configurations.

THIS IS AN ADAPTER: I/O operations are ALLOWED here.
Core logic must remain in PURE engines (allocator.py, composer.py).

Responsibilities:
- Load/save RigProfile JSON files
- Manage current profile state
- Provide default profiles
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import time

from .schema import RigProfile
from .defaults import get_default_profiles


# Default storage location (can be overridden)
DEFAULT_PROFILE_DIR = Path.home() / ".beatoven" / "rig_profiles"


class RigProfileStorage:
    """
    Filesystem storage for RigProfiles.

    Stores profiles as JSON files in ~/.beatoven/rig_profiles/
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize storage.

        Args:
            storage_dir: Directory for profile storage (default: ~/.beatoven/rig_profiles)
        """
        self.storage_dir = storage_dir or DEFAULT_PROFILE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Current profile cache
        self._current_profile_id: Optional[str] = None

    def save(self, profile: RigProfile) -> None:
        """
        Save profile to filesystem.

        Args:
            profile: RigProfile to save
        """
        file_path = self.storage_dir / f"{profile.id}.json"

        data = profile.to_dict()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)

    def load(self, profile_id: str) -> Optional[RigProfile]:
        """
        Load profile from filesystem.

        Args:
            profile_id: Profile ID to load

        Returns:
            RigProfile if found, None otherwise
        """
        file_path = self.storage_dir / f"{profile_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return RigProfile.from_dict(data)

    def list(self) -> List[RigProfile]:
        """
        List all saved profiles.

        Returns:
            List of RigProfiles
        """
        profiles = []

        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                profile = RigProfile.from_dict(data)
                profiles.append(profile)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue

        # Sort by creation time (newest first)
        profiles.sort(key=lambda p: p.created_at_ts_ms or 0, reverse=True)

        return profiles

    def delete(self, profile_id: str) -> bool:
        """
        Delete profile from filesystem.

        Args:
            profile_id: Profile ID to delete

        Returns:
            True if deleted, False if not found
        """
        file_path = self.storage_dir / f"{profile_id}.json"

        if not file_path.exists():
            return False

        file_path.unlink()

        # Clear current if this was the current profile
        if self._current_profile_id == profile_id:
            self._current_profile_id = None
            self._save_current_state()

        return True

    def set_current(self, profile_id: str) -> bool:
        """
        Set current active profile.

        Args:
            profile_id: Profile ID to set as current

        Returns:
            True if set successfully, False if profile not found
        """
        # Verify profile exists
        if not (self.storage_dir / f"{profile_id}.json").exists():
            return False

        self._current_profile_id = profile_id
        self._save_current_state()
        return True

    def get_current(self) -> Optional[RigProfile]:
        """
        Get current active profile.

        Returns:
            Current RigProfile if set, None otherwise
        """
        self._load_current_state()

        if self._current_profile_id is None:
            return None

        return self.load(self._current_profile_id)

    def get_current_id(self) -> Optional[str]:
        """
        Get current active profile ID.

        Returns:
            Profile ID if set, None otherwise
        """
        self._load_current_state()
        return self._current_profile_id

    def _save_current_state(self) -> None:
        """Save current profile ID to state file."""
        state_file = self.storage_dir / ".current"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump({"current_profile_id": self._current_profile_id}, f)

    def _load_current_state(self) -> None:
        """Load current profile ID from state file."""
        state_file = self.storage_dir / ".current"

        if not state_file.exists():
            return

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._current_profile_id = data.get("current_profile_id")
        except (json.JSONDecodeError, KeyError):
            pass

    def ensure_defaults(self) -> None:
        """
        Ensure default profiles are available.

        If no profiles exist, create default profiles from defaults.py.
        """
        existing = self.list()

        if len(existing) == 0:
            # No profiles exist, create defaults
            defaults = get_default_profiles()
            for profile in defaults:
                self.save(profile)

            # Set first default as current
            if defaults:
                self.set_current(defaults[0].id)


# Singleton instance for convenience
_default_storage: Optional[RigProfileStorage] = None


def get_default_storage() -> RigProfileStorage:
    """
    Get singleton storage instance.

    Returns:
        Default RigProfileStorage
    """
    global _default_storage
    if _default_storage is None:
        _default_storage = RigProfileStorage()
        _default_storage.ensure_defaults()
    return _default_storage


__all__ = [
    "RigProfileStorage",
    "get_default_storage",
    "DEFAULT_PROFILE_DIR",
]
