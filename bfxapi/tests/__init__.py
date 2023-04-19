import unittest

from .test_rest_serializers import TestRestSerializers
from .test_websocket_serializers import TestWebSocketSerializers
from .test_labeler import TestLabeler
from .test_notification import TestNotification

def suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestRestSerializers),
        unittest.makeSuite(TestWebSocketSerializers),
        unittest.makeSuite(TestLabeler),
        unittest.makeSuite(TestNotification),
    ])

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
