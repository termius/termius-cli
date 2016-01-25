#!/usr/bin/env bats

@test "pfrules help by arg" {
    run serverauditor pfrules --help
    [ "$status" -eq 0 ]
}

@test "pfrules help command" {
    run serverauditor help pfrules
    [ "$status" -eq 0 ]
}

@test "List pfrules in table format" {
    rm ~/.serverauditor.storage || true
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    serverauditor pfrule --dynamic --host $host 127.0.0.1:2222
    run serverauditor pfrules
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
