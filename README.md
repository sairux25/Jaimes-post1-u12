# Laboratorio Unidad 12 — Computación cuántica con Qiskit
Sara Jaimes Castañeda · Arquitectura de Computadores

Entorno utilizado

Windows 11 Home con Python 3.13.2, Qiskit 1.4.6, Qiskit Aer 0.18.4 y matplotlib 3.11.2. Todos los experimentos se ejecutaron en el simulador AerSimulator, sin hardware cuántico real. Los scripts se ejecutan desde la raíz del repositorio para que las imágenes se guarden en la carpeta capturas.

# PARTE 1 — Laboratorio de circuitos cuánticos con Qiskit

## Checkpoint 1 — Estado de Bell
Capturas: capturas/CP1_bell_ejecucion.png y capturas/bell_histogram.png

El circuito aplica una Hadamard al qubit 0, que lo deja en superposición, y después una CNOT con el qubit 0 como control y el qubit 1 como objetivo, así los dos qubits quedan entrelazados en el estado |Φ⁺⟩.

```
     ┌───┐     ┌─┐   
q_0: ┤ H ├──■──┤M├───
     └───┘┌─┴─┐└╥┘┌─┐
q_1: ─────┤ X ├─╫─┤M├
          └───┘ ║ └╥┘
c: 2/═══════════╩══╩═
                0  1 
```

En 1024 mediciones se obtuvieron 507 resultados |00⟩ (49.5%) y 517 resultados |11⟩ (50.5%), sin ningún |01⟩ ni |10⟩. Por eso la verificación del script pasó y el histograma muestra solo esas dos barras. Esto muestra la correlación del entrelazamiento, al medir un qubit el otro siempre da el mismo valor.

## Checkpoint 2 — Algoritmo de Deutsch-Jozsa
Captura: capturas/CP2_deutsch_jozsa_ejecucion.png

Se implementaron los dos oráculos para n=2 con un qubit auxiliar (q_2) que se prepara en |−⟩ con una X y luego una H. El oráculo constante no aplica ninguna puerta y el balanceado aplica una CNOT de cada qubit de entrada hacia el auxiliar.

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

El resultado fue determinista. Con el oráculo constante las 1024 mediciones dieron |00⟩ y con el balanceado las 1024 dieron |11⟩, así que las dos verificaciones del script pasaron.

En el caso clásico, para n=2 hay 4 entradas posibles y se necesitan hasta 3 evaluaciones. Si las dos primeras dan el mismo valor la función todavía puede ser balanceada, y solo la tercera lo decide. En cambio, el circuito cuántico evalúa el oráculo una sola vez, porque las H ponen las 4 entradas en superposición y el auxiliar en |−⟩ hace que f(x) quede como un cambio de fase en cada una. Las H finales hacen interferir esas fases, si la función es constante toda la probabilidad queda en |00⟩ y si es balanceada la de |00⟩ se cancela.

## Checkpoint 3 — Algoritmo de Grover en 2 qubits
Capturas: capturas/CP3_grover_ejecucion.png, capturas/grover_00.png, capturas/grover_01.png, capturas/grover_10.png y capturas/grover_11.png

El circuito pone los dos qubits en superposición con H, después aplica el oráculo de fase que le cambia el signo al estado buscado y termina con el difusor, que amplifica ese estado. Para el objetivo |11⟩ el oráculo es solo una CZ, para los otros tres se agregan puertas X antes y después de la CZ en los qubits que deben valer 0.

```
     ┌───┐   ┌───┐┌───┐   ┌───┐┌───┐┌─┐   
q_0: ┤ H ├─■─┤ H ├┤ X ├─■─┤ X ├┤ H ├┤M├───
     ├───┤ │ ├───┤├───┤ │ ├───┤├───┤└╥┘┌─┐
q_1: ┤ H ├─■─┤ H ├┤ X ├─■─┤ X ├┤ H ├─╫─┤M├
     └───┘   └───┘└───┘   └───┘└───┘ ║ └╥┘
c: 2/════════════════════════════════╩══╩═
                                     0  1 
```

En la primera prueba el programa encontró bien |00⟩ y |11⟩, pero al buscar |01⟩ midió |10⟩ en los 1024 disparos y al buscar |10⟩ midió |01⟩, y el script imprimió ERROR en esos dos casos. El problema es que Qiskit escribe los resultados con el qubit 1 a la izquierda y el oráculo suponía el orden contrario, entonces negaba el qubit equivocado. Por eso se cambió el oráculo para que el objetivo "01" aplique la X sobre el qubit 1 y el objetivo "10" sobre el qubit 0. Con ese cambio los cuatro objetivos se encontraron correctamente.

| Objetivo | Estado medido | Conteo | Probabilidad | Resultado |
|---|---|---|---|---|
| \|00⟩ | \|00⟩ | 1024 | 100.0% | CORRECTO |
| \|01⟩ | \|01⟩ | 1024 | 100.0% | CORRECTO |
| \|10⟩ | \|10⟩ | 1024 | 100.0% | CORRECTO |
| \|11⟩ | \|11⟩ | 1024 | 100.0% | CORRECTO |

Con n=2 basta una iteración porque el espacio tiene solo 4 estados y el número óptimo de iteraciones, cercano a (π/4)·√4 ≈ 1.57, se redondea a 1. Al inicio cada estado tiene amplitud 1/2, el oráculo deja la del objetivo en −1/2 y el difusor refleja todas las amplitudes alrededor de su promedio, que es 1/4. De esta forma el objetivo pasa a amplitud 1 y los otros tres quedan en 0, por lo que la probabilidad llega al 100% con una sola iteración y una segunda la volvería a bajar.

## Checkpoint 4 — Grover bajo ruido simulado
Capturas: capturas/CP4_grover_ruido_ejecucion.png y capturas/grover_noise_comparison.png

Se reutilizó el mismo circuito de Grover del Checkpoint 3 con objetivo |11⟩, que tiene 10 puertas de 1 qubit (H y X) y 2 puertas CZ. Se ejecutó una vez en el simulador ideal y otra con un NoiseModel que agrega un error despolarizante de 0.1% a cada H y X y de 1% a cada CZ.

En la primera prueba los porcentajes salieron bien, sin embargo en la imagen comparativa el panel izquierdo quedó sin el título "Sin ruido" y sin la rejilla. La causa está en plot_histogram, que coloca el título y la rejilla en el eje activo de matplotlib y no en el que recibe, y después de plt.subplots el activo es el panel derecho. Se agregó entonces plt.sca antes de cada histograma para activar el panel que se va a dibujar, y ya cada uno quedó con su título. Además, el oráculo de este script recibió el mismo cambio de las X del Checkpoint 3 para que el circuito sea idéntico.

| Estado | Sin ruido | Con ruido |
|---|---|---|
| \|00⟩ | 0 | 4 |
| \|01⟩ | 0 | 4 |
| \|10⟩ | 0 | 8 |
| \|11⟩ | 1024 (100.0%) | 1008 (98.4%) |

La probabilidad de éxito bajó de 100.0% a 98.4%, es decir 1.6 puntos porcentuales, y en ejecuciones anteriores con las mismas tasas el valor con ruido estuvo entre 97.5% y 98.5%. Esta pérdida tiene sentido con el modelo configurado, ya que cada puerta tiene una pequeña probabilidad de alterar el estado y las CZ, con un error diez veces mayor, son las que más aportan. Los 16 disparos que se perdieron se repartieron entre los otros tres estados, que sin ruido nunca aparecían, pero |11⟩ sigue siendo claramente el más probable.
