import copy


class UnspecifiedDefault(object):
    pass


class Field(object):
    def __init__(self, nullable=False, default=UnspecifiedDefault, read_only=False):
        self._nullable = nullable
        self._default = default
        self._read_only = read_only

    def __repr__(self):
        return '%s(default=%s, nullable=%s)' % (self.__class__.__name__,
                                                self._default, self._nullable)

    @property
    def nullable(self):
        return self._nullable

    @property
    def default(self):
        return self._default

    @property
    def read_only(self):
        return self._read_only

    def _null(self, obj, attr):
        if self.nullable:
            return None
        else:
            raise ValueError("Field `%s' cannot be None" % attr)

    def coerce(self, obj, attr, value):
        """Coerce a value to a suitable type.

        :param:obj: The object being acted upon
        :param:attr: The name of the attribute/field being set
        :param:value: The value being set
        :returns: The properly-typed value
        """
        if value is None:
            return self._null(obj, attr)
        elif self._default != UnspecifiedDefault:
            return Field.stringify(self._default)
        else:
            raise NotImplementedError

    def from_primitive(self, obj, attr, value):
        """Deserialize a value from primitive form.

        This is responsible for deserializing a value from primitive
        into regular form. It calls the from_primitive() method on a
        FieldType to do the actual deserialization.

        :param:obj: The object being acted upon
        :param:attr: The name of the attribute/field being deserialized
        :param:value: The value to be deserialized
        :returns: The deserialized value
        """
        if value is None:
            return None
        else:
            raise NotImplementedError

    def to_primitive(self, obj, attr, value):
        """Serialize a value to primitive form.

        This is responsible for serializing a value to primitive
        form. It calls to_primitive() on a FieldType to do the actual
        serialization.

        :param:obj: The object being acted upon
        :param:attr: The name of the attribute/field being serialized
        :param:value: The value to be serialized
        :returns: The serialized value
        """
        if value is None:
            return None
        else:
            raise NotImplementedError

    @staticmethod
    def stringify(value):
        if value is None:
            return 'None'
        else:
            return str(value)


class StringField(Field):

    def __init__(self, nullable=False, default=UnspecifiedDefault, read_only=False):
        super().__init__(nullable, default, read_only)
