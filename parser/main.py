import logging
import os
import zipfile
from os import walk

import click as click
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

from feature_extractor import FeatureExtractor
from features.board import Board
from features.combinations import Combination
from features.features import FeaturesPack
from parser import Parser
import tempfile

log = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


def extract_data(input_dir: str, output_dir: str):
    log.info("Start extracting data")
    for (dirpath, dirnames, filenames) in walk(input_dir):
        for filename in tqdm(filenames):
            try:
                with zipfile.ZipFile(os.path.join(input_dir, filename), 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(output_dir, filename.strip('.zip')))
            except Exception as e:
                log.debug(e)


def load_nicknames(path):
    with open(path) as fin:
        return [line.strip() for line in fin]


def parse_file(fe: FeatureExtractor, fpath, datasets_path: str, filename: str, dir: str):
    features = []
    parser = Parser()
    with open(fpath) as f:
        try:
            lines = [x.strip() for x in filter(lambda x: x != '\n', list(f))]
            parser.add_lines(dir, lines)
        except:
            pass
    for hand_id in parser.hands:
        features.extend(fe.extract_features(parser.hands[hand_id][0]))
    if features:
        if filename.endswith('.txt'):
            filename = filename[:-4]
        pd.DataFrame(features).to_csv(os.path.join(datasets_path, dir + filename + '.csv'), index=False,
                                      header=FeaturesPack.features_names() +
                                             Board.features_names() +
                                             Combination.features_names())


def parse_files(fe: FeatureExtractor, path: str, datasets_path: str):
    all_files = []
    for (dirpath, dirnames, filenames) in walk(path):
        for directory in dirnames:
            filenames = os.listdir(os.path.join(path, directory))
            for filename in filenames:
                all_files.append((os.path.join(path, directory, filename), filename, directory))
    log.info(f"Found {len(all_files)} files")
    Parallel(n_jobs=-1, verbose=10)(delayed(parse_file)(fe, fpath, datasets_path, filename, directory)
                                    for fpath, filename, directory in all_files)


def parse_directory_impl(directory, datasets_path, nicknames_path):
    with tempfile.TemporaryDirectory() as output_dir:
        extract_data(directory, output_dir)
        nicknames = load_nicknames(nicknames_path)
        log.debug(f"Loaded follow players: {nicknames}")
        fe = FeatureExtractor(nicknames)
        parse_files(fe, output_dir, datasets_path)


@click.command()
@click.option('--input_dir', type=click.Path(), help='Path to directory with zip arhives')
@click.option('--datasets_path', type=click.Path(), help='Path to result dataset')
@click.option('--nicknames_path', type=click.Path(), help='Path to nicknames dataset')
def parse_directory(input_dir, datasets_path, nicknames_path):
    setup_logging()
    for dirname in os.listdir(input_dir):
        path = os.path.join(input_dir, dirname)
        if os.path.isdir(path):
            parse_directory_impl(path, datasets_path, nicknames_path)


if __name__ == '__main__':
    parse_directory()
