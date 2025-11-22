import math
import pytest

from finance import (
	calculate_compound_interest,
	calculate_annuity_payment,
	calculate_internal_rate_of_return,
)


# --- Tests for calculate_compound_interest ---

def test_compound_interest_basic():
	assert calculate_compound_interest(1000, 0.05, 2) == pytest.approx(1102.5, rel=1e-6)


def test_compound_interest_zero_rate():
	assert calculate_compound_interest(1500, 0.0, 10) == 1500


def test_compound_interest_zero_periods():
	assert calculate_compound_interest(800, 0.12, 0) == 800


def test_compound_interest_negative_rate():
	# Simula pérdida anual del 5%
	assert calculate_compound_interest(1000, -0.05, 3) == pytest.approx(857.375, rel=1e-6)


def test_compound_interest_large_periods():
	result = calculate_compound_interest(100, 0.04, 50)
	# Valor futuro esperado usando fórmula estándar
	expected = 100 * (1.04 ** 50)
	assert result == pytest.approx(expected, rel=1e-12)


def test_compound_interest_zero_principal():
	assert calculate_compound_interest(0, 0.07, 20) == 0


# --- Tests for calculate_annuity_payment ---

def test_annuity_payment_basic():
	payment = calculate_annuity_payment(10000, 0.06, 5)
	# Fórmula manual para comparar
	expected = 10000 * (0.06 * (1.06 ** 5)) / ((1.06 ** 5) - 1)
	assert payment == pytest.approx(expected, rel=1e-12)


def test_annuity_payment_zero_rate():
	assert calculate_annuity_payment(1200, 0.0, 12) == 100


def test_annuity_payment_periods_one():
	# Con un solo período el pago es principal * (1+rate)
	payment = calculate_annuity_payment(5000, 0.08, 1)
	# Fórmula se reduce correctamente:
	expected = 5000 * (0.08 * (1.08 ** 1)) / ((1.08 ** 1) - 1)
	assert payment == pytest.approx(expected, rel=1e-12)


def test_annuity_payment_zero_principal():
	assert calculate_annuity_payment(0, 0.05, 10) == 0


def test_annuity_payment_negative_rate():
	# Tasa negativa (descuento). Verifica que la fórmula no explota.
	payment = calculate_annuity_payment(8000, -0.02, 4)
	expected = 8000 * (-0.02 * (0.98 ** 4)) / ((0.98 ** 4) - 1)
	assert payment == pytest.approx(expected, rel=1e-12)


def test_annuity_payment_periods_zero_raises_rate_zero():
	with pytest.raises(ZeroDivisionError):
		calculate_annuity_payment(1000, 0.0, 0)


def test_annuity_payment_periods_zero_raises_rate_positive():
	# Denominador (1+rate)**0 -1 = 0 => ZeroDivisionError
	with pytest.raises(ZeroDivisionError):
		calculate_annuity_payment(1000, 0.05, 0)


# --- Tests for calculate_internal_rate_of_return ---

def test_irr_basic_two_periods():
	irr = calculate_internal_rate_of_return([-1000, 1100])
	assert irr == pytest.approx(0.1, rel=1e-3)


def test_irr_derivative_zero_case():
	# Derivada será 0 tras primera iteración (todos cf posteriores son 0)
	irr = calculate_internal_rate_of_return([-1000, 0, 0, 0])
	# Se espera que retorne el guess inicial (0.1)
	assert irr == pytest.approx(0.1, rel=1e-12)


def test_irr_multiple_periods_accuracy():
	cash_flows = [-1000, 200, 300, 500, 600]
	irr = calculate_internal_rate_of_return(cash_flows)
	npv = sum(cf / (1 + irr) ** i for i, cf in enumerate(cash_flows))
	assert abs(npv) < 1e-4


def test_irr_low_iterations_inaccuracy():
	cash_flows = [-1000, 400, 400, 400, 400]
	irr_few = calculate_internal_rate_of_return(cash_flows, iterations=1)
	irr_many = calculate_internal_rate_of_return(cash_flows, iterations=100)
	# Con pocas iteraciones el NPV no estará tan cerca de cero
	npv_few = sum(cf / (1 + irr_few) ** i for i, cf in enumerate(cash_flows))
	npv_many = sum(cf / (1 + irr_many) ** i for i, cf in enumerate(cash_flows))
	assert abs(npv_many) < abs(npv_few)


def test_irr_zero_final_cash_flow():
	cash_flows = [-500, 0, 600]
	irr = calculate_internal_rate_of_return(cash_flows)
	npv = sum(cf / (1 + irr) ** i for i, cf in enumerate(cash_flows))
	assert abs(npv) < 1e-4


def test_irr_single_positive_cash_flow_large_return():
	irr = calculate_internal_rate_of_return([-100, 300])
	# Aproximadamente 200% de retorno
	assert irr == pytest.approx(2.0, rel=1e-2)


def test_irr_zero_investment_edge():
	irr = calculate_internal_rate_of_return([0, 100])
	# Inversión inicial cero => cualquier retorno infinito; el método produce algún valor finito.
	# Verificamos que NPV cercano a cero de todas formas.
	npv = sum(cf / (1 + irr) ** i for i, cf in enumerate([0, 100]))
	assert abs(npv) < 1e-4


def test_irr_high_growth_flow():
	cash_flows = [-1000, 50, 100, 200, 400, 800]
	irr = calculate_internal_rate_of_return(cash_flows)
	npv = sum(cf / (1 + irr) ** i for i, cf in enumerate(cash_flows))
	assert abs(npv) < 1e-4


def test_irr_short_series():
	irr = calculate_internal_rate_of_return([-500, 600])
	assert irr == pytest.approx(0.2, rel=1e-2)


def test_irr_flat_series():
	irr = calculate_internal_rate_of_return([-1000, 250, 250, 250, 250, 250])
	npv = sum(cf / (1 + irr) ** i for i, cf in enumerate([-1000, 250, 250, 250, 250, 250]))
	assert abs(npv) < 1e-4

