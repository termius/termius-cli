#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "pfrules help by arg" {
    run termius pfrules --help
    [ "$status" -eq 0 ]
}

@test "pfrules help command" {
    run termius help pfrules
    [ "$status" -eq 0 ]
}

@test "List pfrules in table format" {
    host="$(termius host --label test2 --address 127.0.0.1)"
    termius pfrule --dynamic --host $host --binding 127.0.0.1:2222
    run termius pfrules
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'pfrule_set') -eq 1 ]
}
