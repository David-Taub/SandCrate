from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pygame
from nptyping import NDArray

from .utils.geometry_utils import rotate_vectors_clockwise_90_deg
from .utils.types import Points, Velocities

Segment = tuple[float, float]


# Position = Union[tuple[float, float], list[float, float], NDArray[float]]


@dataclass
class RigidBody:
    segments: NDArray  # segments x dots(2) x dims(2)
    name: str = ""
    center_velocity: NDArray = np.array([0.0, 0.0])
    angular_clockwise_velocity: float = 0.00  # assumed small. if not, we should use the sine on this value*
    scale: pygame.Vector2 = field(default_factory=lambda: [1.0, 1.0])
    position: pygame.Vector2 = field(default_factory=lambda: [0.0, 0.0])

    def calc_body_points_velocities(self, body_points: Points) -> Velocities:
        # N x 2
        points_central_position = body_points - self.position
        # N x 2
        points_tangential_direction = rotate_vectors_clockwise_90_deg(points_central_position)
        # N x 2
        return self.center_velocity[None] + points_tangential_direction * self.angular_clockwise_velocity

    def place_in_world(self):
        self.segments *= np.array(self.scale)[None]
        self.segments += np.array(self.position)[None]

    def apply_velocity(self, dt: float) -> None:
        new_segments = self.segments.copy()
        new_segments[:, 0, :] += self.calc_body_points_velocities(self.segments[:, 0, :]) * dt
        new_segments[:, 1, :] += self.calc_body_points_velocities(self.segments[:, 1, :]) * dt
        self.segments = new_segments

    def __len__(self) -> int:
        return len(self.segments)


@dataclass
class FixedRigidBody(RigidBody):
    def apply_velocity(self, dt: float) -> None:
        ...


@dataclass
class MotoredRigidBody(RigidBody):
    velocity_func: Callable[[float], NDArray] = lambda t: np.array([0.0, 0.0])
    angular_velocity_func: Callable[[float], float] = lambda t: 0
    time_from_start: float = 0.0

    def apply_velocity(self, dt: float) -> None:
        self.time_from_start += dt
        self.center_velocity = self.velocity_func(self.time_from_start)  # noqa
        self.angular_clockwise_velocity = self.angular_velocity_func(self.time_from_start)  # noqa
        super(MotoredRigidBody, self).apply_velocity(dt)
