import hydra
from omegaconf import DictConfig

from experiment_project.text_to_kg.process import text_to_kg
from experiment_project.utils.config.hydra import resolve_hydra_config


@hydra.main(version_base='1.3', config_path=f"../configs",
            config_name="text_to_kg.yaml")
def run_text_to_kg(cfg: DictConfig):
    cfg = resolve_hydra_config(cfg=cfg)
    text_to_kg_cfg = {}
    for k, v in cfg.items():
        text_to_kg_cfg.update(v)
    print(text_to_kg_cfg)

    text_to_kg(**text_to_kg_cfg)

if __name__ == "__main__":
    run_text_to_kg()