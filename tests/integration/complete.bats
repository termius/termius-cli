#!/usr/bin/env bats

@test "bash complete output" {
    run serverauditor complete
    [ "$status" -eq 0 ]
}

@test "bash complete" {
    run source <(serverauditor complete)
    [ "$status" -eq 0 ]
}
