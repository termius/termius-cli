#!/usr/bin/env bats

@test "group help by arg" {
    run serverauditor group --help
    [ "$status" -eq 0 ]
}

@test "group help command" {
    run serverauditor help group
    [ "$status" -eq 0 ]
}

@test "Add general group" {
    rm ~/.serverauditor.storage || true
    run serverauditor group -L 'test group' --port 2 --username 'use r name'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
