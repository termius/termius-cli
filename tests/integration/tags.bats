#!/usr/bin/env bats

@test "tags help by arg" {
    run serverauditor tags --help
    [ "$status" -eq 0 ]
}

@test "tags help command" {
    run serverauditor help tags
    [ "$status" -eq 0 ]
}

@test "tags list" {
    serverauditor host -L test --port 2022 --address localhost --username root --password password -t A,B,C

    run serverauditor tags
    [ "$status" -eq 0 ]
}
