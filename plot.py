from pathlib import Path

import click

from main import plot


def plotter(ffs, output_dir, input_dir="industry", names=None, **kwargs):
    if names is None:
        names = ffs
    dirs = [f"output/{input_dir}/{ff}" for ff in ffs]
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)
    plot(output_dir, dirs, names, **kwargs)


@click.command()
@click.argument("forcefields", nargs=-1)
@click.option("--input-dir", "-d", default="industry")
@click.option("--filter-records", "-r", default=None)
@click.option("--negate", "-n", is_flag=True, default=False)
@click.option("--output_dir", "-o", default="/tmp")
def main(forcefields, input_dir, filter_records, negate, output_dir):
    if filter_records is not None:
        # assume it's the name of a file
        with open(filter_records) as inp:
            filter_records = [line.strip() for line in inp]
    plotter(
        forcefields,
        output_dir,
        input_dir=input_dir,
        filter_records=filter_records,
        negate=negate,
    )


if __name__ == "__main__":
    main()
