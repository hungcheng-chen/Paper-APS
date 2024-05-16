import argparse
import os

import pandas as pd


class Opts(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Advanced Planning and Scheduling (APS) for Paper Mills using OR-Tools"
        )
        self.parser.add_argument(
            "--unit",
            type=str,
            default="inch",
            choices=["inch"],
            help="Measurement unit [inch]",
        )
        self.parser.add_argument(
            "--orders_path",
            type=str,
            default="data/example_orders.json",
            help="Path to the orders JSON file",
        )
        self.parser.add_argument(
            "--cpu", default=4, type=int, help="Number of CPU cores to use (default: 4)"
        )
        self.parser.add_argument(
            "--max_time",
            default=30,
            type=int,
            help="Time limit in seconds (default: 30)",
        )
        self.parser.add_argument(
            "--magnification",
            default=100,
            type=int,
            help="Magnification factor for measurements (default: 100)",
        )
        self.parser.add_argument(
            "--max_per_reel",
            default=5,
            type=int,
            help="Number of orders per reel (default: 5)",
        )

    def parse(self, args=""):
        if args == "":
            opt = self.parser.parse_args()
        else:
            opt = self.parser.parse_args(args)
        # TODO
        opt.unit = "inch"
        opt.orders_path = "data/example_orders.json"
        # Setting paths
        opt.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        opt.src_path = os.path.abspath(os.path.dirname(__file__))
        opt.machine_specs_path = os.path.join(opt.src_path, "data/machine_specs.json")
        opt.stock_path = os.path.join(opt.src_path, "data/stocks.json")
        opt.orders_path = os.path.join(opt.root_path, opt.orders_path)

        # Load machine specifications
        machine_specs = self.load_machine_specs(opt.machine_specs_path)
        opt.specs = machine_specs[machine_specs["unit"] == opt.unit]

        # Set bin capacity
        opt.bin_capacity = self.set_bin_capacity(opt.specs, opt.magnification)
        # Preprocess orders
        opt.orders_df = self.preprocess_orders(opt.orders_path, opt.magnification)
        # Prepare stock data
        opt.stock_df = self.prepare_stock(opt.stock_path, opt.unit, opt.magnification)

        # Output format
        opt.format = {
            **{f"width{i}": None for i in range(1, 6)},  # Width format
            "unit": opt.unit,  # Unit
            "total": int,  # Total width
            "remark": "",  # Stock remarks
        }
        return opt

    def load_machine_specs(self, path: str) -> pd.DataFrame:
        """Load machine specifications from a JSON file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Machine specs file not found: {path}")
        with open(path, encoding="utf-8") as f:
            machine_specs = pd.read_json(f)
        return machine_specs

    def set_bin_capacity(self, specs: pd.DataFrame, magnification: int) -> dict:
        """Set bin capacity based on machine specifications and magnification factor"""
        bin_capacity = {
            "lb": int(specs["lb"].iloc[0] * magnification),
            "ub": int(specs["ub"].iloc[0] * magnification),
        }
        return bin_capacity

    def preprocess_orders(self, path: str, magnification: int) -> pd.DataFrame:
        """Preprocess order data from a JSON file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Orders file not found: {path}")
        with open(path, encoding="utf-8") as f:
            orders_df = pd.read_json(f)

        orders_df = orders_df.groupby("width").qty.sum().reset_index()
        orders_df = orders_df.sort_values(by="width", ascending=False).reset_index(
            drop=True
        )
        orders_df["width"] = (orders_df["width"] * magnification).astype(int)
        return orders_df

    def prepare_stock(self, path: str, unit: str, magnification: int) -> pd.DataFrame:
        """Prepare stock data from a JSON file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Stock file not found: {path}")
        with open(path, encoding="utf-8") as f:
            stock_df = pd.read_json(f)

        stock_df[unit] = (stock_df[unit] * magnification).astype(int)
        return stock_df
