import unittest

from dataclasses import dataclass
from ..labeler import generate_labeler_serializer
from ..notification import _Type, _Notification, Notification

class TestNotification(unittest.TestCase):
    def test_notification(self):
        @dataclass
        class Test(_Type):
            A: int
            B: float
            C: str

        test = generate_labeler_serializer("Test", Test,
            [ "A", "_PLACEHOLDER", "B", "_PLACEHOLDER", "C" ])

        notification = _Notification[Test](test)

        actual = notification.parse(*[ 1675787861506, "test", None, None, [ 5, None, 65.0, None, "X" ], \
                0, "SUCCESS", "This is just a test notification." ])

        expected = Notification[Test](1675787861506, "test", None, Test(5, 65.0, "X"),
                0, "SUCCESS", "This is just a test notification.")

        self.assertEqual(actual, expected, msg="_Notification should produce the right notification.")

if __name__ == "__main__":
    unittest.main()
