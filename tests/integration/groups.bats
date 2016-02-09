#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}


@test "groups help by arg" {
    run serverauditor groups --help
    [ "$status" -eq 0 ]
}

@test "groups help command" {
    run serverauditor help groups
    [ "$status" -eq 0 ]
}

@test "List groups in table format" {
    serverauditor group -L 'test group' --port 2 --username 'use r name'
    run serverauditor groups
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "List groups in subgroup in table format" {
    parent=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    serverauditor group -L 'test group' --parent-group $parent --port 2 --username 'use r name'
    run serverauditor groups $parent
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
}

@test "List groups recursivly in subgroup in table format" {
    grandparent=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    parent=$(serverauditor group -L 'test group' --parent-group $grandparent --port 2 --username 'use r name')
    serverauditor group -L 'test group' --parent-group $parent --port 2 --username 'use r name'
    run serverauditor groups $grandparent
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 3 ]
}
