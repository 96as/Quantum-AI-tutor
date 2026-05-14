# mock_data.py
# Fake results used by the UI while Team A/B build the real backend.
# On Day 2, Team A/B will replace this with real function calls.
# The shape of each result dict is the JSON contract all teams agreed on.

MOCK_RESULTS = {

    "bell": {
        "code": """\
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)          # Hadamard: put qubit 0 in superposition
qc.cx(0, 1)      # CNOT: entangle qubit 1 with qubit 0
qc.measure([0, 1], [0, 1])
""",
        "actual_distribution":   {"00": 0.502, "01": 0.010, "10": 0.010, "11": 0.478},
        "expected_distribution": {"00": 0.500, "01": 0.000, "10": 0.000, "11": 0.500},
        "verification_passed": True,
        "verification_message": "Output matches expected Bell state. Equal peaks at |00⟩ and |11⟩.",
        "bugs": [
            "Qiskit uses little-endian qubit ordering — |11⟩ means qubit 0 = 1, qubit 1 = 1."
        ],
        "explanation": (
            "A Bell state is the simplest example of quantum entanglement. "
            "The Hadamard gate puts qubit 0 into superposition (50% |0⟩ / 50% |1⟩). "
            "The CNOT then links qubit 1 to qubit 0, so measuring one instantly tells you the other. "
            "The result is an equal split between |00⟩ and |11⟩ — the two qubits are always correlated."
        ),
    },

    "grover": {
        "code": """\
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(3, 3)
qc.h([0, 1, 2])    # Put all qubits in equal superposition

# Oracle: marks the target state |011⟩ by flipping its phase
qc.x(2)
qc.h(2)
qc.ccx(0, 1, 2)    # Toffoli gate (controlled-controlled-NOT)
qc.h(2)
qc.x(2)

# Diffusion step: amplifies the marked state
qc.h([0, 1, 2])
qc.x([0, 1, 2])
qc.h(2)
qc.ccx(0, 1, 2)
qc.h(2)
qc.x([0, 1, 2])
qc.h([0, 1, 2])

qc.measure([0, 1, 2], [0, 1, 2])
""",
        "actual_distribution":   {"000": 0.03, "001": 0.02, "010": 0.03, "011": 0.78,
                                   "100": 0.03, "101": 0.04, "110": 0.03, "111": 0.04},
        "expected_distribution": {"000": 0.00, "001": 0.00, "010": 0.00, "011": 1.00,
                                   "100": 0.00, "101": 0.00, "110": 0.00, "111": 0.00},
        "verification_passed": True,
        "verification_message": "Peak at 78% on target state |011⟩. Grover amplification is working.",
        "bugs": [
            "Qiskit uses little-endian ordering — |011⟩ means qubit 0=1, qubit 1=1, qubit 2=0. "
            "Double-check this is the state you intended to mark."
        ],
        "explanation": (
            "Grover's algorithm finds a marked item in an unsorted list faster than any classical method. "
            "Step 1 — the Hadamard gates create an equal superposition of all 8 states. "
            "Step 2 — the oracle flips the phase of |011⟩ without revealing which state it is. "
            "Step 3 — the diffusion step amplifies the marked state's probability. "
            "After one Grover iteration, |011⟩ dominates the output at ~78%."
        ),
    },

    "ghz": {
        "code": """\
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(3, 3)
qc.h(0)          # Hadamard on qubit 0
qc.cx(0, 1)      # Entangle qubit 1
qc.cx(0, 2)      # Entangle qubit 2
qc.measure([0, 1, 2], [0, 1, 2])
""",
        "actual_distribution":   {"000": 0.497, "111": 0.503},
        "expected_distribution": {"000": 0.500, "111": 0.500},
        "verification_passed": True,
        "verification_message": "Output matches expected GHZ state. Only |000⟩ and |111⟩ appear.",
        "bugs": [],
        "explanation": (
            "A GHZ (Greenberger–Horne–Zeilinger) state is a 3-qubit entangled state. "
            "Like a Bell state but extended to 3 qubits — all three are always perfectly correlated. "
            "Measuring any one qubit instantly determines the other two. "
            "The result is an equal split between |000⟩ and |111⟩, with no other states."
        ),
    },
}

# Shown when no keyword in the prompt matches any entry above
DEFAULT_RESULT = MOCK_RESULTS["bell"]
