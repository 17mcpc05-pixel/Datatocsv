import json
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

from src.consts import activity_name_idx_map
from src.consts import ap_rssi_name_map
from src.consts import location_name_idx_map
from src.consts import participant_lookup
from src.consts import pir_name_idx_map
from src.consts import pir_name_map
from src.consts import pir_names_sorted
from src.consts import train_test_id_split
from src.dtypes import ProcessedSequence
from src.dtypes import RawSequence
from src.io import dump_df
from src.io import dump_json


def tabularise_intervals(
    seqs, lookup: dict[str, int], start: int, end: int, delta: float = 0.1, return_time: bool = False
):
    """Resample a CSV file with columns of [name, start, end] to a matrix sampled at `1 / delta` Hz"""
    time = np.arange(start, end, delta)
    data = np.zeros((len(time), len(lookup)), dtype=float)
    for row in seqs.itertuples():
        data[(time >= row.start) & (time < row.end), lookup[row.name]] += 1.0
    if return_time:
        return time, data
    return data


def make_tabular_labels(seq: RawSequence, kind: str, delta: float = 0.1, return_raw=False):
    """Resample a labels file (i.e. activity or location) to a tabular format; see `tabularise_intervals`"""

    if kind == "activity":
        columns = json.load(open("assets/activity_labels.json"))
        annotations = seq.activity
        lookup = activity_name_idx_map

    elif kind == "location":
        columns = json.load(open("assets/location_labels.json"))
        annotations = seq.location
        lookup = location_name_idx_map

    else:
        raise ValueError(f"Unknown annotation type {kind}, expected one of ‘location’, ‘activity’")

    # Build the matrix
    values = []
    time = None
    for ann in annotations.values():
        time, value = tabularise_intervals(
            seqs=ann,
            lookup=lookup,
            start=seq.meta.start,
            end=seq.meta.end,
            return_time=True,
            delta=delta,
        )
        values.append(value)

    # Build data frame, including the time column
    labels = pd.DataFrame(np.mean(values, axis=0), columns=columns)
    labels.insert(0, "t", time)

    if return_raw:
        for di, df in enumerate(values):
            df = pd.DataFrame(df, columns=columns)
            df.insert(0, "t", time)
            values[di] = df
        return labels, values
    return labels


def rename_file(root, old, new):
    old = root / old
    new = root / new

    if not old.exists():
        logger.warning(f"Cannot rename {old=} to {new=} since old doesn't exist")
    else:
        if not new.exists():
            # Note: this will silently overwrite
            old.rename(new)


def standardise_sequences(root, force: bool = False, delta: float = 0.1):
    """Go through the raw data files, and correct some inconsistencies in naming convention, and create
    tabularised formats of interval data too"""

    for path in Path(root).iterdir():
        # Quick test to make sure the current subdirectory is a sequence ID
        try:
            int(path.name)
        except ValueError:
            continue

        logger.info(f"parsing sequence {path}")

        # Rename pir and rgbd living files
        rename_file(root=path, old="pir.csv", new="pir_raw.csv")
        rename_file(root=path, old="video_living_room.csv", new="video_living.csv")
        rename_file(root=path, old="video_hallway.csv", new="video_hall.csv")

        for loc in json.load(open("assets/rgbd_locs.json", "r")):
            rename_file(root=path, old=f"video_{loc}.csv", new=f"rgbd_{loc}.csv")

        for idx in range(3):
            rename_file(root=path, old=f"annotations_{idx}.csv", new=f"activity_{idx}.csv")
            rename_file(root=path, old=f"activity_{idx}.csv", new=f"activity_{idx}_raw.csv")
            rename_file(root=path, old=f"location_{idx}.csv", new=f"location_{idx}_raw.csv")

        # Load the raw sequence
        seq = RawSequence.load_from_path(path)

        # Add the user ID to the metadata
        seq.meta.user_id = participant_lookup[path.name]
        dump_json(obj=seq.meta.dict(), fil=path / "meta.json")

        for idx in range(len(seq.meta.annotators)):
            # Add the label index to the activity / location files
            for fname in ("activity", "location"):
                lookup = dict(
                    activity=activity_name_idx_map,
                    location=location_name_idx_map,
                )[fname]

                # Add the index to the label file to make it easier to map to the required column
                df = pd.read_csv(path / f"{fname}_{idx}_raw.csv")
                if "index" not in df.columns:
                    df.insert(1, "index", [lookup[val] for val in df["name"].values])
                    dump_df(df=df, fil=path / f"{fname}_{idx}_raw.csv")

        # Standardise the RSSI names (e.g. Kitchen_AP -> kitchen)
        seq.rssi.columns = [ap_rssi_name_map.get(col, col) for col in seq.rssi.columns]
        dump_df(df=seq.rssi, fil=path / "rssi.csv")

        # Standardise the names in the PIR files (e.g. S1_K -> kitchen)
        try:
            seq.pir.name = seq.pir.name.apply(pir_name_map.__getitem__)
            dump_df(df=seq.pir, fil=path / "pir_raw.csv")
        except KeyError:
            pass

        # Create a time-series format (rather than interval-defined format) representation for PIR data
        pir_t, pir_ts = tabularise_intervals(
            seqs=seq.pir,
            lookup=pir_name_idx_map,
            start=seq.meta.start,
            end=seq.meta.end,
            delta=delta,
            return_time=True,
        )

        pir = pd.DataFrame(pir_ts, columns=pir_names_sorted)
        pir.insert(0, "t", pir_t)

        dump_df(df=pir, fil=path / "pir.csv")

        # Create the tabular labels for activity and location targets
        for kind in ("activity", "location"):
            if force or not (path / f"{kind}.csv").exists():
                labels, label_values = make_tabular_labels(seq=seq, kind=kind, delta=delta, return_raw=True)
                dump_df(df=labels, fil=path / f"{kind}.csv")

                for di, df in enumerate(label_values):
                    dump_df(df=df, fil=path / f"per_ann_{kind}_{di}.csv")


def create_train_sequences(root: Path, out_root: Path):
    """A helper function that creates output train data. note: this is the same in the `full` and `sliced` contexts"""

    for idx, seq_id in enumerate(train_test_id_split["train"], start=1):
        logger.info(f"Loading {seq_id}")

        seq = ProcessedSequence.load_from_path(root / seq_id, accel="acceleration_corrected_hist")

        seq_dir = out_root / "train" / f"{idx:05d}"
        seq_dir.mkdir(exist_ok=True, parents=True)

        ProcessedSequence.dump(path=seq_dir, obj=seq)


def create_full_sequences(root: Path, out_root: Path):
    """A function that creates the train data, but also the full test sequences in the required files"""

    create_train_sequences(root=root, out_root=out_root)

    for idx, seq_id in enumerate(train_test_id_split["test"], start=len(train_test_id_split["train"]) + 1):
        logger.info(f"Loading {seq_id}")
        seq = ProcessedSequence.load_from_path(root / seq_id, accel="acceleration_corrected_hist")

        seq_dir = out_root / "test" / f"{idx:05d}"
        seq_dir.mkdir(exist_ok=True, parents=True)

        ProcessedSequence.dump(path=seq_dir, obj=seq)


def create_sliced_sequences(root: Path, out_root: Path):
    """A function that creates train data, but also the short sequences of test data that were used in the
    evaluation of the Sphere Challenge"""

    create_train_sequences(root=root, out_root=out_root)

    segs = pd.read_csv("assets/test_index_lookup.csv")

    seqs = {
        seq_id: ProcessedSequence.load_from_path(root / seq_id, accel="acceleration_corrected_hist")
        for seq_id in train_test_id_split["test"]
    }

    for row in segs.itertuples():
        if row.private_index == 19:
            continue

        logger.info(f"Loading {row}")

        seq_dir = out_root / "test" / f"{row.public_index:05d}"
        seq_dir.mkdir(exist_ok=True, parents=True)

        seg = seqs[f"{row.private_index:03d}"].slice_obj(start=row.start, end=row.end)
        ProcessedSequence.dump(path=seq_dir, obj=seg)


def process_data(
    data="data", raw="raw", full="sphere-challenge-complete-2022", sliced="sphere-challenge-2016", force=True
):
    root = Path(f"{data}/{raw}")

    standardise_sequences(root=root, force=force)
    create_full_sequences(root=root, out_root=Path(f"{data}/{full}"))
    create_sliced_sequences(root=root, out_root=Path(f"{data}/{sliced}"))


if __name__ == "__main__":
    process_data()
