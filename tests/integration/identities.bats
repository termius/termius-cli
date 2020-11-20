#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "Identities help by arg" {
    run termius identities --help
    [ "$status" -eq 0 ]
}

@test "Identities help command" {
    run termius help identities
    [ "$status" -eq 0 ]
}

@test "List general identities in table format" {
    rm ~/.termius.storage || true
    termius identity -L local --username 'ROOT'
    run termius identities
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'identity_set') -eq 1 ]
}
