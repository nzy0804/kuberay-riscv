"""Validate one existing KubeRay head and at least two worker Pods.

Run this driver inside the head Pod. Supply a recent Kubernetes Pod JSON
snapshot selected by this RayCluster's label. This is a functional check on
one physical Kubernetes node, not a cross-machine performance benchmark.
"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import socket
import sys
import time
import traceback


SIZES = (1024, 1024 * 1024, 64 * 1024 * 1024)


def timestamp():
    return datetime.now(timezone(timedelta(hours=8)))


def identity():
    import ray

    return {
        "node_id": ray.get_runtime_context().get_node_id(),
        "pod_name": os.environ.get("POD_NAME", socket.gethostname()),
        "pod_ip": os.environ.get("POD_IP"),
        "pod_uid": os.environ.get("POD_UID"),
        "pid": os.getpid(),
        "ray_version": ray.__version__,
        "python": platform.python_version(),
        "architecture": platform.machine(),
    }


def seed_for(token):
    return hashlib.sha256(token.encode("utf-8")).digest()


def expected_digest(size, token):
    # Compute the expected digest without getting the Ray object onto the head.
    chunk = seed_for(token) * 32768
    digest = hashlib.sha256()
    for offset in range(0, size, len(chunk)):
        digest.update(chunk[: min(len(chunk), size - offset)])
    return digest.hexdigest()


def square(value):
    return {"input": value, "value": value * value, "where": identity()}


def read_object(wrapped_reference, timeout):
    import ray

    # A list prevents top-level ObjectRef auto-dereferencing before this method.
    assert len(wrapped_reference) == 1
    reference = wrapped_reference[0]
    assert isinstance(reference, ray.ObjectRef), type(reference)
    started = time.monotonic_ns()
    payload = ray.get(reference, timeout=timeout)
    acquired = time.monotonic_ns()
    assert isinstance(payload, bytes), type(payload)
    return {
        "where": identity(),
        "object_id": reference.hex(),
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "get_elapsed_ns": acquired - started,
    }


class Counter:
    def __init__(self):
        self.value = 0

    def add(self, amount):
        self.value += amount
        return {"value": self.value, "where": identity()}


class ObjectProducer:
    def __init__(self):
        # The owner actor and its references stay alive throughout all reads.
        self.references = {}

    def create(self, size, token):
        import ray

        seed = seed_for(token)
        payload = seed * (size // len(seed)) + seed[: size % len(seed)]
        reference = ray.put(payload)
        self.references[token] = reference
        # Return only a nested reference and small metadata, never the payload.
        return {
            "reference": [reference],
            "object_id": reference.hex(),
            "size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "where": identity(),
        }

    def retained(self):
        return {"count": len(self.references), "where": identity()}


class ObjectConsumer:
    def read(self, wrapped_reference, timeout):
        return read_object(wrapped_reference, timeout)


def node_record(node):
    return {
        "node_id": node["NodeID"],
        "ip": node["NodeManagerAddress"],
        "resources": node["Resources"],
        "is_head": node["Resources"].get("node:__internal_head__", 0) > 0,
    }


def map_pods(nodes, manifest):
    pods_by_ip = {
        pod["status"]["podIP"]: pod
        for pod in manifest["items"]
        if pod.get("status", {}).get("podIP")
    }
    mapping = {}
    for node in nodes:
        pod = pods_by_ip[node["ip"]]
        assert pod["status"]["phase"] == "Running", pod["metadata"]["name"]
        assert any(
            condition["type"] == "Ready" and condition["status"] == "True"
            for condition in pod["status"].get("conditions", [])
        ), pod["metadata"]["name"]
        expected_role = "head" if node["is_head"] else "worker"
        assert pod["metadata"]["labels"]["ray.io/node-type"] == expected_role
        mapping[node["node_id"]] = {
            **node,
            "pod_name": pod["metadata"]["name"],
            "pod_uid": pod["metadata"]["uid"],
            "namespace": pod["metadata"]["namespace"],
            "cluster": pod["metadata"]["labels"]["ray.io/cluster"],
            "kubernetes_node": pod["spec"]["nodeName"],
        }
    assert len({item["ip"] for item in mapping.values()}) == len(nodes)
    assert len({item["pod_uid"] for item in mapping.values()}) == len(nodes)
    for key in ("kubernetes_node", "namespace", "cluster"):
        assert len({item[key] for item in mapping.values()}) == 1, key
    return mapping


def check_identity(actual, target, mapping):
    assert actual["node_id"] == target, (actual, target)
    expected = mapping[target]
    assert actual["pod_name"] == expected["pod_name"], (actual, expected)
    if actual["pod_ip"] is not None:
        assert actual["pod_ip"] == expected["ip"], (actual, expected)
    if actual["pod_uid"] is not None:
        assert actual["pod_uid"] == expected["pod_uid"], (actual, expected)
    assert actual["ray_version"] == "2.52.0", actual
    assert actual["python"].split(".")[:2] == ["3", "11"], actual
    assert actual["architecture"] == "riscv64", actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pods-json", type=Path, required=True)
    parser.add_argument("--expected-workers", type=int, default=2)
    parser.add_argument("--registration-timeout", type=float, default=120)
    parser.add_argument("--rpc-timeout", type=float, default=60)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(os.environ.get("RAY_TEST_RESULTS_DIR", "/tmp/ray-kuberay-results")))
    args = parser.parse_args()
    if args.expected_workers < 2 or min(args.registration_timeout, args.rpc_timeout) <= 0:
        parser.error("At least two workers and positive timeouts are required")
    run_id = timestamp().strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}"
    output = args.output_dir / run_id
    output.mkdir(parents=True)
    result_path = output / "result.json"
    report = {
        "status": "RUNNING", "started": timestamp().isoformat(), "run_id": run_id,
        "scope": "single_physical_host_multiple_ray_pods_functional",
        "timing_usage": "diagnostic_only_not_a_performance_benchmark",
        "pods_snapshot": str(args.pods_json), "checks": {},
    }

    def save():
        temporary = result_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(result_path)

    def step(name):
        report["phase"] = name
        save()
        print("STEP=" + name, flush=True)

    def terminate(signum, _frame):
        raise SystemExit(f"Received signal {signum}")

    ray = None
    actors = []
    retained_references = []
    initial_node_ids = set()
    success = False
    signal.signal(signal.SIGTERM, terminate)
    print("Results:", result_path, flush=True)
    try:
        step("connect")
        if not __debug__:
            raise RuntimeError("Run without Python -O so all assertions remain enabled")
        import ray
        from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy

        assert ray.__version__ == "2.52.0", ray.__version__
        assert sys.version_info[:2] == (3, 11), sys.version
        ray.init(address="auto", namespace="kuberay-validation-" + run_id)
        signal.signal(signal.SIGTERM, terminate)
        report["driver"] = identity()

        step("registration")
        expected_nodes = 1 + args.expected_workers
        deadline = time.monotonic() + args.registration_timeout
        while True:
            alive = [node_record(node) for node in ray.nodes() if node["Alive"]]
            if len(alive) == expected_nodes:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError(f"Expected {expected_nodes} Alive nodes, found {alive}")
            time.sleep(1)
        mapping = map_pods(alive, json.loads(args.pods_json.read_text(encoding="utf-8")))
        heads = [node for node in alive if node["is_head"]]
        workers = sorted((node for node in alive if not node["is_head"]), key=lambda n: n["ip"])
        assert len(heads) == 1 and len(workers) == args.expected_workers, alive
        check_identity(report["driver"], heads[0]["node_id"], mapping)
        assert all(node["resources"].get("CPU", 0) >= 2 for node in workers), workers
        initial_node_ids = set(mapping)
        report["checks"]["registration"] = {"nodes": mapping, "resources": ray.cluster_resources()}
        print("PASS registration:", {key: value["pod_name"] for key, value in mapping.items()}, flush=True)

        def strategy(node_id):
            return NodeAffinitySchedulingStrategy(node_id=node_id, soft=False)

        step("tasks")
        remote_square = ray.remote(num_cpus=1, max_retries=0)(square)
        pending = []
        targets = []
        for node in workers:
            for value in range(4):
                targets.append((node["node_id"], value))
                pending.append(remote_square.options(scheduling_strategy=strategy(node["node_id"])).remote(value))
        results = ray.get(pending, timeout=args.rpc_timeout)
        for result, (target, value) in zip(results, targets):
            assert result["input"] == value and result["value"] == value * value, result
            check_identity(result["where"], target, mapping)
        report["checks"]["tasks"] = results
        print("PASS tasks on each worker", flush=True)

        step("actors")
        counter_type = ray.remote(num_cpus=1, max_restarts=0)(Counter)
        counter_results = []
        for node in workers:
            actor = counter_type.options(scheduling_strategy=strategy(node["node_id"])).remote()
            actors.append(actor)
            updates = ray.get([actor.add.remote(1), actor.add.remote(2)], timeout=args.rpc_timeout)
            assert [item["value"] for item in updates] == [1, 3], updates
            for item in updates:
                check_identity(item["where"], node["node_id"], mapping)
            counter_results.append(updates)
        report["checks"]["actors"] = counter_results
        # Free the test counters' CPUs before producer/consumer actors and tasks.
        for actor in actors:
            ray.kill(actor, no_restart=True)
        actors.clear()
        print("PASS stateful actor on each worker", flush=True)

        step("objects")
        source_id, destination_id = workers[0]["node_id"], workers[1]["node_id"]
        assert source_id != destination_id
        producer = ray.remote(num_cpus=1, max_restarts=0)(ObjectProducer).options(
            scheduling_strategy=strategy(source_id)).remote()
        consumer = ray.remote(num_cpus=1, max_restarts=0)(ObjectConsumer).options(
            scheduling_strategy=strategy(destination_id)).remote()
        actors.extend((producer, consumer))
        remote_read = ray.remote(num_cpus=1, max_retries=0)(read_object).options(
            scheduling_strategy=strategy(destination_id))
        object_results = []
        seen_ids = set()
        for size in SIZES:
            for receiver in ("task", "actor"):
                # Separate fresh objects keep each receiver's first read distinct.
                token = f"{run_id}:{size}:{receiver}"
                expected_sha = expected_digest(size, token)
                created = ray.get(producer.create.remote(size, token), timeout=args.rpc_timeout)
                check_identity(created["where"], source_id, mapping)
                wrapped = created["reference"]
                assert len(wrapped) == 1 and isinstance(wrapped[0], ray.ObjectRef)
                assert created["object_id"] == wrapped[0].hex()
                assert created["object_id"] not in seen_ids
                seen_ids.add(created["object_id"])
                retained_references.extend(wrapped)
                assert created["size"] == size and created["sha256"] == expected_sha
                readings = []
                for read_kind in ("first", "repeat"):
                    if receiver == "task":
                        pending_read = remote_read.remote(wrapped, args.rpc_timeout)
                    else:
                        pending_read = consumer.read.remote(wrapped, args.rpc_timeout)
                    received = ray.get(pending_read, timeout=args.rpc_timeout)
                    check_identity(received["where"], destination_id, mapping)
                    assert received["object_id"] == created["object_id"]
                    assert received["size"] == size and received["sha256"] == expected_sha
                    readings.append({"read_kind": read_kind, **received})
                object_results.append({
                    "receiver": receiver, "size": size, "object_id": created["object_id"],
                    "sha256": expected_sha, "producer": created["where"], "readings": readings,
                })
                report["checks"]["objects"] = object_results
                save()
                print(f"PASS {size} bytes: {receiver}, first/repeat, {source_id} -> {destination_id}", flush=True)
        owner = ray.get(producer.retained.remote(), timeout=args.rpc_timeout)
        check_identity(owner["where"], source_id, mapping)
        assert owner["count"] == len(SIZES) * 2 == len(retained_references)
        report["checks"]["object_owner"] = owner
        success = True
    except BaseException:
        report["failed_phase"] = report.get("phase")
        report["error"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        step("cleanup_and_disconnect")
        if ray is not None and ray.is_initialized():
            cleanup_errors = []
            for actor in actors:
                try:
                    ray.kill(actor, no_restart=True)
                except BaseException:
                    cleanup_errors.append(traceback.format_exc())
            try:
                remaining = {node["NodeID"] for node in ray.nodes() if node["Alive"]}
                if initial_node_ids:
                    assert remaining == initial_node_ids, (remaining, initial_node_ids)
                    report["checks"]["cluster_preserved"] = sorted(remaining)
                # Disconnect this driver; the existing KubeRay services stay alive.
                ray.shutdown()
                assert not ray.is_initialized()
                report["checks"]["disconnect"] = "PASS"
            except BaseException:
                cleanup_errors.append(traceback.format_exc())
            if cleanup_errors:
                success = False
                report["cleanup_errors"] = cleanup_errors
        report["status"] = "PASS" if success else "FAIL"
        report["finished"] = timestamp().isoformat()
        save()
        print("KubeRay multi-node functional check:", report["status"], flush=True)
        print("Results:", result_path, flush=True)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

