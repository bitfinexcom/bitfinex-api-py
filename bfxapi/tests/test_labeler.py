import unittest

from dataclasses import dataclass
from ..exceptions import LabelerSerializerException
from ..labeler import _Type, generate_labeler_serializer, generate_recursive_serializer

class TestLabeler(unittest.TestCase):
    def test_generate_labeler_serializer(self):
        @dataclass
        class Test(_Type):
            A: int
            B: float
            C: str

        labels = [ "A", "_PLACEHOLDER", "B", "_PLACEHOLDER", "C" ]

        serializer = generate_labeler_serializer("Test", Test, labels)

        self.assertEqual(serializer.parse(5, None, 65.0, None, "X"), Test(5, 65.0, "X"))
        self.assertRaises(LabelerSerializerException, serializer.parse, 5, 65.0, "X")
        self.assertListEqual(serializer.get_labels(), [ "A", "B", "C" ])

if __name__ == "__main__":
    unittest.main()