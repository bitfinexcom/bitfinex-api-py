import decimal as dec

class Decimal(dec.Decimal):

    @classmethod
    def from_float(cls, f):
      return cls(str(f))

    def __new__(cls, value=0, *args, **kwargs):
      if isinstance(value, float):
        value = Decimal.from_float(value)
      return super(Decimal, cls).__new__(cls, value, *args, **kwargs)

    def __mul__(self, rhs):
      if isinstance(rhs, float):
        rhs = Decimal.from_float(rhs)
      return Decimal(super().__mul__(rhs))

    def __rmul__(self, lhs):
      return self.__mul__(lhs)

    def __add__(self, rhs):
      if isinstance(rhs, float):
        rhs = Decimal.from_float(rhs)
      return Decimal(super().__add__(rhs))

    def __radd__(self, lhs):
      return self.__add__(lhs)

    def __sub__(self, rhs):
      if isinstance(rhs, float):
        rhs = Decimal.from_float(rhs)
      return Decimal(super().__sub__(rhs))

    def __rsub__(self, lhs):
      return self.__sub__(lhs)

    def __truediv__(self, rhs):
      if isinstance(rhs, float):
        rhs = Decimal.from_float(rhs)
      return Decimal(super().__truediv__(rhs))

    def __rtruediv__(self, rhs):
      return self.__truediv__(rhs)

    def __floordiv__(self, rhs):
      if isinstance(rhs, float):
        rhs = Decimal.from_float(rhs)
      return Decimal(super().__floordiv__(rhs))

    def __rfloordiv__ (self, rhs):
      return self.__floordiv__(rhs)
