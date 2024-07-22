import pandas as pd
from ortools.sat.python import cp_model


class CSP_Optim:
    def __init__(self, opt, orders_df):
        # Initialize optimization parameters
        self.cpu = opt.cpu
        self.max_per_reel = opt.max_per_reel
        self.max_time = opt.max_time

        self.unit = opt.unit
        self.magnification = opt.magnification
        self.bin_capacity = opt.bin_capacity

        self.format = opt.format
        self.stock_df = opt.stock_df

        self.model = cp_model.CpModel()
        # Filter out orders with quantity=0
        self.orders_df = self.filter_orders(orders_df)

        self.prepare_data()  # Prepare data for optimization
        self.create_variables()  # Create variables for optimization
        self.add_constraints()  # Add constraints to the model

    def solve(self):
        # Define objective: minimize the number of reels used
        objective = cp_model.LinearExpr.Sum(self.is_reel_vars.values())
        self.model.Minimize(objective)

        # Create solver and set parameters
        self.solver = cp_model.CpSolver()
        self.solver.parameters.num_search_workers = self.cpu
        self.solver.parameters.max_time_in_seconds = self.max_time
        printer = cp_model.ObjectiveSolutionPrinter()

        # Solve the model
        status = self.solver.Solve(self.model, printer)
        status_name = self.solver.StatusName(status)
        print("Status name:", status_name)
        print("Time =", self.solver.WallTime(), "ms")
        if status_name in ["OPTIMAL", "FEASIBLE"]:
            self.extract_solution()  # Extract the solution
        return status_name

    def get_solution(self):
        return self.solution

    def get_unused_df(self):
        return self.unused_df

    @staticmethod
    def filter_orders(orders_df):
        # Filter out orders with quantity greater than 0
        return orders_df[orders_df["qty"] > 0].reset_index(drop=True)

    def prepare_data(self):
        # Prepare order data
        # Convert orders_df to dictionary
        self.orders_dict = self.orders_df.to_dict("records")
        self.order_items = list(range(len(self.orders_df)))  # Indices of orders

        # Prepare reel data
        # Create list of reels based on total quantity
        self.reels = list(range(self.orders_df["qty"].sum()))

        # Prepare stock data
        # Convert stock_df to dictionary
        self.stock_dict = self.stock_df.to_dict("records")
        self.stock_items = list(range(len(self.stock_df)))  # Indices of stock items

    def create_variables(self):
        # Create order variables
        self.order_vars = {}
        for order in self.order_items:
            for reel in self.reels:
                var_name = f"order_vars[{order},{reel}]"
                # Variable representing quantity of an order in a reel
                self.order_vars[(order, reel)] = self.model.NewIntVar(
                    0, self.max_per_reel, var_name
                )

        # Create boolean variables to indicate if a reel is used
        self.is_reel_vars = {}
        for reel in self.reels:
            var_name = f"is_reel_vars[{reel}]"
            # Boolean variable for reel usage
            self.is_reel_vars[reel] = self.model.NewBoolVar(var_name)
            # Provide a hint for the solver
            self.model.AddHint(self.is_reel_vars[reel], 0)

        # Create stock variables
        self.stock_vars = {}
        for stock in self.stock_items:
            for reel in self.reels:
                var_name = f"stock_vars[{stock},{reel}]"
                # Variable representing quantity of a stock item in a reel
                self.stock_vars[(stock, reel)] = self.model.NewIntVar(
                    0, self.max_per_reel, var_name
                )
                # Provide a hint for the solver
                self.model.AddHint(self.stock_vars[(stock, reel)], 0)

    def add_constraints(self):
        # Ensure that the total quantity for each order is met
        for order in self.order_items:
            order_qty = self.orders_dict[order]["qty"]
            self.model.Add(
                sum(self.order_vars[order, reel] for reel in self.reels) == order_qty
            )

        # Ensure that the total quantity in each reel does not exceed the maximum per reel
        for reel in self.reels:
            sum_order_qty = sum(
                self.order_vars[(order, reel)] for order in self.order_items
            )
            sum_stock_qty = sum(
                self.stock_vars[(stock, reel)] for stock in self.stock_items
            )
            self.model.Add(sum_order_qty + sum_stock_qty <= self.max_per_reel)

        # Ensure that the total width of items in each reel is within the bin capacity limits
        for reel in self.reels:
            sum_order_width = sum(
                self.order_vars[(order, reel)] * self.orders_dict[order]["width"]
                for order in self.order_items
            )
            sum_stock_width = sum(
                self.stock_vars[(stock, reel)] * self.stock_dict[stock][self.unit]
                for stock in self.stock_items
            )
            sum_width = sum_order_width + sum_stock_width
            self.model.Add(
                sum_width <= self.is_reel_vars[reel] * self.bin_capacity["ub"]
            )
            self.model.Add(
                sum_width >= self.is_reel_vars[reel] * self.bin_capacity["lb"]
            )

        # Ensure reels are used in sequence (i.e., no gaps in reel usage)
        for reel in range(1, len(self.reels)):
            self.model.Add(self.is_reel_vars[reel - 1] >= self.is_reel_vars[reel])

        # Ensure the total number of used reels is within the limit
        self.model.Add(
            cp_model.LinearExpr.Sum(self.is_reel_vars.values()) <= len(self.reels)
        )

    def extract_solution(self):
        solution = []
        unused_orders = {order["width"]: order["qty"] for order in self.orders_dict}

        # Iterate over each reel
        for reel in self.reels:
            is_reel = self.solver.Value(
                self.is_reel_vars[reel]
            )  # Check if reel is used
            if is_reel != 1:  # Skip if reel is not used
                continue

            # Extract values for orders and stocks
            packed_orders = self.extract_order_values(reel, unused_orders)
            packed_stocks = self.extract_stock_values(reel)

            # Format the solution for the current reel
            solution.append(self.format_solution(packed_orders, packed_stocks))

        self.solution = solution
        self.unused_df = pd.DataFrame(unused_orders.items(), columns=["width", "qty"])

    def extract_order_values(self, reel, unused_orders):
        """Extract order values for a given reel."""
        packed_orders = []
        for order in self.order_items:
            order_width = self.orders_dict[order]["width"]
            qty = self.solver.Value(self.order_vars[order, reel])
            packed_orders.extend([order_width / self.magnification] * int(qty))
            unused_orders[order_width] -= qty
        return packed_orders

    def extract_stock_values(self, reel):
        """Extract stock values for a given reel."""
        packed_stocks = []
        for stock in self.stock_items:
            qty = self.solver.Value(self.stock_vars[stock, reel])
            if qty > 0:
                stock_width = self.stock_dict[stock][self.unit]
                packed_stocks.extend([stock_width / self.magnification] * int(qty))
        return packed_stocks

    def format_solution(self, packed_orders, packed_stocks):
        """Format the solution for a given reel."""
        packed = packed_orders + packed_stocks
        packed.sort(reverse=True)  # Sort orders and stocks by width in descending order
        solution_format = self.format.copy()  # Copy the format for the solution

        # Update the solution format with the total quantity and remarks
        solution_format.update(
            {
                "total": sum(packed),
                "qty": 1,
                "remark": f"{packed_stocks}",
            }
        )

        # Update the solution format with the widths of the orders and stocks
        for idx, pack in enumerate(packed, start=1):
            solution_format.update({f"width{idx}": pack})

        return solution_format
