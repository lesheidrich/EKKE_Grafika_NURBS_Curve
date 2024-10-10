from typing import List, Tuple, Any
import numpy as np


class NurbsCurve:
    def __init__(self, control_points: List[Tuple[int]], weights: List[int] = None, degree: int = 3):
        """
        :param control_points: List of (x, y) tuples for Control Points
        :param degree: Curve degree, defaults to 3
        :param weights: int List of weights  for Control Point magnitude
        """
        self.control_points = control_points
        self.degree = degree
        self.weights = weights if weights is not None else [1.0] * len(control_points)
        self.knots = self.get_uniform_knots_v()
        print(f"Knot V: {self.knots} / CPs: {len(control_points)}\n")

    def get_uniform_knots_v(self) -> List[int]:
        """
        #knots = count(CPs) + degree + 1
        [0, 0, 0, 0] + [1, ..., count(CPs) -2] + [count(CPs) - 2]*4
        :return: int List[uniform knot vectors] from len(Control Points) and curve degree
        """
        # num_knots = len(self.control_points) + self.degree + 1
        # return [0] * (self.degree + 1) + list(range(1, len(self.control_points) - self.degree)) + [len(self.control_points) - self.degree] * (self.degree + 1)
        num_knots = len(self.control_points) + self.degree + 1
        return [0] * (self.degree + 1) + list(range(1, num_knots - 2 * self.degree)) + [num_knots - 2 * self.degree] * (self.degree + 1)

    def cox_de_boor(self, i: int, k: int, t: float) -> float:
        """
        Calculate the degree of influence each weight has on each Control Point at t on the curve.
        Sums up the weighted influence of all control points at each t by recursively calculating
        along decreasing degree for points.
        :param i: int index of the basis function along Control Points
        :param k: degree of the basis function
        :param t: t val (0 <= t <= 1)
        :return: Basis function value at point
        """
        # k--
        if k == 0:
            # 1 if t ∈ [knot_{i}, knot_{i+1}]
            return 1.0 if self.knots[i] <= t < self.knots[i + 1] else 0.0
        else:
            left_numerator = t - self.knots[i]
            left_denominator = self.knots[i + k] - self.knots[i]
            right_numerator = self.knots[i + k + 1] - t
            right_denominator = self.knots[i + k + 1] - self.knots[i + 1]

            # (t - knot_i) / (knot_{i+k} - knot_i) * N_{i,k-1}(t)
            left = (left_numerator / left_denominator * self.cox_de_boor(i, k - 1, t) if left_denominator != 0 else 0)
            # (knot_{i+k+1} - t) / (knot_{i+k+1} - knot_{i+1}) * N_{i+1,k-1}(t)
            right = (right_numerator / right_denominator * self.cox_de_boor(i + 1, k - 1, t) if right_denominator != 0 else 0)

            return left + right

    def evaluate(self, samples: int = 100) -> List[Tuple[int]]:
        """
        Calculates the points along the curve.
        Generates t values, calcualtes each Control Point's influence on each t value
        :param samples: How many points on the curve
        :return: List of point tuples (x, y) for coordinates along the curve
        """
        curve_points = []
        t_min = self.knots[self.degree]  # current
        t_max = self.knots[-self.degree - 1]  # last usable knot
        # evenly spaced t values from current knot to last usable knot
        t_values = np.linspace(t_min, t_max, samples)

        for t in t_values:
            # placeholders
            point = np.zeros(2)  # (x, y)
            weight_sum = 0.0    # all CP's w*influence
            for i in range(len(self.control_points)):
                influence = self.cox_de_boor(i=i, k=self.degree, t=t)
                weight_sum += influence * self.weights[i]
                point += influence * self.weights[i] * np.array(self.control_points[i])

            if weight_sum > 0:
                # normalize point for all CPs influence
                point /= weight_sum
            curve_points.append(tuple(point))

        return curve_points[:-1]
