# TCP Congestion Control Algorithms

This repository contains a simulation of TCP congestion control algorithms implemented in Python. A Docker container is used to simulate a receiver with added latency, providing a controlled environment for testing and observing the behavior of different congestion control mechanisms.

## Implemented Algorithms

The following TCP congestion control algorithms are implemented:
- **TCP Reno**
- **TCP Tahoe**
- **Stop and Wait**
- **Fixed Sliding Window**

## Features

- **Dockerized Environment**: Ensures consistency and isolates the receiver, simulating network latency.
- **Custom Implementations**: Python-based implementation of congestion control algorithms.
- **Simulation**: Observe and analyze how each algorithm handles congestion and adapts to latency.
