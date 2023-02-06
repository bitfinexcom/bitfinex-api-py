import unittest

from ..rest import serializers, types

class TestRestSerializersAndTypes(unittest.TestCase):
    def test_consistency(self):
        for serializer in map(serializers.__dict__.get, serializers.__serializers__):
            type = types.__dict__.get(serializer.name)
            
            self.assertIsNotNone(type, f"_Serializer <{serializer.name}>: no respective _Type found in bfxapi.rest.types.")
            self.assertEqual(serializer.klass, type, f"_Serializer <{serializer.name}>.klass: field does not match with respective _Type in bfxapi.rest.types.")

            self.assertListEqual(serializer.get_labels(), list(type.__annotations__), 
                f"_Serializer <{serializer.name}> and _Type <{type.__name__}> must have matching labels and fields.")

if __name__ == "__main__":
    unittest.main()