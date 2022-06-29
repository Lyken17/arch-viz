# Mojito: A General Purpose Hardware-Aware NAS Dataset

To setup, first install necessary dependencies

`pip install -r requirements.txt`

Below is an overview of Mojito's APIs

```python
from mojito import Mojito, MBV3_10 

mjt = Mojito(MBV3_10) 
# it means mbv3 design space width 1.0 with image size 224

# obtain a random arch from design space
arch = mjt.random_from_design_space()
# arch: ks:5,3,0,0,7,5,3,0,7,5,7,3,7,5,7,7,3,5,7,0-ex:4,3,0,0,6,6,3,0,6,6,4,3,6,3,6,3,4,3,3,0-d:2,3,4,4,3"

# query top-1 accuracy
mjt.query_info_by_arch(arch, info="accuracy") # 74.56

# query CPU latency (default in ms)
mjt.query_info_by_arch(arch, info="cpu-latency") # 18.17

# query GPU latency
mjt.query_info_by_arch(arch, info="gpu-latency") # 26.44


# query multiple inforamtion at once (joint optimization)
mjt.query_info_by_arch(arch, info=("acc", "cpu-latency", "gpu-latency")) 
'''
{
    "acc": 74.56,
    "cpu-latency": 331.6,
    "gpu-latency": 56.3
}
'''

# iterate through all archs
for arch in mjt.get_all_archs():
    print(arch, mjt.query_info_by_arch(arch, info="acc"))

# filter archs with certain conditions
for arch in mjt.get_all_archs(pattern="ks:([0|3|5],?)*-ex:([\d],?)*-d:([\d],?)*"):
    # the string filter uses regex grammar
    # above contion means only consider archs with kernel size 3 and 5
    print(arch)
```


## Example: Searching with Mojito

```python
# We first define the search space 
mjt = Mojito(space=MBV3_10)

# Then, define hyper-parameters for search algorithm
target_latency = 30
latency_regularization = 2

# One single round search with Mojito will look like 
def objective(trial):
    toInt = lambda l: [int(_) for _ in l]

    # the kernel sizes for MJT nets
    ks_list = [trial.suggest_categorical(f"ks_{i}", [3, 5, 7]) for i in range(20)]

    # the expansion ratios for MJT nets
    ex_list = [trial.suggest_categorical(f"ex_{i}", [3, 4, 6]) for i in range(20)]

    # the number of layers per stage for MJT nets
    d_list = [trial.suggest_categorical(f"d_{i}", [2, 3, 4]) for i in range(5)]

    # serialize the arch params into a string
    ks_list, ex_list, d_list = ArchTool.formalize(toInt(ks_list), toInt(ex_list), toInt(d_list))
    arch_str = ArchTool.serialize(ks_list, ex_list, d_list)

    # query the accuracy and latency
    info = mjt.query_info_by_arch(arch_str, info=("acc", "cpu-latency"))
    
    return info["acc"] * ((info["cpu-latency"] / target_latency) ** latency_regularization)
    
    
# Then we can search hardware-aware nas (specialized for CPU) with optuna
study = optuna.create_study(study_name="Optuna Alternative", direction="maximize")
study.optimize(objective, n_trials=50000)

# We also provide a tool to visualize the architecture
ks_list, ex_list, d_list = parse_optuna_params(study.best_params)
draw_arch(ks_list, ex_list) # results are saved to logs/ folder by default.
```

The complete example can be found in [search_opt.py](search_opt.py). 
With mojito, a good architecture for CPU deployment can be found in few minutes and less than 80 lines!

<p align="center">
  <img src="viz/cpu.png" width="50%"/>
</p>
