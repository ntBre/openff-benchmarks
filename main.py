import logging
import os
import time
import warnings
from pathlib import Path

import click
import numpy
import pandas
import seaborn as sea
from matplotlib import pyplot
from openff.toolkit.utils import OpenEyeToolkitWrapper
from yammbs import MoleculeStore
from yammbs.cached_result import CachedResultCollection

assert OpenEyeToolkitWrapper().is_available()

# try to suppress stereo warnings - from lily's valence-fitting
# curate-dataset.py
logging.getLogger("openff").setLevel(logging.ERROR)

# suppress divide by zero in numpy.log
warnings.filterwarnings(
    "ignore", message="divide by zero", category=RuntimeWarning
)

pandas.set_option("display.max_columns", None)


@click.command()
@click.option("--forcefield", "-f", default="force-field.offxml")
@click.option("--dataset", "-d", default="datasets/cache/industry.json")
@click.option("--sqlite-file", "-s", default="tmp.sqlite")
@click.option("--out-dir", "-o", default=".")
@click.option("--procs", "-p", default=16)
@click.option("--invalidate-cache", "-i", is_flag=True, default=False)
def main(forcefield, dataset, sqlite_file, out_dir, procs, invalidate_cache):
    if invalidate_cache and os.path.exists(sqlite_file):
        os.remove(sqlite_file)
    if os.path.exists(sqlite_file):
        print(f"loading existing database from {sqlite_file}", flush=True)
        store = MoleculeStore(sqlite_file)
    else:
        print(f"loading cached dataset from {dataset}", flush=True)
        crc = CachedResultCollection.from_json(dataset)
        store = MoleculeStore.from_cached_result_collection(crc, sqlite_file)

    print("started optimizing store", flush=True)
    start = time.time()
    store.optimize_mm(force_field=forcefield, n_processes=procs)
    print(f"finished optimizing after {time.time() - start} sec")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    make_csvs(store, forcefield, out_dir)
    plot(out_dir)


def make_csvs(store, forcefield, out_dir):
    print("getting DDEs")
    store.get_dde(forcefield, skip_check=True).to_csv(f"{out_dir}/dde.csv")
    print("getting RMSDs")
    store.get_rmsd(forcefield, skip_check=True).to_csv(f"{out_dir}/rmsd.csv")
    print("getting TFDs")
    store.get_tfd(forcefield, skip_check=True).to_csv(f"{out_dir}/tfd.csv")
    print("getting internal coordinate RMSDs")
    store.get_internal_coordinate_rmsd(forcefield, skip_check=True).to_csv(
        f"{out_dir}/icrmsd.csv"
    )


def load_bench(d: Path, filter_records, negate) -> pandas.DataFrame:
    """Load the DDE, RMSD, TFD, and ICRMSD results from the CSV files in ``d``
    and return the result as a merged dataframe"""
    dde = pandas.read_csv(d / "dde.csv")
    dde.columns = ["rec_id", "dde"]
    rmsd = pandas.read_csv(d / "rmsd.csv")
    rmsd.columns = ["rec_id", "rmsd"]
    tfd = pandas.read_csv(d / "tfd.csv")
    tfd.columns = ["rec_id", "tfd"]
    icrmsd = pandas.read_csv(d / "icrmsd.csv")
    icrmsd.columns = ["rec_id", "bonds", "angles", "dihedrals", "impropers"]
    ret = (
        dde.merge(rmsd)
        .pipe(pandas.DataFrame.merge, tfd)
        .pipe(pandas.DataFrame.merge, icrmsd)
    )
    if filter_records is not None:
        if negate:
            ret = ret[~ret["rec_id"].astype(str).isin(filter_records)]
        else:
            ret = ret[ret["rec_id"].astype(str).isin(filter_records)]
    print(f"loaded {ret.shape} rows for {d}")
    return ret


def load_benches(
    ffs, in_dirs, filter_records, negate
) -> list[pandas.DataFrame]:
    """Load a sequence of dataframes, one per ``ff``. If there are multiple
    ``in_dirs``, each ``ff`` is loaded from each ``in_dir`` and stacked into a
    single dataframe."""
    ret = list()
    for ff in ffs:
        df = load_bench(Path(in_dirs[0]) / ff, filter_records, negate)
        for d in in_dirs[1:]:
            df = pandas.concat(
                [df, load_bench(Path(d) / ff, filter_records, negate)]
            )
        ret.append(df)
    return ret


def merge_metrics(dfs, names, metric: str):
    assert len(dfs) > 0, "must provide at least one dataframe"
    df = dfs[0][["rec_id", metric]].copy()
    df.columns = ["rec_id", names[0]]
    for i, d in enumerate(dfs[1:]):
        name = names[i + 1]
        to_add = d[["rec_id", metric]].copy()
        to_add.columns = ["rec_id", name]
        df = df.merge(to_add, on="rec_id")
    return df


def plot_ddes(dfs: list[pandas.DataFrame], names, out_dir):
    figure, axis = pyplot.subplots(figsize=(6, 4))
    ddes = merge_metrics(dfs, names, "dde")
    ax = sea.histplot(
        data=ddes.iloc[:, 1:],
        binrange=(-15, 15),
        bins=16,
        element="step",
        fill=False,
    )
    label = "DDE (kcal mol$^{-1}$)"
    ax.set_xlabel(label)
    pyplot.savefig(f"{out_dir}/dde.png", dpi=300)
    pyplot.close()


def plot_rmsds(dfs: list[pandas.DataFrame], names, out_dir):
    figure, axis = pyplot.subplots(figsize=(6, 4))
    rmsds = merge_metrics(dfs, names, "rmsd")
    ax = sea.kdeplot(data=numpy.log10(rmsds.iloc[:, 1:]))
    ax.set_xlim((-2.0, 0.7))
    ax.set_xlabel("Log RMSD")
    pyplot.savefig(f"{out_dir}/rmsd.png", dpi=300)
    pyplot.close()

    ax = sea.ecdfplot(rmsds.iloc[:, 1:])
    ax.set_xlabel("RMSD (Å)")
    pyplot.savefig(f"{out_dir}/rmsd_cdf.png", dpi=300)
    pyplot.close()


def plot_tfds(dfs: list[pandas.DataFrame], names, out_dir):
    figure, axis = pyplot.subplots(figsize=(6, 4))
    tfds = merge_metrics(dfs, names, "tfd")
    ax = sea.kdeplot(data=numpy.log10(tfds.iloc[:, 1:]))
    ax.set_xlim((-4.0, 0.5))
    ax.set_xlabel("Log TFD")
    pyplot.savefig(f"{out_dir}/tfd.png", dpi=300)
    pyplot.close()

    ax = sea.ecdfplot(tfds.iloc[:, 1:])
    ax.set_xlabel("TFD")
    pyplot.savefig(f"{out_dir}/tfd_cdf.png", dpi=300)
    pyplot.close()


def plot_icrmsds(dfs, names, out_dir):
    titles = {
        "bonds": "Bond Internal Coordinate RMSDs",
        "angles": "Angle Internal Coordinate RMSDs",
        "dihedrals": "Proper Torsion Internal Coordinate RMSDs",
        "impropers": "Improper Torsion Internal Coordinate RMSDs",
    }
    ylabels = {
        "bonds": "Bond error (Å)",
        "angles": "Angle error (̂°)",
        "dihedrals": "Proper Torsion error (°)",
        "impropers": "Improper Torsion error(°)",
    }
    for m in ["bonds", "angles", "dihedrals", "impropers"]:
        full = merge_metrics(dfs, names, m)
        df = full.iloc[:, 1:]
        # only take the data points within f standard deviations of the mean
        if f := os.environ.get("OFF_BENCH_F", None):
            std, mean = df.std(), df.mean()
            f = float(f)
            cond = ((df > mean - f * std) & (df < mean + f * std)).all(1)
            df = df[cond]
            filt = full[~cond]["rec_id"].to_list()
            print(f"filtered {len(filt)} {m}:")
            print(filt)
        ax = sea.boxplot(df)
        pyplot.title(titles[m])
        ax.set_ylabel(ylabels[m])
        pyplot.savefig(f"{out_dir}/{m}.png", dpi=300)
        pyplot.close()


def stats(dfs, names, out_dir):
    with open(f"{out_dir}/stats.tex", "w") as out:
        for m in [
            "dde",
            "rmsd",
            "tfd",
            "bonds",
            "angles",
            "dihedrals",
            "impropers",
        ]:
            for n, df in zip(names, dfs):
                data = df[df[m].notnull()][m]
                avg = numpy.mean(data)
                mae = numpy.mean(numpy.abs(data))
                mdn = numpy.median(data)
                std = numpy.std(data)
                o = m.upper()
                print(
                    f"{n}&{o}& {avg:.2f} & {mae:.2f} & {mdn:.2f} & {std:.2f}"
                    " \\\\",
                    file=out,
                )
            print("\\hline", file=out)


def plot(out_dir, ffs, in_dirs, names=None, filter_records=None, negate=False):
    """Plot each of the `dde`, `rmsd`, and `tfd` CSV files found in `in_dirs`
    and write the resulting PNG images to out_dir. If provided, take the plot
    legend entries from `names` instead of `in_dirs`. If `filter_records` is
    provided, restrict the plot only to those records. `negate` swaps the
    comparison to include only the records *not* in `filter_records`.

    """
    # default to directory names
    if names is None:
        names = in_dirs

    dfs = load_benches(ffs, in_dirs, filter_records, negate)

    for name, df in zip(names, dfs):
        df.to_csv(f"{out_dir}/{name}.csv")

    plot_ddes(dfs, names, out_dir)
    plot_rmsds(dfs, names, out_dir)
    plot_tfds(dfs, names, out_dir)
    plot_icrmsds(dfs, names, out_dir)

    stats(dfs, names, out_dir)


if __name__ == "__main__":
    main()
