"""
Kalman Filter for multi-object bounding box tracking.
Implements an 8-dimensional state space kinematic model:
[cx, cy, a, h, vx, vy, va, vh]^T
where (cx, cy) is bounding box center, a is aspect ratio (w/h),
h is height, and (vx, vy, va, vh) are their respective velocities.
"""

from typing import Tuple
import numpy as np


class KalmanFilter:
    """
    A simple Kalman filter for tracking bounding boxes in image space.
    The 8-dimensional state vector is:
        x = [cx, cy, a, h, vx, vy, va, vh]
    The 4-dimensional measurement vector is:
        z = [cx, cy, a, h]
    """

    def __init__(self):
        ndim, dt = 4, 1.0

        # State transition matrix F (constant velocity model)
        self._motion_mat = np.eye(2 * ndim, 2 * ndim)
        for i in range(ndim):
            self._motion_mat[i, ndim + i] = dt

        # Measurement projection matrix H
        self._update_mat = np.eye(ndim, 2 * ndim)

        # Motion and observation uncertainty weights
        self._std_weight_position = 1.0 / 20
        self._std_weight_velocity = 1.0 / 160

    def initiate(self, measurement: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create track from unassociated measurement.
        Parameters:
            measurement : ndarray of shape (4,) [cx, cy, a, h]
        Returns:
            mean : ndarray of shape (8,)
            covariance : ndarray of shape (8, 8)
        """
        mean_pos = measurement
        mean_vel = np.zeros_like(mean_pos)
        mean = np.r_[mean_pos, mean_vel]

        std = [
            2 * self._std_weight_position * measurement[3],
            2 * self._std_weight_position * measurement[3],
            1e-2,
            2 * self._std_weight_position * measurement[3],
            10 * self._std_weight_velocity * measurement[3],
            10 * self._std_weight_velocity * measurement[3],
            1e-5,
            10 * self._std_weight_velocity * measurement[3],
        ]
        covariance = np.diag(np.square(std))
        return mean, covariance

    def predict(self, mean: np.ndarray, covariance: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Run Kalman filter prediction step.
        Parameters:
            mean : ndarray (8,)
            covariance : ndarray (8, 8)
        Returns:
            predicted_mean : ndarray (8,)
            predicted_covariance : ndarray (8, 8)
        """
        std_pos = [
            self._std_weight_position * mean[3],
            self._std_weight_position * mean[3],
            1e-2,
            self._std_weight_position * mean[3],
        ]
        std_vel = [
            self._std_weight_velocity * mean[3],
            self._std_weight_velocity * mean[3],
            1e-5,
            self._std_weight_velocity * mean[3],
        ]
        motion_cov = np.diag(np.square(np.r_[std_pos, std_vel]))

        predicted_mean = np.dot(self._motion_mat, mean)
        predicted_covariance = (
            np.linalg.multi_dot((self._motion_mat, covariance, self._motion_mat.T))
            + motion_cov
        )
        return predicted_mean, predicted_covariance

    def project(self, mean: np.ndarray, covariance: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Project state distribution to measurement space.
        Parameters:
            mean : ndarray (8,)
            covariance : ndarray (8, 8)
        Returns:
            projected_mean : ndarray (4,)
            projected_covariance : ndarray (4, 4)
        """
        std = [
            self._std_weight_position * mean[3],
            self._std_weight_position * mean[3],
            1e-1,
            self._std_weight_position * mean[3],
        ]
        innovation_cov = np.diag(np.square(std))

        projected_mean = np.dot(self._update_mat, mean)
        projected_covariance = (
            np.linalg.multi_dot((self._update_mat, covariance, self._update_mat.T))
            + innovation_cov
        )
        return projected_mean, projected_covariance

    def update(
        self, mean: np.ndarray, covariance: np.ndarray, measurement: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Run Kalman filter update step with new measurement.
        Parameters:
            mean : ndarray (8,)
            covariance : ndarray (8, 8)
            measurement : ndarray (4,)
        Returns:
            updated_mean : ndarray (8,)
            updated_covariance : ndarray (8, 8)
        """
        projected_mean, projected_cov = self.project(mean, covariance)

        # Kalman gain: K = P * H^T * S^-1
        kalman_gain = np.linalg.multi_dot(
            (covariance, self._update_mat.T, np.linalg.inv(projected_cov))
        )
        innovation = measurement - projected_mean

        new_mean = mean + np.dot(kalman_gain, innovation)
        new_covariance = covariance - np.linalg.multi_dot(
            (kalman_gain, projected_cov, kalman_gain.T)
        )
        return new_mean, new_covariance
