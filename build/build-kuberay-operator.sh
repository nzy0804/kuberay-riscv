#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"

archive="$build_root/downloads/go1.24.6.linux-riscv64.tar.gz"
download_verified https://go.dev/dl/go1.24.6.linux-riscv64.tar.gz \
    "$archive" e92c19ff15a9004fe43e1f62d433555250ef9fe3fabee3dc29ebd4802c2b8021
go_root="$build_root/tools/go1.24.6"
mkdir -- "$go_root"
tar -xzf "$archive" --strip-components=1 -C "$go_root"
go="$go_root/bin/go"
export GOROOT="$go_root" GOTOOLCHAIN=local GOWORK=off GOFLAGS=
export GOCACHE="$build_root/cache/go-build" GOMODCACHE="$build_root/cache/go-mod"
export CGO_ENABLED=0 GOOS=linux GOARCH=riscv64
[[ "$("$go" version)" == "go version go1.24.6 linux/riscv64" ]] || die "Unexpected Go version."

source_dir="$build_root/src/kuberay"
checkout_pinned https://github.com/ray-project/kuberay.git v1.5.2 \
    9f65eca1d6226d20f9e7c340f2af27cc4a1c9985 "$source_dir"
cd -- "$source_dir/ray-operator"
output="$build_root/artifacts/manager"
"$go" build -mod=readonly -p "$build_jobs" -trimpath -o "$output" main.go
file "$output"
sha256sum "$output"
