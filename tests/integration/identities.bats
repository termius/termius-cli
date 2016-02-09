#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "Identities help by arg" {
    run serverauditor identities --help
    [ "$status" -eq 0 ]
}

@test "Identities help command" {
    run serverauditor help identities
    [ "$status" -eq 0 ]
}

@test "List general identities in table format" {
    rm ~/.serverauditor.storage || true
    serverauditor identity -L local --username 'ROOT' --password 'pa'
    run serverauditor identities
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'sshidentity_set') -eq 1 ]
}
