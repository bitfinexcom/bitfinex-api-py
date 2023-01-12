import json
from decimal import Decimal
from datetime import datetime

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal) or isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)