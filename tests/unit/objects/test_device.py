import unittest
from objects.device import Device
from db.sqlalchemy.models import DeviceSyncMode


class FakeModelField:
    def __init__(self, name):
        self.name = name


class DeviceTestCase(unittest.TestCase):

    def test_validate_sync_fields_with_sync_mode_normal(self):
        sync_mode_field = FakeModelField('sync_mode')

        self.assertEqual(DeviceSyncMode.poll, Device.validate_sync_fields('poll', sync_mode_field))
        self.assertEqual(DeviceSyncMode.report, Device.validate_sync_fields('report', sync_mode_field))

    def test_validate_sync_fields_with_sync_mode_exception(self):
        sync_mode_field = FakeModelField('sync_mode')
        # invalid input
        self.assertRaises(ValueError, Device.validate_sync_fields, 123, sync_mode_field)
        self.assertRaises(ValueError, Device.validate_sync_fields, '', sync_mode_field)
        self.assertRaises(ValueError, Device.validate_sync_fields, 'sync_mode', sync_mode_field)

        # empty input
        self.assertEqual(DeviceSyncMode.poll, Device.validate_sync_fields(None, sync_mode_field))

    def test_validate_sync_fields_with_sync_interval_normal(self):
        sync_interval_field = FakeModelField('sync_interval')

        self.assertEqual(300, Device.validate_sync_fields(300, sync_interval_field))
        self.assertEqual(300, Device.validate_sync_fields('300', sync_interval_field))
        self.assertEqual(1000, Device.validate_sync_fields('1000', sync_interval_field))

    def test_validate_sync_fields_with_sync_interval_exception(self):
        sync_interval_field = FakeModelField('sync_interval')

        # invalid input
        self.assertRaises(ValueError, Device.validate_sync_fields, 0, sync_interval_field)
        self.assertRaises(ValueError, Device.validate_sync_fields, -1, sync_interval_field)
        self.assertRaises(ValueError, Device.validate_sync_fields, 5.5, sync_interval_field)
        self.assertRaises(ValueError, Device.validate_sync_fields, '', sync_interval_field)
        self.assertRaises(ValueError, Device.validate_sync_fields, 'sync_interval', sync_interval_field)

        # empty input
        self.assertEqual(60 * 5, Device.validate_sync_fields(None, sync_interval_field))
