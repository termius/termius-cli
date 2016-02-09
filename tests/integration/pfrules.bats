#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "pfrules help by arg" {
    run serverauditor pfrules --help
    [ "$status" -eq 0 ]
}

@test "pfrules help command" {
    run serverauditor help pfrules
    [ "$status" -eq 0 ]
}

@test "List pfrules in table format" {
    host="$(serverauditor host --label test2 --address 127.0.0.1)"
    serverauditor pfrule --dynamic --host $host --binding 127.0.0.1:2222
    run serverauditor pfrules
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
}
