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

        self.assertEqual(serializer.parse(5, None, 65.0, None, "X"), Test(5, 65.0, "X"),
            msg="_Serializer should produce the right result.")

        self.assertEqual(serializer.parse(5, 65.0, "X", skip=[ "_PLACEHOLDER" ]), Test(5, 65.0, "X"),
            msg="_Serializer should produce the right result when skip parameter is given.")

        self.assertListEqual(serializer.get_labels(), [ "A", "B", "C" ],
            msg="_Serializer::get_labels() should return the right list of labels.")

        with self.assertRaises(LabelerSerializerException,
                msg="_Serializer should raise LabelerSerializerException if given " \
                        "fewer arguments than the serializer labels."):
            serializer.parse(5, 65.0, "X")

    def test_generate_recursive_serializer(self):
        @dataclass
        class Outer(_Type):
            A: int
            B: float
            C: "Middle"

        @dataclass
        class Middle(_Type):
            D: str
            E: "Inner"

        @dataclass
        class Inner(_Type):
            F: bool

        inner = generate_labeler_serializer("Inner", Inner, ["F"])
        middle = generate_recursive_serializer("Middle", Middle, ["D", "E"], serializers={ "E": inner })
        outer = generate_recursive_serializer("Outer", Outer, ["A", "B", "C"], serializers={ "C": middle })

        self.assertEqual(outer.parse(10, 45.5, [ "Y", [ True ] ]), Outer(10, 45.5, Middle("Y", Inner(True))),
            msg="_RecursiveSerializer should produce the right result.")

if __name__ == "__main__":
    unittest.main()
