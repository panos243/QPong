#
# Copyright 2019 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from model import circuit_node_types as node_types


class CircuitGridModel():
    """Grid-based model that is built when user interacts with circuit"""
    def __init__(self, max_wires, max_columns):
        self.max_wires = max_wires
        self.max_columns = max_columns
        self.nodes = np.empty((max_wires, max_columns),
                                dtype = CircuitGridNode)

    def __str__(self):
        retval = ''
        for wire_num in range(self.max_wires):
            retval += '\n'
            for column_num in range(self.max_columns):
                retval += str(self.nodes[wire_num][column_num]) + ', '

        return 'CircuitGridModel: ' + retval

    def set_node(self, wire_num, column_num, node_type, radians=0, ctrl_a=-1, ctrl_b=-1, swap=-1):
        self.nodes[wire_num][column_num] = CircuitGridNode(node_type, radians, ctrl_a, ctrl_b, swap)

        # TODO: Decide whether to protect as shown below
        # if not self.nodes[wire_num][column_num]:
        #     self.nodes[wire_num][column_num] = CircuitGridNode(node_type, radians)
        # else:
        #     print('Node ', wire_num, column_num, ' not empty')

    def get_node(self, wire_num, column_num):
        return self.nodes[wire_num][column_num]

    def compute_circuit(self):
        qr = QuantumRegister(self.max_wires, 'q')
        qc = QuantumCircuit(qr)

        for column_num in range(self.max_columns):
            for wire_num in range(self.max_wires):
                node = self.nodes[wire_num][column_num]
                if node:
                    if node.node_type == node_types.IDEN:
                        # Identity gate
                        qc.iden(qr[wire_num])
                    elif node.node_type == node_types.X:
                        if node.radians == 0:
                            if node.ctrl_a != -1:
                                if node.ctrl_b != -1:
                                    # Toffoli gate
                                    qc.ccx(qr[node.ctrl_a], qr[node.ctrl_b], qr[wire_num])
                                else:
                                    # Controlled X gate
                                    qc.cx(qr[node.ctrl_a], qr[wire_num])
                            else:
                                # Pauli-X gate
                                qc.x(qr[wire_num])
                        else:
                            # Rotation around X axis
                            qc.rx(node.radians, qr[wire_num])
                    elif node.node_type == node_types.Y:
                        if node.radians == 0:
                            if node.ctrl_a != -1:
                                # Controlled Y gate
                                qc.cy(qr[node.ctrl_a], qr[wire_num])
                            else:
                                # Pauli-Y gate
                                qc.y(qr[wire_num])
                        else:
                            # Rotation around Y axis
                            qc.ry(node.radians, qr[wire_num])
                    elif node.node_type == node_types.Z:
                        if node.radians == 0:
                            if node.ctrl_a != -1:
                                # Controlled Z gate
                                qc.cz(qr[node.ctrl_a], qr[wire_num])
                            else:
                                # Pauli-Z gate
                                qc.z(qr[wire_num])
                        else:
                            if node.ctrl_a != -1:
                                # Controlled rotation around the Z axis
                                qc.crz(node.radians, qr[node.ctrl_a], qr[wire_num])
                            else:
                                # Rotation around Z axis
                                qc.rz(node.radians, qr[wire_num])
                    elif node.node_type == node_types.S:
                        # S gate
                        qc.s(qr[wire_num])
                    elif node.node_type == node_types.SDG:
                        # S dagger gate
                        qc.sdg(qr[wire_num])
                    elif node.node_type == node_types.T:
                        # T gate
                        qc.t(qr[wire_num])
                    elif node.node_type == node_types.TDG:
                        # T dagger gate
                        qc.tdg(qr[wire_num])
                    elif node.node_type == node_types.H:
                        if node.ctrl_a != -1:
                            # Controlled Hadamard
                            qc.ch(qr[node.ctrl_a], qr[wire_num])
                        else:
                            # Hadamard gate
                            qc.h(qr[wire_num])
                    elif node.node_type == node_types.SWAP:
                        if node.ctrl_a != -1:
                            # Controlled Swap
                            qc.cswap(qr[node.ctrl_a], qr[wire_num], qr[node.swap])
                        else:
                            # Swap gate
                            qc.swap(qr[wire_num], qr[node.swap])
                    elif node.node_type == node_types.B:
                        # Barrier
                        qc.barrier(qr)

        return qc


class CircuitGridNode():
    """Represents a node in the circuit grid"""
    def __init__(self, node_type, radians=0.0, ctrl_a=-1, ctrl_b=-1, swap=-1):
        self.node_type = node_type
        self.radians = radians
        self.ctrl_a = ctrl_a
        self.ctrl_b = ctrl_b
        self.swap = swap

    def __str__(self):
        string = 'type: ' + str(self.node_type)
        string += ', radians: ' + str(self.radians) if self.radians != 0 else ''
        string += ', ctrl_a: ' + str(self.ctrl_a) if self.ctrl_a != -1 else ''
        string += ', ctrl_b: ' + str(self.ctrl_b) if self.ctrl_b != -1 else ''
        return string