#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "info help by arg" {
    run serverauditor settings --help
    [ "$status" -eq 0 ]
}

@test "info help command" {
    run serverauditor help settings
    [ "$status" -eq 0 ]
}

@test "Settings yes" {
    run serverauditor settings --synchronize-key=yes --agent-forwarding yes
    [ "$status" -eq 0 ]
}

@test "Settings no" {
    run serverauditor settings --synchronize-key=no --agent-forwarding no
    [ "$status" -eq 0 ]
}
