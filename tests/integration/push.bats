#!/usr/bin/env bats

@test "push help by arg" {
    run serverauditor push --help
    [ "$status" -eq 0 ]
}

@test "push help command" {
    run serverauditor help push
    [ "$status" -eq 0 ]
}
