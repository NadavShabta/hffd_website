# HFFD Website 🌐

This repository hosts the **HFFD (Hierarchical Fair Fractional Division)** algorithm and a web-based interface to interact with it.

## 🔢 About the Algorithm

The **HFFD algorithm** is designed to solve fair division problems involving multiple agents and divisible goods, such as budget items. It guarantees:
- **Fairness**: Each agent receives their proportional share based on preferences.
- **Efficiency**: The allocation maximizes global utility under given constraints.
- **Hierarchical structure**: The algorithm respects nested preferences and group constraints.

The algorithm takes a total budget and a set of agents' preferences over topics/items, then computes a fair fractional allocation using convex programming and optimization techniques.

## 🧰 About the Library

The backend logic is implemented as a **Python package**, structured for reusability and modular design:
- Core logic (`core.py`) handles the optimization and decomposition.
- Input validation and edge-case handling included.
- Compatible with multiple solvers (e.g. `cvxpy`, `scipy.optimize`).
- Designed for educational and research use.

### Key Technologies:
- Python 3.10+
- `cvxpy`, `numpy`, `pandas`
- Flask (for the web API)
- Gunicorn (for deployment)

## 🌍 About the Website

The website provides an intuitive interface to input budgets and preferences, and visualize fair allocation results in real time.

### Features:
- Submit preferences via the web form.
- View calculated allocations and decompositions instantly.
- Simple, mobile-friendly design for classroom or demo use.
- Hosted on `csariel.xyz` and deployed via Gunicorn + Nginx.

### Deployment Details:
- Virtual environment using `venv`
- Service management via `systemd` (`myservice`)
- Live instance: [http://nadav034.csariel.xyz](http://nadav034.csariel.xyz)

---

## 🚀 Getting Started (Dev)

```bash
git clone https://github.com/NadavShabta/hffd_website.git
cd hffd_website
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
