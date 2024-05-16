# Paper-APS

## Introduction

`Paper-APS` is an **Advanced Planning and Scheduling (APS)** system specifically designed for paper mills to address the **Cutting Stock Problem (CSP)**. This system optimizes the arrangement of different order widths onto parent rolls. Successful implementation of this system has reduced production costs by **8%** and inventory levels by **67%**, promoting **digital transformation** and **smart manufacturing** in the paper industry.

## Background

- **Production Planning**:
  Based on order requirements, different widths are pre-arranged onto fixed-width parent rolls, such as **129 inches**.

- **Production Constraints**:
  1. The slitter rewinder cannot handle excess waste exceeding **1 inch**.
  2. The slitter rewinder can cut a maximum of **5 rolls** at a time.

- **Optimization Goal**:
  The goal is to minimize the number of parent rolls used, thereby maximizing resource utilization.

Through **mathematical optimization** and **linear programming** using OR-Tools, combined with actual production data and operational constraints, this system devises the most optimal production strategy.

## Quickstart

To get started with `Paper-APS`, follow these steps:

1. **Clone the Repository**:
    ```sh
    git clone [Project URL]
    cd paper_aps
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run Example**:
    ```sh
    python paper_aps/main.py
    ```

4. **Get Help**:
    ```sh
    python paper_aps/main.py --help
    ```

## Example

Order data (`example_orders.json`) includes various order widths, such as **5 rolls of 43 inches**, **9 rolls of 36 inches**, etc. All orders need to be arranged onto machines with a width setting of **128 to 129 inches** based on `machine_specs.json`, and common stock rolls (`stocks.json`) are used to ensure compliance with operational constraints.

### Output Example

```plaintext
Solution 0, time = 11.53 s, objective = 14
Solution 1, time = 11.62 s, objective = 13
Status name: OPTIMAL
Time = 11.6722851 ms
APS:
    width1  width2  width3  width4  width5  unit  total  remark  qty
0    43.0    43.0    43.0     NaN     NaN  inch  129.0      []    1
1    43.0    36.0    25.0    25.0     NaN  inch  129.0      []    1
2    43.0    31.0    27.0    27.0     NaN  inch  128.0      []    1
3    36.0    36.0    36.0    21.0     NaN  inch  129.0  [21.0]    2
4    36.0    32.0    32.0    29.0     NaN  inch  129.0  [29.0]    1
5    36.0    31.0    31.0    31.0     NaN  inch  129.0      []    1
6    34.0    34.0    34.0    27.0     NaN  inch  129.0      []    1
7    34.0    32.0    32.0    31.0     NaN  inch  129.0      []    1
8    34.0    32.0    31.0    31.0     NaN  inch  128.0      []    2
9    27.0    27.0    25.0    25.0    25.0  inch  129.0      []    2
```

## Notices

The following features are currently disabled and the project is provided for reference only:

- Multi-machine configuration
- Unit selection
- Multiple common stock roll tables
- Front-end interface display
- Advanced algorithms for rapid handling of large order volumes
- Enhanced algorithms to minimize the number of scheduling patterns
- Test functionality
- Packaging into software packages

Please contact the developer if you have any questions or require these features.

## License

This project is licensed under the **MIT License**. For more details, see the [LICENSE](LICENSE) file.

## Contact

- **Author**: HungCheng Chen
- **Email**: [hcchen.nick@gmail.com](mailto:hcchen.nick@gmail.com)
