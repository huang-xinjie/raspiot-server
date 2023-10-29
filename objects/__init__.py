
def register_all():
    __import__('objects.device')
    __import__('objects.mac_mapping')
    __import__('objects.role')
    __import__('objects.room')
    __import__('objects.user')
