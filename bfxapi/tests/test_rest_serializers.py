#pylint: disable=duplicate-code

import unittest

from ..labeler import _Type

from ..rest import serializers

class TestRestSerializers(unittest.TestCase):
    def test_rest_serializers(self):
        for serializer in map(serializers.__dict__.get, serializers.__serializers__):
            self.assertTrue(issubclass(serializer.klass, _Type),
                f"_Serializer <{serializer.name}>: .klass field must be a subclass " \
                    f"of _Type (got {serializer.klass}).")

            self.assertListEqual(serializer.get_labels(), list(serializer.klass.__annotations__),
                f"_Serializer <{serializer.name}> and _Type <{serializer.klass.__name__}> " \
                    "must have matching labels and fields.")

if __name__ == "__main__":
    unittest.main()
