#!/usr/bin/env bats

@test "connect help by arg" {
    run serverauditor connect --help
    [ "$status" -eq 0 ]
}

@test "connect help command" {
    run serverauditor help connect
    [ "$status" -eq 0 ]
}
