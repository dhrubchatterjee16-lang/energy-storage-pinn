# Energy Storage PINN: Battery Degradation & Marcus-Hush-Chidsey Kinetics

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Energy__storage-yellow)](https://huggingface.co/spaces/dhrubchatterjee/Energy_storage)
[![Tests: Passing](https://img.shields.io/badge/tests-6%2F6%20passed-brightgreen.svg)](tests/)

**Energy Storage PINN** is an open-source Scientific Machine Learning (SciML) engine coupling Physics-Informed Neural Networks (PINNs) with quantum Marcus-Hush-Chidsey (MHC) interfacial electron transfer kinetics, diffusion-controlled Solid Electrolyte Interphase (SEI) growth, and finite-sample inductive conformal uncertainty quantification.

---

## 🔬 Scientific Foundations & Governing Equations

### 1. Quantum Marcus-Hush-Chidsey (MHC) Kinetics
Replaces traditional Butler-Volmer exponential approximations that break down at high fast-charging overpotentials ($\eta > 0.15 \, \mathrm{V}$). Integrates across the Fermi-Dirac continuum of electronic states:

$$k_{\mathrm{MHC}}(\eta) = k_0 \int_{-\infty}^{\infty} \exp\left(-\frac{(x - \lambda \pm \eta)^2}{4 \lambda k_B T}\right) \frac{1}{1 + \exp(x)} \, dx$$

where $\lambda$ is the solvent and lattice reorganization energy ($\sim 0.85 \, \mathrm{eV}$) and $k_B T$ is thermal energy.

### 2. Coupled SEI Passivation & Chemomechanical Fatigue
SEI growth couples solvent diffusion across the resistive layer with mechanical intercalation-induced particle cracking:

$$j_{\mathrm{sei}} = F \left(\frac{D_{\mathrm{eff}} c_{\mathrm{bulk}}}{\delta_{\mathrm{sei}}}\right) \exp\left(-\frac{\alpha F}{R T} \eta_{\mathrm{side}}\right) \cdot \left(1 + 0.8 \cdot C_{\mathrm{rate}}^{1.3}\right)$$

$$\frac{d\delta_{\mathrm{sei}}}{dt} = \frac{j_{\mathrm{sei}}}{F} V_{\mathrm{sei}} + \dot{\delta}_{\mathrm{mech\_crack}}$$

$$\Delta Q_{\mathrm{lost}} = \int j_{\mathrm{sei}} A \, dt + Q_{\mathrm{crack}}$$

### 3. Nernst-Planck Interfacial Electrodiffusion
Preserves second-law thermodynamic entropy generation ($\dot{S}_{\mathrm{gen}} \ge 0$) under non-equilibrium ion transport:

$$J_{\mathrm{Li}^+} = - D_{\mathrm{Li}^+} \nabla c - \frac{z F D_{\mathrm{Li}^+}}{R T} c \nabla \phi$$

---

## ⚡ Quickstart

### Installation

```bash
pip install -e .
```

### Python API

```python
from energy_storage import BatterySEIPINN, MarcusHushChidseyKinetics, ConformalBatteryUQ

# 1. 500-Cycle Aging Simulation with High C-Rate Fatigue
pinn = BatterySEIPINN(nominal_capacity_Ah=2.5)
traj = pinn.forecast_aging_trajectory(cycles=500, c_rate=1.5, temp_C=30.0)

print(f"Initial Capacity: {traj['initial_capacity_Ah']} Ah")
print(f"Final Retained Capacity: {traj['final_capacity_Ah']} Ah")
print(f"State of Health (SoH): {traj['final_soh_pct']}%")
print(f"End-of-Life Reached (<80%): {traj['end_of_life_reached']}")
print(f"Final SEI Thickness: {traj['final_sei_thickness_nm']} nm")

# 2. Conformal Uncertainty Bounds (90% Finite-Sample Guarantee)
uq = ConformalBatteryUQ().predict_soh_interval(traj["final_soh_pct"], confidence=0.90)
print(f"90% Conformal SoH Bounds: [{uq['lower_bound_pct']}%, {uq['upper_bound_pct']}%]")

# 3. Marcus-Hush-Chidsey Quantum Interfacial Rate
mhc = MarcusHushChidseyKinetics()
rate = mhc.compute_mhc_rate(overpotential_v=0.25)
print(f"MHC Interfacial Transfer Rate: {rate:.4e} m/s")
```

---

## 🖥️ Command-Line Interface (CLI)

```bash
# Forecast 600 cycles at 2C fast-charging
energy-pinn forecast --capacity 2.5 --cycles 600 --crate 2.0 --temp 35.0 --confidence 0.95

# Compute Marcus-Hush-Chidsey rate constant
energy-pinn mhc --overpotential 0.20 --lambda-ev 0.85
```

---

## 🧪 Automated Verification Suite

```bash
python run_tests.py
```
```text
Ran 6 tests in 0.029s
OK - ALL ENERGY-STORAGE-PINN TESTS PASSED (6/6)!
```

---

## 📚 References & Scientific Foundations
- Chidsey, C. E. (1991). *Free energy and temperature dependence of electron transfer at the gold-electrolyte interface*. Science, 251(4996), 919-922.
- Marcus, R. A. (1965). *On the theory of electron-transfer reactions. VI. Unified treatment for homogeneous and electrochemical systems*. Journal of Chemical Physics, 43(2), 679-701.
- Safari, M., & Delacourt, C. (2011). *Mathematical modeling of lithium-ion batteries: Single-particle model with SEI layer growth*. Journal of The Electrochemical Society, 158(12), A1436.
- Shafer, G., & Vovk, V. (2008). *A Tutorial on Conformal Prediction*. Journal of Machine Learning Research, 9, 371-421.

---

## 📄 License
MIT License. Copyright (c) 2026 Dhrub Chatterjee.
