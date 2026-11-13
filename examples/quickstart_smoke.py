"""Run inside the Quick Start head Pod and verify that a worker executes a task."""

import platform
import time

import ray


@ray.remote(num_cpus=1, max_retries=0)
def square(value):
    return value * value, ray.get_runtime_context().get_node_id(), platform.machine()


def main():
    if platform.machine() != "riscv64" or ray.__version__ != "2.52.0":
        raise RuntimeError(f"Expected Ray 2.52.0 on riscv64, got {ray.__version__} on {platform.machine()}")

    ray.init(address="auto")
    try:
        head = ray.get_runtime_context().get_node_id()
        deadline = time.monotonic() + 60
        while True:
            workers = {
                node["NodeID"] for node in ray.nodes()
                if node["Alive"] and node["NodeID"] != head and node["Resources"].get("CPU", 0) >= 1
            }
            if workers:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("No live Ray worker with CPU resources after 60 seconds")
            time.sleep(1)

        result, worker, arch = ray.get(square.remote(7), timeout=60)
        if result != 49 or worker not in workers or arch != "riscv64":
            raise RuntimeError(f"Unexpected task result: value={result}, node={worker}, arch={arch}")
        print("PASS: Ray 2.52.0 executed 7^2 = 49 on a riscv64 worker")
    finally:
        ray.shutdown()


if __name__ == "__main__":
    main()
