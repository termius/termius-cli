#!/usr/bin/env bats

@test "sync help by arg" {
    run termius sync --help
    [ "$status" -eq 0 ]
}

@test "sync help command" {
    run termius help sync
    [ "$status" -eq 0 ]
}

@test "sync not supported service" {
    run termius sync awesomeservice
    [ "$status" -eq 1 ]
    [ "$output" = "Do not support service: awesomeservice." ]
}
