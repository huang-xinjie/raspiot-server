
class BBaseException(Exception):
    msg_fmt = 'An unknown exception occurred'

    def __init__(self, message=None, **kwargs):
        if not message:
            self.message = self.msg_fmt % kwargs
        else:
            self.message = str(message)

    def __reduce__(self):
        return self.__class__, (self.message,)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class DeviceNotFound(BBaseException):
    msg_fmt = 'Device %(device_uuid)s not found'


class DeviceBasicAttributeError(BBaseException):
    msg_fmt = 'Device %(device_uuid)s basic attribute %(attribute)s is empty'


class InvalidDeviceProtocol(BBaseException):
    msg_fmt = 'Invalid device protocol %(protocol)s'


class DeviceRemoteError(BBaseException):
    msg_fmt = 'Failed to handle remote device %(device_uuid)s: %(reason)s'


class DeviceConnectTimeout(DeviceRemoteError):
    msg_fmt = 'Connect device %(device_uuid)s timeout %(timeout)s'


class ObjectRegistryConflict(BBaseException):
    msg_fmt = 'Object registry conflict %(class_name)s'
