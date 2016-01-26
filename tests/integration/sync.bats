#!/usr/bin/env bats

@test "sync help by arg" {
    run serverauditor sync --help
    [ "$status" -eq 0 ]
}

@test "sync help command" {
    run serverauditor help sync
    [ "$status" -eq 0 ]
}

@test "sync not supported service" {
    run serverauditor sync awesomeservice
    [ "$status" -eq 1 ]
    [ "$output" = "Do not support service: awesomeservice." ]
}
