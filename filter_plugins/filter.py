from __future__ import annotations

from typing import Any, ClassVar

from ansible.parsing.yaml.objects import (
    AnsibleUnicode,
    AnsibleVaultEncryptedUnicode,
)
from ansible.utils.unsafe_proxy import AnsibleUnsafeText


class FilterModule:
    """
    Custom jinja filters
    """

    def filters(self) -> dict:
        """
        :return: filters dict
        """
        return {
            "is_list": self.is_list,
            "is_ne_list": self.is_ne_list,
            "is_ne_list_dicts": self.is_ne_list_dicts,
            "is_dict": self.is_dict,
            "is_ne_dict": self.is_ne_dict,
            "is_str": self.is_str,
            "is_ne_str": self.is_ne_str,
            "get_all_pairs": self.get_all_pairs,
            "to_list": self.to_list,
            "get_key": self.get_key,
            "get_keys": self.get_keys,
        }

    @staticmethod
    def is_list(var: Any) -> bool:
        """
        :param var: any variable
        :return: true if var is list
        """
        return var and isinstance(var, list)

    def is_ne_list(self, var: Any) -> bool:
        """
        :param var: any variable
        :return: true if var is not empty list
        """
        return self.is_list(var) and len(var) > 0

    @staticmethod
    def is_dict(var: Any) -> bool:
        """
        :param var: any variable
        :return: true if variable is dict
        """
        return var and isinstance(var, dict)

    def is_ne_dict(self, var: Any) -> bool:
        """
        :param var: any variable
        :return: true if variable is not empty dict
        """
        return self.is_dict(var) and var != {}

    def is_ne_list_dicts(self, var: Any) -> bool:
        """
        :param var: any variable
        :return: true if variable is list of dicts
        """
        if not self.is_ne_list(var):
            return False

        for element in var:
            if not self.is_ne_dict(element):
                return False

        return True

    @staticmethod
    def is_str(var: Any) -> bool:
        """
        :param var: any variable
        :return: true if variable is one of instance of string
        """
        return var and isinstance(
            var,
            (
                str,
                AnsibleUnicode,
                AnsibleVaultEncryptedUnicode,
                AnsibleUnsafeText,
            ),
        )

    def is_ne_str(self, var: Any) -> bool:
        """
        :param var: any variable
        :return: true if variable is one of instance of string and not empty
        """
        return self.is_str(var) and len(var) > 0

    @staticmethod
    def get_all_pairs(var: list[str]) -> list[dict]:
        """
        :param var: list of interfaces / networks / zones
        :return: all pairs of list elements
        """
        if not isinstance(var, list) or len(var) < 2:
            return []

        result = [
            {"from": a, "to": b}
            for idx, a in enumerate(var)
            for b in var[idx + 1 :]
        ]
        return result

    @staticmethod
    def to_list(var: Any) -> list:
        if not isinstance(var, list):
            return [
                var,
            ]
        return var

    def get_key(self, var: dict, key: str, default: Any = None) -> Any:
        if "." in key:
            _current, _next = key.split(".", 1)
            _var = var.get(_current, None)

            if not _var or not isinstance(_var, dict):
                return default

            return self.get_key(var=_var, key=_next)

        return var.get(key, default)

    def get_keys(self, var: list[dict], key: str) -> list[Any]:
        """
        :param var: List of dicts
        :param key: Key for search
        :return: List with key values
        """

        result = []

        for v in var:
            data = self.get_key(v, key)
            if not data:
                continue
            result.extend(self.to_list(data))

        return list(set(result))
