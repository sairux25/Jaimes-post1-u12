# Laboratorio Unidad 12 — Computación cuántica con Qiskit
Sara Jaimes Castañeda · Arquitectura de Computadores

Este repositorio contiene las dos partes del postcontenido de la Unidad 12. En la Parte 1 se implementan y simulan con Qiskit el estado de Bell, el algoritmo de Deutsch-Jozsa y el algoritmo de Grover para 2 qubits, y luego se ejecuta Grover bajo un modelo de ruido despolarizante para medir cuánto se degrada el resultado. En la Parte 2 se analiza el impacto de la computación cuántica en la ciberseguridad y se propone un plan de migración hacia la criptografía post-cuántica en el documento docs/analisis-pqc.md.

Entorno utilizado

Windows 11 Home con Python 3.13.2, Qiskit 1.4.6, Qiskit Aer 0.18.4 y matplotlib 3.11.2. Todos los experimentos se ejecutaron sobre el simulador AerSimulator, sin hardware cuántico real. Los scripts se ejecutan desde la raíz del repositorio para que las imágenes queden guardadas en la carpeta capturas.

# PARTE 1 — Laboratorio de circuitos cuánticos con Qiskit

## Checkpoint 1 — Estado de Bell
Capturas: capturas/CP1_bell_ejecucion.png y capturas/bell_histogram.png

El circuito aplica una puerta Hadamard al qubit 0 para dejarlo en superposición y luego una CNOT con el qubit 0 como control y el qubit 1 como objetivo, de modo que los dos qubits quedan entrelazados en el estado |Φ⁺⟩.

```
     ┌───┐     ┌─┐   
q_0: ┤ H ├──■──┤M├───
     └───┘┌─┴─┐└╥┘┌─┐
q_1: ─────┤ X ├─╫─┤M├
          └───┘ ║ └╥┘
c: 2/═══════════╩══╩═
                0  1 
```

En 1024 mediciones se obtuvieron 507 resultados |00⟩ (49.5%) y 517 resultados |11⟩ (50.5%), sin ningún |01⟩ ni |10⟩. La verificación del script pasó y el histograma muestra solo esas dos barras, lo que confirma la correlación perfecta del entrelazamiento, ya que al medir un qubit el otro siempre da el mismo valor.
