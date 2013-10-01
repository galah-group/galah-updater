#!/usr/bin/env python

# gicore
import gicore.preplanner
from gicore.preplanner import UAInstall, UAMigrate

# stdlib
import unittest

# Shorter names to make creating the expected results easier
class TestSignatures(unittest.TestCase):
    def setUp(self):
        self.all_packages = {
            "a": ["1", "2", "3", "4", "5", "6"],
            "b": ["alpha", "bravo", "charlie", "echo"]
        }

    def test_basic_upgrade(self):
        installed_packages = {"a": "1"}
        desired_state = {"a": "2"}
        expected_result = [
            UAMigrate(name = "a", from_version = "1", to_version = "2"),
            UAInstall(name = "a", version = "2")
        ]
        result = gicore.preplanner.determine_preactions(self.all_packages,
            installed_packages, desired_state)
        self.assertEquals(expected_result, result)

    def test_basic_downgrade(self):
        installed_packages = {"a": "2"}
        desired_state = {"a": "1"}
        expected_result = [
            UAMigrate(name = "a", from_version = "2", to_version = "1"),
            UAInstall(name = "a", version = "1")
        ]
        result = gicore.preplanner.determine_preactions(self.all_packages,
            installed_packages, desired_state)
        self.assertEquals(expected_result, result)

    def test_long_upgrade(self):
        installed_packages = {"a": "1"}
        desired_state = {"a": "4"}
        expected_result = [
            UAMigrate(name = "a", from_version = "1", to_version = "2"),
            UAMigrate(name = "a", from_version = "2", to_version = "3"),
            UAMigrate(name = "a", from_version = "3", to_version = "4"),
            UAInstall(name = "a", version = "4")
        ]
        result = gicore.preplanner.determine_preactions(self.all_packages,
            installed_packages, desired_state)
        self.assertEquals(expected_result, result)

    def test_long_downgrade(self):
        installed_packages = {"a": "4"}
        desired_state = {"a": "1"}
        expected_result = [
            UAMigrate(name = "a", from_version = "4", to_version = "3"),
            UAMigrate(name = "a", from_version = "3", to_version = "2"),
            UAMigrate(name = "a", from_version = "2", to_version = "1"),
            UAInstall(name = "a", version = "1")
        ]
        result = gicore.preplanner.determine_preactions(self.all_packages,
            installed_packages, desired_state)
        self.assertEquals(expected_result, result)

    def test_composite(self):
        installed_packages = {"a": "2", "b": "charlie"}
        desired_state = {"a": "5", "b": "alpha"}
        expected_result = [
            UAMigrate(name = "a", from_version = "2", to_version = "3"),
            UAMigrate(name = "a", from_version = "3", to_version = "4"),
            UAMigrate(name = "a", from_version = "4", to_version = "5"),
            UAInstall(name = "a", version = "5"),

            UAMigrate(name = "b", from_version = "charlie",
                to_version = "bravo"),
            UAMigrate(name = "b", from_version = "bravo",
                to_version = "alpha"),
            UAInstall(name = "b", version = "alpha")
        ]
        result = gicore.preplanner.determine_preactions(self.all_packages,
            installed_packages, desired_state)
        self.assertEquals(expected_result, result)

if __name__ == '__main__':
    unittest.main()
