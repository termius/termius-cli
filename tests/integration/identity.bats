#!/usr/bin/env bats

@test "Identity help by arg" {
    run serverauditor identity --help
    [ "$status" -eq 0 ]
}

@test "Identity help command" {
    run serverauditor help identity
    [ "$status" -eq 0 ]
}

@test "Add general identity" {
    rm ~/.serverauditor.storage || true
    run serverauditor identity -L local --username 'ROOT' --password 'pa'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
