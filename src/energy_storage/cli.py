"""
Command-Line Interface for Energy Storage PINN
"""

import argparse
import sys
import json
from .sei_pinn import BatterySEIPINN
from .mhc_kinetics import MarcusHushChidseyKinetics, MHCParameters
from .conformal import ConformalBatteryUQ

def main():
    parser = argparse.ArgumentParser(
        prog="energy-pinn",
        description="Energy Storage PINN: Battery Degradation & Marcus-Hush-Chidsey Kinetics Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # aging forecast subcommand
    aging_parser = subparsers.add_parser("forecast", help="Forecast battery SEI growth & capacity fade")
    aging_parser.add_argument("--capacity", type=float, default=2.5, help="Nominal cell capacity (Ah)")
    aging_parser.add_argument("--cycles", type=int, default=500, help="Total cycle count")
    aging_parser.add_argument("--crate", type=float, default=1.0, help="Charge/discharge C-rate")
    aging_parser.add_argument("--temp", type=float, default=25.0, help="Operating temperature (°C)")
    aging_parser.add_argument("--confidence", type=float, default=0.90, help="Conformal confidence level")

    # mhc subcommand
    mhc_parser = subparsers.add_parser("mhc", help="Compute Marcus-Hush-Chidsey electron transfer rate")
    mhc_parser.add_argument("--overpotential", type=float, default=0.15, help="Overpotential in Volts")
    mhc_parser.add_argument("--lambda-ev", type=float, default=0.85, help="Reorganization energy in eV")
    mhc_parser.add_argument("--temp-k", type=float, default=298.15, help="Temperature in Kelvin")

    args = parser.parse_args()

    if args.command == "forecast":
        model = BatterySEIPINN(nominal_capacity_Ah=args.capacity)
        traj = model.forecast_aging_trajectory(
            cycles=args.cycles,
            c_rate=args.crate,
            temp_C=args.temp
        )
        uq = ConformalBatteryUQ().predict_soh_interval(
            traj["final_soh_pct"],
            confidence=args.confidence
        )
        print("\n--- Battery SEI Aging & Degradation Forecast ---")
        print(f"Nominal Capacity:    {traj['initial_capacity_Ah']} Ah")
        print(f"Retained Capacity:   {traj['final_capacity_Ah']} Ah after {args.cycles} cycles")
        print(f"State of Health:     {traj['final_soh_pct']}%")
        print(f"SEI Layer Growth:    5.00 nm -> {traj['final_sei_thickness_nm']} nm")
        print(f"Internal SEI R:      {traj['final_r_sei_ohm']} Ohm")
        print(f"Conformal Bounds:    [{uq['lower_bound_pct']}%, {uq['upper_bound_pct']}%] (Coverage: {int(args.confidence*100)}%)\n")

    elif args.command == "mhc":
        params = MHCParameters(
            reorganization_energy_ev=args.lambda_ev,
            temperature_k=args.temp_k
        )
        kinetics = MarcusHushChidseyKinetics(params)
        rate = kinetics.compute_mhc_rate(args.overpotential)
        print("\n--- Marcus-Hush-Chidsey Interfacial Kinetics ---")
        print(f"Overpotential:       {args.overpotential} V")
        print(f"Reorganization:      {args.lambda_ev} eV")
        print(f"MHC Net Rate:        {rate:.4e} m/s\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
