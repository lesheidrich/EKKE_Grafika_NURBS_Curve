import tkinter as tk
from typing import Tuple
from nurbs_curve import NurbsCurve


class Display:
    def __init__(self, CP_size: int):
        """
        :param CP_size: int of pixel size for Control Points
        """
        self.CP_size = CP_size
        self.current_CP = None
        self.current_CP_i = None
        self.CP_list = []          # (x, y, char, w=1.0)
        # self.knot_list = []

        self._setup()
        self._set_bindings()
        self._set_buttons()
        self._create_weight_slider()
        # self._create_knot_slider()

        self.root.mainloop()

    def _setup(self) -> None:
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=600, height=450, bg="black")
        self.canvas.pack()

    def _set_bindings(self) -> None:
        self.canvas.bind("<Button-1>", self.left_mouse_click)
        self.canvas.bind("<B1-Motion>", self.left_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.left_mouse_release)

    def _set_buttons(self) -> None:
        self.clear_button = tk.Button(self.root, text="Clear", command=self.clear_display)
        self.clear_button.pack()

    def _create_weight_slider(self) -> None:
        self.weight_slider_frame = tk.Frame(self.root)
        self.weight_var = tk.DoubleVar()
        self.weight_var.set(1.0)

        self.weight_slider = tk.Scale(self.weight_slider_frame, from_=0.1, to=10.0, resolution=0.1,
                                      orient=tk.HORIZONTAL, label="w", command=self.update_weight_from_slider)
        self.weight_slider.grid(row=0, column=0, padx=250)
        self.weight_slider_frame.pack(side=tk.BOTTOM, pady=10)
        self.weight_slider_frame.pack_forget()

    # def _create_knot_slider(self) -> None:
    #     self.knot_slider_frame = tk.Frame(self.root)
    #     self.knot_var = tk.DoubleVar()
    #     self.knot_var.set(0.0)
    #
    #     self.knot_slider = tk.Scale(self.knot_slider_frame, from_=0.0, to=1.0, resolution=0.01,
    #                                 orient=tk.HORIZONTAL, label="knots", command=self.update_knot_from_slider)
    #     self.knot_slider.grid(row=0, column=0, padx=250)
    #     self.knot_slider_frame.pack(side=tk.BOTTOM, pady=10)
    #     self.knot_slider_frame.pack_forget()

    def left_mouse_click(self, event) -> None:
        """
        Select point if nearby, else create and draw
        :param event: Bound to left mouse click
        """
        # clicked on CP?
        self.current_CP = self.find_nearby_point(event.x, event.y)

        if self.current_CP:
            self.show_weight_modifier()
            # self.show_knot_modifier()
        else:
            # new point
            self.CP_list.append((event.x, event.y, self.get_next_label(), 1.0))
            # self.knot_list.append(0.0)
            self.redraw_display()

    def left_mouse_drag(self, event) -> None:
        """
        Drags point
        :param event: Bound to left mouse hold
        """
        if self.current_CP:
            _, _, char, w = self.CP_list[self.current_CP_i]
            self.CP_list[self.current_CP_i] = (event.x, event.y, char, w)
            self.redraw_display()

    def left_mouse_release(self, event) -> None:
        """
        Stops dragging current point when mouse released b/c current_CP is unset
        :param event: bound to left mouse release
        """
        self.current_CP = None

    def find_nearby_point(self, x: int, y: int, radius: int = 10) -> Tuple[int, int] | None:
        """
        Returns closest CP to coordinates (supplied by x and y of click), if any
        :param x: int of pixel row to search around
        :param y: int of pixel col to search around
        :param radius: int of radius to search
        :return: x: int, y: int tuple of coordinates for nearest CP or None
        """
        # closest CP in radius
        for i, (px, py, char, w) in enumerate(self.CP_list):
            if (x - px) ** 2 + (y - py) ** 2 <= radius ** 2:
                self.current_CP_i = i
                return px, py
        return None

    def get_next_label(self) -> chr:
        """
        :return: chr of Label for next Control Point
        """
        if not self.CP_list:
            return "A"

        return chr(ord(max(self.CP_list, key=lambda P: P[2])[2]) + 1)

    def NURBS_curve(self) -> None:
        """
        samples and draws NURBS curve
        """
        labels = [label for _, _, label, _ in self.CP_list]
        CPs = [(x, y) for x, y, _, _ in self.CP_list]
        weights = [w for _, _, _, w in self.CP_list]

        print(", ".join(f"{labels[i]}: {CPs[i]}" for i in range(len(CPs))))
        print(", ".join(f"w.{labels[i]}: {weights[i]}" for i in range(len(CPs))))

        nurbs = NurbsCurve(CPs, weights, 3)
        curve_points = nurbs.evaluate(samples=100)

        # draw
        for i in range(len(curve_points) - 1):
            self.canvas.create_line(curve_points[i][0], curve_points[i][1],
                                    curve_points[i + 1][0], curve_points[i + 1][1],
                                    fill="orange", width=2)

    def redraw_display(self) -> None:
        """
        Clears and redraws the entire canvas
        """
        self.canvas.delete("all")

        # lines btw CPs
        if len(self.CP_list) > 1:
            for i in range(len(self.CP_list)-1):
                self.canvas.create_line(self.CP_list[i][0], self.CP_list[i][1],
                                        self.CP_list[i+1][0], self.CP_list[i+1][1],
                                        fill="lightseagreen", width=round(self.CP_size / 4, 0))
        # CPs
        for x, y, char, w in self.CP_list:
            # vertice
            self.canvas.create_oval(x - self.CP_size / 2, y - self.CP_size / 2,
                                    x + self.CP_size / 2, y + self.CP_size / 2,
                                    fill="lightseagreen", outline="lightseagreen")
            # char label
            self.canvas.create_text(x + self.CP_size, y, text=char, fill="lightseagreen", anchor="w", font=("Arial", 12))

        # NURBS curve
        if len(self.CP_list) > 3:
            self.NURBS_curve()

    def show_weight_modifier(self) -> None:
        """
        Sets slider to w var and vice versa. Toggles slider visibility.
        """
        self.weight_var.set(self.CP_list[self.current_CP_i][3])
        self.weight_slider.set(self.CP_list[self.current_CP_i][3])

        self.weight_slider_frame.pack(side=tk.BOTTOM, fill=tk.X)

    def update_weight_from_slider(self, value: str) -> None:
        """
        Update the weight of the selected control point based on the slider's value
        """
        new_weight = float(value)
        self.update_weight(new_weight)

    def update_weight(self, new_weight: float) -> None:
        """
        Updates the weight of the selected Control Point and redraws
        """
        if self.current_CP_i:
            x, y, char, _ = self.CP_list[self.current_CP_i]
            self.CP_list[self.current_CP_i] = (x, y, char, new_weight)
            self.weight_var.set(new_weight)
            self.weight_slider.set(new_weight)

            self.redraw_display()

    # def show_knot_modifier(self) -> None:
    #     """
    #     Sets knot slider based on current Control Point knot value and redraws
    #     """
    #     knot_value = self.knot_list[self.current_CP_i]
    #     self.knot_var.set(knot_value)
    #     self.knot_slider.set(knot_value)
    #
    #     self.knot_slider_frame.pack(side=tk.BOTTOM, fill=tk.X)
    #
    # def update_knot_from_slider(self, value: str) -> None:
    #     """
    #     Update the knot value of the selected Control Point based on the slider's value
    #     """
    #     new_knot_value = float(value)
    #     self.update_knot(new_knot_value)
    #
    # def update_knot(self, new_knot_value: float) -> None:
    #     """
    #     Updates the knot value of the selected Control Point and redraws
    #     """
    #     if self.current_CP_i:
    #         self.knot_list[self.current_CP_i] = new_knot_value
    #         self.knot_var.set(new_knot_value)
    #         self.knot_slider.set(new_knot_value)
    #
    #         self.redraw_display()

    def clear_display(self) -> None:
        self.CP_list = []
        # self.knot_list = []
        self.redraw_display()


