import unittest

from .test_types_labeler import TestTypesLabeler
from .test_types_notification import TestTypesNotification
from .test_types_serializers import TestTypesSerializers

def suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestTypesLabeler),
        unittest.makeSuite(TestTypesNotification),
        unittest.makeSuite(TestTypesSerializers),
    ])

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
