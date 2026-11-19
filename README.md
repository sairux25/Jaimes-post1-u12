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

## Checkpoint 2 — Algoritmo de Deutsch-Jozsa
Captura: capturas/CP2_deutsch_jozsa_ejecucion.png

Se implementaron los dos oráculos para n=2 con un qubit auxiliar (q_2) que se prepara en |−⟩ aplicando X y luego H. El oráculo constante no aplica ninguna puerta, mientras que el balanceado aplica una CNOT de cada qubit de entrada hacia el auxiliar.

```
Oráculo constante
     ┌───┐┌───┐┌─┐   
q_0: ┤ H ├┤ H ├┤M├───
     ├───┤├───┤└╥┘┌─┐
q_1: ┤ H ├┤ H ├─╫─┤M├
     ├───┤├───┤ ║ └╥┘
q_2: ┤ X ├┤ H ├─╫──╫─
     └───┘└───┘ ║  ║ 
c: 2/═══════════╩══╩═
                0  1 

Oráculo balanceado
     ┌───┐          ┌───┐     ┌─┐   
q_0: ┤ H ├───────■──┤ H ├─────┤M├───
     ├───┤       │  └───┘┌───┐└╥┘┌─┐
q_1: ┤ H ├───────┼────■──┤ H ├─╫─┤M├
     ├───┤┌───┐┌─┴─┐┌─┴─┐└───┘ ║ └╥┘
q_2: ┤ X ├┤ H ├┤ X ├┤ X ├──────╫──╫─
     └───┘└───┘└───┘└───┘      ║  ║ 
c: 2/══════════════════════════╩══╩═
                               0  1 
```

Con el oráculo constante las 1024 mediciones dieron |00⟩ y con el balanceado las 1024 dieron |11⟩, así que el resultado fue determinista en los dos casos y las dos verificaciones del script pasaron.

Clásicamente, para n=2 hay 4 entradas posibles y se necesitan hasta 3 evaluaciones, porque si las dos primeras dan el mismo valor la función todavía puede ser balanceada y solo la tercera lo decide. En cambio, el circuito cuántico evalúa el oráculo una sola vez, ya que las puertas H ponen las 4 entradas en superposición y el auxiliar en |−⟩ hace que f(x) quede como un cambio de fase en cada una. Luego las H finales hacen interferir esas fases, de modo que si la función es constante toda la probabilidad se concentra en |00⟩ y si es balanceada la de |00⟩ se cancela por completo.

## Checkpoint 3 — Algoritmo de Grover en 2 qubits
Capturas: capturas/CP3_grover_ejecucion.png, capturas/grover_00.png, capturas/grover_01.png, capturas/grover_10.png y capturas/grover_11.png

El circuito pone los dos qubits en superposición con H, aplica el oráculo de fase que invierte el signo del estado buscado y termina con el difusor, que amplifica ese estado. Para el objetivo |11⟩ el oráculo es solo una CZ, y para los otros tres objetivos se agregan puertas X antes y después de la CZ en los qubits que deben valer 0.

```
     ┌───┐   ┌───┐┌───┐   ┌───┐┌───┐┌─┐   
q_0: ┤ H ├─■─┤ H ├┤ X ├─■─┤ X ├┤ H ├┤M├───
     ├───┤ │ ├───┤├───┤ │ ├───┤├───┤└╥┘┌─┐
q_1: ┤ H ├─■─┤ H ├┤ X ├─■─┤ X ├┤ H ├─╫─┤M├
     └───┘   └───┘└───┘   └───┘└───┘ ║ └╥┘
c: 2/════════════════════════════════╩══╩═
                                     0  1 
```

En la primera prueba el programa encontró bien |00⟩ y |11⟩, pero al buscar |01⟩ midió |10⟩ en los 1024 disparos y al buscar |10⟩ midió |01⟩, por lo que el mismo script imprimió ERROR en esos dos casos. Esto pasó porque Qiskit escribe los resultados con el qubit 1 a la izquierda y el qubit 0 a la derecha, mientras que el oráculo suponía el orden contrario y negaba el qubit equivocado. Por lo tanto se ajustó el oráculo para que el objetivo "01" aplique la X sobre el qubit 1 y el objetivo "10" la aplique sobre el qubit 0. Hecho esto, los cuatro objetivos se encontraron correctamente.

| Objetivo | Estado medido | Conteo | Probabilidad | Resultado |
|---|---|---|---|---|
| \|00⟩ | \|00⟩ | 1024 | 100.0% | CORRECTO |
| \|01⟩ | \|01⟩ | 1024 | 100.0% | CORRECTO |
| \|10⟩ | \|10⟩ | 1024 | 100.0% | CORRECTO |
| \|11⟩ | \|11⟩ | 1024 | 100.0% | CORRECTO |

Con n=2 basta una iteración porque el espacio tiene solo 4 estados y el número óptimo de iteraciones, cercano a (π/4)·√4 ≈ 1.57, se redondea a 1. Además, en este caso la superposición inicial le da a cada estado una amplitud de 1/2, el oráculo deja la del objetivo en −1/2 y el difusor refleja todas las amplitudes alrededor de su promedio, que es 1/4. Así el objetivo pasa a amplitud 1 y los otros tres quedan en 0, por eso la probabilidad llega al 100% con una sola iteración y una segunda la volvería a bajar.
