import json, os, os.path as osp
import pickle

import numpy as np
import matplotlib.pyplot as plt

from graphviz import Digraph

k3c = "#%02x%02x%02x" % (0, 118, 197)  # "blue"
k5c = "#%02x%02x%02x" % (247, 173, 40)  # yellow
k7c = "#%02x%02x%02x" % (153, 20, 0)  # "red"

c_lut = {
    3: k3c,
    5: k5c,
    7: k7c
}

w_lut = {
    3: 3,
    4: 3.5,
    6: 4.5
}


def draw_arch(ks_list, ex_list, out_name="viz/temp", info=None):
    ddot = Digraph(comment='The visualization of Mojito Architecture Search', format='png',
                   # graph_attr={"size": "60,20"},
                   node_attr={"fontsize": "32", "height": "0.8"}
                   )

    model_name = "mojito"
    with ddot.subgraph(name=model_name) as dot:
        prev = None
        for idx in range(20):

            ks = ks_list[idx]
            ex = ex_list[idx]

            if ks == 0 and ex == 0:
                # print("Skipped")
                continue
            else:
                pass
                # print(w_lut[ex])

            new_name = f"MBConv{ex}-{ks}x{ks}"
            dot.node("%s-%s" % (model_name, idx), new_name, fontcolor="white", \
                     style="rounded,filled", shape="record", color=c_lut[ks], width=str(w_lut[ex]))
            if prev is not None:
                dot.edge("%s-%s" % (model_name, prev), "%s-%s" % (model_name, idx))
            prev = idx
    if info is not None:
        res = []
        for k, v in info.items():
            res.append("%s: %.2f" % (k, v))
        result = " ".join(res)
        ddot.attr(label=f'<<FONT POINT-SIZE="32">{result}</FONT>>' , labelloc="top")

    os.makedirs(osp.dirname(out_name), exist_ok=True)
    ddot.render(out_name)
    print(f"The arch is visualized to {out_name}")

if __name__ == '__main__':
    from utils import ArchTool

    arch_str = "ks:5,7,7,3,5,7,0,0,7,5,5,0,5,5,0,0,5,7,5,7-ex:4,6,6,4,4,3,0,0,3,6,3,0,4,6,0,0,6,6,6,3-d:4,2,3,2,4"
    ks_list, ex_list, d_list = ArchTool.deserialize(arch_str)
    draw_arch(ks_list, ex_list)
