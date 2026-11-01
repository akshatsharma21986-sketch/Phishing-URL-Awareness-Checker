"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : main.py
Description   : Universal launcher for the Smart Lost & Found System.
Usage         : python main.py          (Launches the Desktop GUI)
                python main.py --cli    (Runs the Terminal CLI Interface)
=============================================================================
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="Smart Lost & Found Campus Intelligence System")
    parser.add_argument("--cli", action="store_true", help="Launch in Command-Line Interface mode")
    parser.add_argument("--scan", action="store_true", help="Run AI Smart Match Radar")
    parser.add_argument("--stats", action="store_true", help="Display recovery analytics")
    parser.add_argument("--seed", action="store_true", help="Re-seed sample campus dataset")

    args, remaining = parser.parse_known_args()

    if args.cli or args.scan or args.stats or args.seed:
        import cli
        cli.main()
    else:
        # Launch Desktop GUI by default
        try:
            import app_gui
            app_gui.launch_app()
        except Exception as e:
            print(f"[!] Unable to open graphical window ({e}). Defaulting to Terminal CLI mode.\n")
            import cli
            cli.main()


if __name__ == "__main__":
    main()
