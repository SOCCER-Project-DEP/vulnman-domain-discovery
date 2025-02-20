import os

import click


@click.command()
@click.option("-p", "--prescan", is_flag=True, help="Run prescan")
@click.option("-s", "--scan", is_flag=True, help="Run scan")
@click.option("-t", "--target", help="Target domain")
def main(prescan, scan, target):
    if prescan:
        # call prescan.py from shell because it might modify current file
        os.system("python src/prescan.py")
    if scan:
        if target is None:
            print("ERROR: --target is required for scan")
            return
        os.system(f"poetry run python src/main.py --target={target}")


if __name__ == "__main__":
    main()
