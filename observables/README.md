# Observáveis: exercício do Prof. Rodrigo Pasti

Valores esperados de strings de Pauli (`ZZZ`, `XXX`, `YYY`, `XYZ`) em circuitos de 3 qubits,
estimados a partir de contagens (10 000 shots) e comparados com o valor exato.

- `exercise_observables.py`: implementação (Qiskit + Aer). Baseada no conceito do `observables_template.py` do professor.
- `observables_resultados.csv` e `observables_resultados.png`: resultados.

## Como rodar
```
pip install qiskit qiskit-aer matplotlib numpy
python exercise_observables.py
```

## Resultados (valor esperado exato)
| Bases | H | H + S | H + T |
|---|---|---|---|
| ZZZ | 0 | 0 | 0 |
| XXX | 1 | 0 | 0,354 |
| YYY | 0 | 1 | 0,354 |
| XYZ | 0 | 0 | 0 |

H leva cada qubit ao eixo X; S gira de X para Y; T gira 45° entre X e Y (0,354 = 0,707³).

## Notas
- A lista de exercícios cita 3 circuitos mas lista 4; o quarto ("XYZ") não está definido, então foi omitido.
- Cada string devolve um único número: a correlação entre os qubits (produto dos autovalores).
