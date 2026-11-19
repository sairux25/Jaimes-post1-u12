# src/grover_noise.py
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def build_grover_circuit(target="11"):
    """Reconstruye el mismo circuito de Grover (2 qubits) del Paso 3."""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    if target == "11":
        qc.cz(0, 1)
    elif target == "00":
        qc.x([0, 1]); qc.cz(0, 1); qc.x([0, 1])
    # Qiskit escribe los bits como q1q0, por eso "01" niega q1 y "10" niega q0
    elif target == "01":
        qc.x(1); qc.cz(0, 1); qc.x(1)
    elif target == "10":
        qc.x(0); qc.cz(0, 1); qc.x(0)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    return qc

def build_noise_model(p1q=0.001, p2q=0.01):
    """Modelo de ruido despolarizante: p1q por puerta de 1 qubit (h, x),
    p2q por puerta de 2 qubits (cz) — órdenes de magnitud típicos de
    hardware NISQ superconductor publicados en la documentación de IBM Quantum."""
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1q, 1), ["h", "x"])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2q, 2), ["cz"])
    return noise_model

def grover_noise_experiment(target="11", shots=1024):
    qc = build_grover_circuit(target)

    # Simulación ideal (sin ruido) — línea base
    counts_ideal = AerSimulator().run(qc, shots=shots).result().get_counts()

    # Simulación con ruido despolarizante inyectado en cada puerta
    noisy_sim = AerSimulator(noise_model=build_noise_model())
    counts_noisy = noisy_sim.run(qc, shots=shots).result().get_counts()

    p_ideal = counts_ideal.get(target, 0) / shots
    p_noisy = counts_noisy.get(target, 0) / shots

    print(f"Grover |{target}> sin ruido: {p_ideal*100:.1f}%")
    print(f"Grover |{target}> con ruido: {p_noisy*100:.1f}%")
    print(f"Degradacion: {(p_ideal - p_noisy)*100:.1f} puntos porcentuales")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    # plot_histogram pone el titulo y la rejilla en el eje activo, por eso se activa cada panel antes
    plt.sca(axs[0])
    plot_histogram(counts_ideal, ax=axs[0], title="Sin ruido")
    plt.sca(axs[1])
    plot_histogram(counts_noisy, ax=axs[1], title="Con ruido (despolarizante)")
    fig.tight_layout()
    fig.savefig("capturas/grover_noise_comparison.png", dpi=150)

    return p_ideal, p_noisy

if __name__ == "__main__":
    grover_noise_experiment()
