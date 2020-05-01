import sys
sys.path.append('../components')

from bfxapi import Decimal

def test_precision():
	assert str(Decimal(0.00000123456789)) == "0.00000123456789"
	assert str(Decimal("0.00000123456789")) == "0.00000123456789"

def test_float_operations():
	assert str(Decimal(0.0002) * 0.02) == "0.000004"
	assert str(0.02 * Decimal(0.0002)) == "0.000004"
	
	assert str(Decimal(0.0002) / 0.02) == "0.01"
	assert str(0.02 / Decimal(0.0002)) == "0.01"

	assert str(0.02 + Decimal(0.0002)) == "0.0202"
	assert str(Decimal(0.0002) + 0.02) == "0.0202"

	assert str(0.02 - Decimal(0.0002)) == "-0.0198"
	assert str(Decimal(0.0002) - 0.02) == "-0.0198"

	assert str(0.01 // Decimal(0.0004)) == "0"
	assert str(Decimal(0.0004) // 0.01) == "0"
