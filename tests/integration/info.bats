#!/usr/bin/env bats


@test "info help by arg" {
    run serverauditor info --help
    [ "$status" -eq 0 ]
}

@test "info help command" {
    run serverauditor help info
    [ "$status" -eq 0 ]
}

@test "info host use default formatter" {
    host=$(serverauditor host -L test --port 2022 --address localhost --username root --password password)
    run serverauditor info $host
    [ "$status" -eq 0 ]
}

@test "info host use ssh formatter" {
    host=$(serverauditor host -L test --port 2022 --address localhost --username root --password password)
    run serverauditor info $host -f ssh
    [ "$status" -eq 0 ]
}


@test "info group use default formatter" {
    group=$(serverauditor group -L test --port 2022)
    run serverauditor info --group $group --debug
    echo ${lines[*]}
    [ "$status" -eq 0 ]
}

@test "info group use ssh formatter" {
    group=$(serverauditor group -L test --port 2022)
    run serverauditor info --group $group -f ssh
    [ "$status" -eq 0 ]
}

@test "info host not existed" {
    group=$(serverauditor group -L test --port 2022)
    run serverauditor info $group
    [ "$status" -eq 1 ]
}
@test "info group not existed" {
    host=$(serverauditor host -L test --port 2022 --address localhost --username root --password password)
    run serverauditor info --group $host
    [ "$status" -eq 1 ]
}

setup() {
    rm ~/.serverauditor.storage || true
}
