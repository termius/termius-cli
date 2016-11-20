#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "info help by arg" {
    run termius settings --help
    [ "$status" -eq 0 ]
}

@test "info help command" {
    run termius help settings
    [ "$status" -eq 0 ]
}

@test "Settings yes" {
    run termius settings --synchronize-key=yes --agent-forwarding yes
    [ "$status" -eq 0 ]
}

@test "Settings no" {
    run termius settings --synchronize-key=no --agent-forwarding no
    [ "$status" -eq 0 ]
}
