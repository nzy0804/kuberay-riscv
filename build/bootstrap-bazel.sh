#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"

configure_java
export CC="${CC:-gcc}" CXX="${CXX:-g++}"
export EMBED_LABEL=6.5.0
export BAZEL_WRKDIR="$build_root/cache/bazel-bootstrap"
export BAZEL_DIR_STARTUP_OPTIONS="--output_user_root=$BAZEL_WRKDIR/user_root"
export EXTRA_BAZEL_ARGS="--tool_java_runtime_version=local_jdk --java_runtime_version=local_jdk --jobs=$build_jobs"
mkdir -p -- "$BAZEL_WRKDIR"

archive="$build_root/downloads/bazel-6.5.0-dist.zip"
download_verified https://github.com/bazelbuild/bazel/releases/download/6.5.0/bazel-6.5.0-dist.zip \
    "$archive" fc89da919415289f29e4ff18a5e01270ece9a6fe83cb60967218bac4a3bb3ed2
source_dir="$build_root/src/bazel-6.5.0"
mkdir -- "$source_dir"
unzip -q "$archive" -d "$source_dir"
cd -- "$source_dir"
bash ./compile.sh

output="$build_root/tools/bin/bazel"
install -m 755 output/bazel "$output"
[[ "$("$output" --version)" == "bazel 6.5.0" ]] || die "Unexpected Bazel version."
printf 'Bazel: %s\n' "$output"
