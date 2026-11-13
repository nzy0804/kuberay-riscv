# Shared settings for the native Linux RISC-V build scripts.
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
build_root="${BUILD_ROOT:-$repo_root/.build-riscv}"
build_jobs="${BUILD_JOBS:-8}"

die() {
    printf '%s\n' "$*" >&2
    exit 1
}

if [[ "$(uname -s)" != Linux || "$(uname -m)" != riscv64 ]]; then
    die "Run this build on a Linux riscv64 host."
fi
[[ "$build_jobs" =~ ^[1-9][0-9]*$ ]] || die "BUILD_JOBS must be a positive integer."

mkdir -p -- "$build_root"
build_root="$(cd -- "$build_root" && pwd -P)"
[[ "$build_root" =~ ^/[a-zA-Z0-9_./-]+$ ]] || die "Use a BUILD_ROOT without spaces or shell metacharacters."
mkdir -p -- "$build_root"/{downloads,src,tools/bin,cache,tmp,artifacts}
export TMPDIR="$build_root/tmp"

download_verified() {
    local url="$1" path="$2" sha="$3"
    if [[ ! -f "$path" ]]; then
        curl --fail --location --retry 3 --connect-timeout 20 --output "$path.part" "$url"
        printf '%s  %s\n' "$sha" "$path.part" | sha256sum --check -
        mv -- "$path.part" "$path"
    fi
    printf '%s  %s\n' "$sha" "$path" | sha256sum --check -
}

checkout_pinned() {
    local url="$1" ref="$2" sha="$3" dir="$4"
    [[ ! -e "$dir" ]] || die "Source path already exists: $dir. Use a fresh BUILD_ROOT."
    git clone --depth 1 --branch "$ref" -- "$url" "$dir"
    [[ "$(git -C "$dir" rev-parse HEAD)" == "$sha" ]] || die "Unexpected source commit for $ref."
}

configure_java() {
    if [[ -z "${JAVA_HOME:-}" ]]; then
        local javac
        javac="$(command -v javac)" || die "Install JDK 11 or set JAVA_HOME."
        JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$javac")")")"
    fi
    [[ "$JAVA_HOME" =~ ^/[a-zA-Z0-9_./-]+$ ]] || die "Use an absolute JAVA_HOME without spaces."
    [[ -x "$JAVA_HOME/bin/java" && -x "$JAVA_HOME/bin/javac" ]] || die "JAVA_HOME must point to a JDK."
    [[ "$("$JAVA_HOME/bin/javac" -version 2>&1)" =~ ^javac\ 11([.]|$) ]] || die "Use JDK 11."
    export JAVA_HOME
}
