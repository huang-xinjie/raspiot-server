class BaseObject(object):
    obj_fields = {}

    @property
    def obj_name(self):
        return self.__name__

    def obj_attr_is_set(self, attr_name):
        if attr_name not in self.obj_fields:
            raise AttributeError('%(cls_name)s object has no attribute %(attr_name)s' %
                                 {'cls_name': self.__class__, 'attr_name': attr_name})
        return hasattr(self, attr_name)

    def obj_get_changes(self):
        changes = {}
        for key in self.obj_what_changed():
            changes[key] = getattr(self, key)
        return changes

    def get(self, key, default):
        if key not in self.obj_fields:
            raise AttributeError('%(cls_name)s object has no attribute %(attr_name)s' %
                                 {'cls_name': self.__class__, 'attr_name': key})
        if not self.obj_attr_is_set(key):
            return default
        else:
            return getattr(self, key)
