## Pruebas para `finance.py`

### Objetivo
Crear un conjunto de pruebas automatizadas con alta cobertura (>95%) para las funciones financieras:
- `calculate_compound_interest(principal, rate, periods)`
- `calculate_annuity_payment(principal, rate, periods)`
- `calculate_internal_rate_of_return(cash_flows, iterations=100)`

### Estrategia
1. Identifiqué comportamientos normales y extremos de cada función.
2. Para interés compuesto cubrí: tasa positiva, cero, negativa, períodos grandes, cero períodos, principal cero.
3. Para anualidad cubrí: tasa positiva estándar, tasa cero (rama especial), períodos = 1, tasa negativa, principal cero y división por cero cuando `periods=0` (excepción esperada tanto con tasa 0 como positiva).
4. Para la TIR (IRR) construí flujos que ejercen: retorno típico, derivada 0 (terminación temprana), múltiples períodos con verificación de NPV cercano a cero, pocas iteraciones vs muchas, flujos todos negativos, inversión inicial cero, retorno muy alto, series planas, crecimiento acelerado y casos cortos.
5. Utilicé `pytest.approx` para tolerancias numéricas debido a operaciones de potencia y convergencia iterativa.

### Desafíos y Soluciones
- Ausencia inicial de Python en el entorno: se instaló Python y luego se ejecutaron las pruebas con cobertura.
- Asegurar suficiente variedad en IRR: diseñé diferentes perfiles de flujo (crecimiento, plano, solo un gran retorno, inversión cero) para forzar distintas trayectorias del método de Newton–Raphson.
- Manejo de divisiones por cero en anualidad: agregué pruebas que validan explícitamente la excepción en `periods=0` para ambas variantes de tasa.
- Convergencia IRR: añadí comparación de NPV post-cálculo para confirmar la calidad de la aproximación y diferencié el caso de pocas iteraciones.

### Métricas Finales
- Cantidad de pruebas: 23
  - Interés compuesto: 6
  - Anualidad: 8
  - TIR: 9
- Cobertura sobre `finance.py`: 100% (15 sentencias, 0 faltantes)

### Ejecución
Desde la carpeta `HW - Testing con Copilot`:
```powershell
python -m pip install -r requirements.txt
python -m pytest --cov=finance --cov-report=term-missing -q
```

### Resultado Esperado
Salida similar a:
```
....................... [100%]
finance.py  15 statements  0 missing  100% coverage
```
