#!/usr/bin/env bats

@test "bash complete output" {
    run termius complete
    [ "$status" -eq 0 ]
}

@test "bash complete" {
    run source <(termius complete)
    [ "$status" -eq 0 ]
}
