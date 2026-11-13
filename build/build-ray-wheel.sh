#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"

configure_java
python="${PYTHON:-python3.11}"
"$python" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 11))' || die "Use CPython 3.11."
export BAZEL_PATH="$build_root/tools/bin/bazel"
[[ -x "$BAZEL_PATH" ]] || die "Run build/bootstrap-bazel.sh first with this BUILD_ROOT."
[[ "$("$BAZEL_PATH" --version)" == "bazel 6.5.0" ]] || die "Expected Bazel 6.5.0."
export CC="${CC:-gcc}" CXX="${CXX:-g++}"
export PATH="$build_root/tools/bin:$PATH"
export PIP_CACHE_DIR="$build_root/cache/pip"

source_dir="$build_root/src/ray"
checkout_pinned https://github.com/ray-project/ray.git ray-2.52.0 \
    9527a555280fb9837ce73dabf01559c20656a456 "$source_dir"
venv="$build_root/ray-venv"
"$python" -m venv "$venv"
venv_python="$venv/bin/python"
"$venv_python" -m pip install 'pip==25.0.1' 'setuptools==78.1.1' 'wheel==0.45.1' 'Cython==3.0.12'

# The composite patch adds both dependency patches and registers them with Bazel.
patch_file="$build_root/tmp/ray-source.patch"
sed "s|/opt/ray-build-venv/bin/python|$venv_python|g" \
    "$repo_root/patches/ray/ray-source-complete.example.patch" > "$patch_file"
# Blank context lines in the embedded dependency diffs intentionally contain a space.
git -C "$source_dir" apply --whitespace=nowarn --check "$patch_file"
git -C "$source_dir" apply --whitespace=nowarn "$patch_file"

cat > "$source_dir/.user.bazelrc" <<EOF
startup --batch
startup --server_javabase=$JAVA_HOME
startup --output_user_root=$build_root/cache/bazel-ray
build --jobs=$build_jobs
build --repository_cache=$build_root/cache/bazel-repository
build --disk_cache=$build_root/cache/bazel-disk
EOF
export BAZEL_ARGS="--java_runtime_version=local_jdk --tool_java_runtime_version=local_jdk"
export RAY_BUILD_CORE=1 RAY_DISABLE_EXTRA_CPP=1 RAY_BUILD_REDIS=0 RAY_INSTALL_JAVA=0 RAY_INSTALL_CPP=0 SKIP_BAZEL_BUILD=0
unset IS_AUTOMATED_BUILD RAY_DEBUG_BUILD SKIP_THIRDPARTY_INSTALL_CONDA_FORGE BAZEL_LIMIT_CPUS

wheel_dir="$build_root/artifacts/wheels"
mkdir -p -- "$wheel_dir"
cd -- "$source_dir/python"
"$venv_python" -m pip wheel --no-deps --no-build-isolation --wheel-dir "$wheel_dir" .

wheel="$wheel_dir/ray-2.52.0-cp311-cp311-linux_riscv64.whl"
"$venv_python" - "$wheel" <<'PY'
import sys
from zipfile import ZipFile

with ZipFile(sys.argv[1]) as archive:
    files = set(archive.namelist())
    required = {
        "ray/_raylet.so",
        "ray/core/src/ray/gcs/gcs_server",
        "ray/core/src/ray/raylet/raylet",
    }
    if missing := required - files:
        raise SystemExit(f"Missing wheel binaries: {sorted(missing)}")
PY
sha256sum "$wheel"
