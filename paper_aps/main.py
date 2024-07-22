import argparse

import pandas as pd
from models import CSP_Optim
from opts import Opts


def main(opt: argparse.Namespace):
    # Load orders DataFrame from options
    orders_df = opt.orders_df
    result = []

    # Initialize the StockOptim object with the provided options and orders
    stock_opt = CSP_Optim(opt, orders_df)

    # Solve the optimization problem
    status_name = stock_opt.solve()

    # If a feasible or optimal solution is found, extract the solution
    if status_name in ["OPTIMAL", "FEASIBLE"]:
        result.extend(stock_opt.get_solution())
    else:
        print("No solution found")

    # Sort the results based on the width columns in descending order
    result.sort(
        key=lambda x: (x.get("width1"), x.get("width2"), x.get("width3")),
        reverse=True,
    )

    # Convert the result list to a DataFrame
    APS = pd.DataFrame(result)

    # Group by all columns except 'qty' and sum the 'qty' values for identical orders
    group_fields = [col for col in APS.columns if col != "qty"]
    APS = APS.groupby(group_fields, dropna=False, sort=False)["qty"].sum().reset_index()

    # Print the final aggregated DataFrame
    print("APS:\n", APS)
    return


if __name__ == "__main__":
    # Parse command line options
    opt = Opts().parse()
    # Execute the main function with the parsed options
    main(opt)
