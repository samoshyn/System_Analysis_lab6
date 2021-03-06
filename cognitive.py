from typing import Any, Dict, List, NoReturn, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def cycle_str(x: List[int]) -> str:
    return " - ".join(str(y) for y in x)


class CognitiveModel:
    def __init__(self, adjacency_matrix: np.ndarray, nodes_names: Optional[Dict[int, Any]] = None):
        self.graph = nx.DiGraph(incoming_graph_data=adjacency_matrix)
        self.nodes_names = (
            nodes_names if nodes_names is not None else {key: f"V{key + 1}" for key in range(len(adjacency_matrix))}
        )
        if nodes_names:
            nx.set_node_attributes(self.graph, "name", nodes_names)

    @property
    def adjacency_matrix(self) -> np.ndarray:
        return nx.adjacency_matrix(self.graph).todense()

    @property
    def graph_weights(self) -> Dict[Any, Any]:
        return nx.get_edge_attributes(self.graph, "weight")

    @staticmethod
    def get_spectral_radius(matrix: np.ndarray) -> float:
        return np.max(np.absolute(np.linalg.eigvals(matrix)))

    def check_perturbation_stability(self) -> bool:
        if self.get_spectral_radius(self.adjacency_matrix) <= 1:
            return True
        else:
            return False

    def check_numerical_stability(self) -> bool:
        if self.get_spectral_radius(self.adjacency_matrix) < 1:
            return True
        else:
            return False

    def is_even(self, cycle: List[int]) -> bool:
        negative_count = np.count_nonzero(
            np.less([self.graph_weights[edge] for edge in nx.find_cycle(self.graph, cycle)], 0)
        )
        return not negative_count & 0x1

    def check_structural_stability(self) -> List[List[int]]:
        return [cycle for cycle in nx.simple_cycles(self.graph) if self.is_even(cycle)]

    def calculate_eigenvalues(self) -> np.ndarray:
        return np.linalg.eigvals(self.adjacency_matrix)

    def draw_graph(self) -> NoReturn:
        # rcParams["figure.figsize"] = 10, 8
        fig, ax = plt.subplots()
        colors = ["g" if self.graph_weights[edge] > 0 else "r" for edge in self.graph.edges()]
        nx.draw_networkx(
            self.graph,
            pos=nx.circular_layout(self.graph),
            arrows=True,
            with_labels=True,
            edge_color=colors,
            font_size=10,
            font_color="#ffffff",
            node_color="k",
            labels=self.nodes_names,
            node_size=2400,
            ax=ax
        )
        ax.set_title("???????????????????? ??????????")
        return fig

    def impulse_model(self, t: int = 5, q: Optional[np.ndarray] = None) -> NoReturn:
        # rcParams["figure.figsize"] = 7, 5
        x_0 = np.zeros((self.adjacency_matrix.shape[0], 1))
        init_q = x_0.copy()
        x_list = [x_0, x_0]
        if q is None:
            q = init_q.copy()
            q[1] = 1
        else:
            q = np.array(q).reshape(-1, 1)
        save_q = q.copy()

        for _ in range(t):
            x_next = x_list[-1] + np.dot(self.adjacency_matrix, (x_list[-1] - x_list[-2])) + q
            x_list.append(x_next)
            q = init_q.copy()
        x_plot = np.array(x_list[1:])
        x_plot = x_plot.reshape(x_plot.shape[:2])

        fig, ax = plt.subplots()

        for index in range(x_plot.shape[1]):
            ax.plot(range(t + 1), x_plot[:, index], label=f"V{index + 1}")
        ax.set_title(f"???????????? ???????????????????? ???????????????? ?? ???????????????? \n q = {save_q.reshape(-1, )}")
        ax.set_xlabel("??????????")
        ax.set_ylabel("x(t)")
        ax.legend()

        return fig
