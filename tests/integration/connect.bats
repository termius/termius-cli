#!/usr/bin/env bats

@test "connect help by arg" {
    run termius connect --help
    [ "$status" -eq 0 ]
}

@test "connect help command" {
    run termius help connect
    [ "$status" -eq 0 ]
}
