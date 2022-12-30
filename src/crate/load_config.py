from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

from .particle_source import ParticleSource
from .rigid_body import MotoredRigidBody, FixedRigidBody, RigidBody

BODY_TYPE_TO_CLASS = {"motored": MotoredRigidBody, "fixed": FixedRigidBody, "free": RigidBody}


@dataclass
class WorldConfig:
    rigid_bodies: list[RigidBody]
    particle_sources: list[ParticleSource]
    coefficients: dict


@dataclass
class PlaybackConfig:
    save_recording: bool
    ticks_to_record: bool
    recording_output_dir_path: Path
    screen_x: int
    screen_y: int


@dataclass
class Config:
    world_config: WorldConfig
    playback_config: PlaybackConfig


def load_config(config_file_path: Path) -> Config:
    with open(config_file_path, "r") as f:
        raw_config = yaml.safe_load(f)
    raw_world_config = raw_config["world"]
    world_config = WorldConfig(
        rigid_bodies=build_rigid_bodies(raw_world_config.get("rigid_bodies", [])),
        particle_sources=build_particle_sources(raw_world_config.get("particle_sources")),
        coefficients=raw_world_config.get("coefficients"),
    )
    playback_config = raw_config["playback"]
    playback_config = PlaybackConfig(
        save_recording=playback_config["save_recording"],
        ticks_to_record=playback_config["ticks_to_record"],
        recording_output_dir_path=Path(playback_config["recording_output_dir_path"]),
        screen_x=playback_config["screen_x"],
        screen_y=playback_config["screen_y"]
    )
    return Config(world_config=world_config, playback_config=playback_config)


def build_particle_sources(particle_source_configs):
    return [ParticleSource(**config) for config in particle_source_configs]


def build_rigid_bodies(body_configs: list) -> list[RigidBody]:
    rigid_bodies = []
    for body_config in body_configs:
        body_type, kwargs = next(iter(body_config.items()))
        body_class = BODY_TYPE_TO_CLASS[body_type]
        if "segments" in kwargs:
            kwargs["segments"] = np.array(kwargs["segments"])
        if "velocity" in kwargs:
            kwargs["velocity"] = np.array(kwargs["velocity"])
        if "velocity_func" in kwargs:
            kwargs["velocity_func"] = eval(kwargs["velocity_func"])
        if "angular_velocity_func" in kwargs:
            kwargs["angular_velocity_func"] = eval(kwargs["angular_velocity_func"])
        rigid_body = body_class(**kwargs)
        rigid_body.place_in_world()
        rigid_bodies.append(rigid_body)

    return rigid_bodies
