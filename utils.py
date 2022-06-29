import os
import numpy as np
from filelock import FileLock
import itertools
import functools

from copy import deepcopy

try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

# BASE_URL = "https://file.lzhu.me/projects/ofa_infos"


def download_url(url, model_dir='~/.torch/', overwrite=False):
    # TODO: add md5 hash check
    # TODO: add progress bar
    filename = url.split('/')[-1]
    model_dir = os.path.expanduser(model_dir)

    os.makedirs(model_dir, exist_ok=True)
    filepath = os.path.join(model_dir, filename)

    if os.path.exists(filepath) and not overwrite:
        # file already exists and do not overwrite
        return filepath
    else:
        with FileLock(os.path.join(model_dir, "download.lock")) as lock:
            print('Downloading: "{}" to {}\n'.format(url, filepath))
            urlretrieve(url, filepath)
            return filepath
            # try:
            #     urlretrieve(url, filepath)
            #     return filepath
            # except Exception as e:
            #     # If fail, then ensure the lock is removed so download can be executed next time.
            #     print("Failed to download from url %s" % url + "\n" + str(e) + "\n")
            #     return None


class ArchTool:
    def __init__(self, choices_ks=(3, 5, 7), choices_ex=(3, 4, 6), choices_d=(2, 3, 4),
                 max_ks=20, max_ex=20, max_d=5):
        self.choices_ks = choices_ks
        self.choices_ex = choices_ex
        self.choices_d = choices_d
        self.max_ks = max_ks
        self.max_ex = max_ex
        self.max_d = max_d

    def random(self, serialize=False) -> (list, list, list):
        return ArchTool.simple_random(self.choices_ks, self.choices_ex, self.choices_d,
                                      self.max_ks, self.max_ex, self.max_d, serialize)

    @staticmethod
    def simple_random(ks_choices=(3, 5, 7), ex_choices=(3, 4, 6), d_choices=(2, 3, 4),
                      ks_max=20, ex_max=20, d_max=5, serialize=False):
        assert isinstance(ks_choices, (list, tuple))
        assert isinstance(ex_choices, (list, tuple))
        assert isinstance(d_choices, (list, tuple))
        ks_list = [int(np.random.choice(ks_choices)) for _ in range(ks_max)]
        ex_list = [int(np.random.choice(ex_choices)) for _ in range(ex_max)]
        d_list = [int(np.random.choice(d_choices)) for _ in range(d_max)]

        ks_list, ex_list, d_list = ArchTool.formalize(ks_list, ex_list, d_list)

        if not serialize:
            return ks_list, ex_list, d_list
        else:
            return ArchTool.serialize(ks_list, ex_list, d_list)

    def iterate_space(self, serialize=False) -> (list, list, list):
        for arch in ArchTool.simple_iterate_space(
                self.choices_ks, self.choices_ex, self.choices_d,
                self.max_ks, self.max_ex, self.max_d, serialize
        ):
            yield arch

    @staticmethod
    def simple_iterate_space(ks_choices=(3, 5, 7), ex_choices=(3, 4, 6), d_choices=(2, 3, 4),
                             ks_max=20, ex_max=20, d_max=5, serialize=False):
        assert isinstance(ks_choices, (list, tuple))
        assert isinstance(ex_choices, (list, tuple))
        assert isinstance(d_choices, (list, tuple))

        ks_candidate = [ks_choices for _ in range(ks_max)]
        ex_candidate = [ex_choices for _ in range(ex_max)]
        d_candidate = [d_choices for _ in range(d_max)]

        for config in itertools.product(*(ks_candidate + ex_candidate + d_candidate)):
            ks_list = config[:ks_max]
            ex_list = config[ks_max:ks_max + ex_max]
            d_list = config[ks_max + ex_max:]
            ks_list, ex_list, d_list = ArchTool.formalize(ks_list, ex_list, d_list)

            if not serialize:
                yield ks_list, ex_list, d_list
            else:
                yield ArchTool.serialize(ks_list, ex_list, d_list)

    @staticmethod
    def formalize(_ks_list: list, _ex_list: list, _d_list: list) -> (list, list, list):
        ks_list, ex_list, d_list = list(_ks_list), list(_ex_list), list(_d_list)
        # ks and ex between (d, max_d) is meaningless. Fill 0 to avoid redundancy
        start = 0
        end = 4
        for d in d_list:
            for j in range(start + d, end):
                ks_list[j] = 0
                ex_list[j] = 0
            start += 4
            end += 4
        return ks_list, ex_list, d_list

    @staticmethod
    def serialize(ks_list: list, ex_list: list, d_list: list) -> str:
        assert len(ks_list) == 20, "Kernel size list can only contain 20 numbers."
        assert len(ex_list) == 20, "Expansion ratio list can only contain 20 numbers."
        assert len(d_list) == 5, "Depth list can only contain 5 numbers."
        ks_list, ex_list, d_list = ArchTool.formalize(ks_list, ex_list, d_list)

        ks_str = "%s:%s" % ("ks", ",".join([str(_) for _ in ks_list]))
        ex_str = "%s:%s" % ("ex", ",".join([str(_) for _ in ex_list]))
        d_str = "%s:%s" % ("d", ",".join([str(_) for _ in d_list]))
        return "-".join([ks_str, ex_str, d_str])

    @staticmethod
    def deserialize(cfg_str: str) -> (list, list, list):
        ks_str, ex_str, d_str = cfg_str.strip().split("-")

        ks_list = [int(_) for _ in ks_str.split(":")[-1].split(",")]
        ex_list = [int(_) for _ in ex_str.split(":")[-1].split(",")]
        d_list = [int(_) for _ in d_str.split(":")[-1].split(",")]

        assert len(ks_list) == 20, "Kernel size list can only contain 20 numbers."
        assert len(ex_list) == 20, "Expansion ratio list can only contain 20 numbers."
        assert len(d_list) == 5, "Depth list can only contain 5 numbers."

        return ks_list, ex_list, d_list
