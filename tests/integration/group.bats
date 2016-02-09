#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "group help by arg" {
    run serverauditor group --help
    [ $status -eq 0 ]
}

@test "group help command" {
    run serverauditor help group
    [ $status -eq 0 ]
}

@test "Add general group" {
    run serverauditor group -L 'test group' --port 2 --username 'use r name' --debug
    [ $status -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "Add group to main group" {
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group -L 'test group' --port 2 --username 'user' --parent-group $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
}

@test "Update group" {
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group -L 'test group' --port 2 --username 'user' $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "Update group add in self" {
    group=$(serverauditor group -L 'test group' --port 2 --username 'name')
    run serverauditor group -L 'test group' --port 2 --username 'user' --parent-group $group $group
    [ "$status" -eq 1 ]
    [ $(get_models_set_length 'group_set') -eq 1 ]
}

@test "Update group add in parent group" {
    parent_group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group=$(serverauditor group -L 'test group' --port 2 --username 'name')
    run serverauditor group -L 'test group' --port 2 --username 'user' --parent-group $parent_group $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
}

@test "Update many groups" {
    group1=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group2=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group -L 'test group' --port 2 --username 'user' $group1 $group2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 2 ]
}

@test "Delete group" {
    group=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --delete $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 0 ]
}

@test "Delete many groups" {
    group1=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    group2=$(serverauditor group -L 'test group' --port 2 --username 'use r name')
    run serverauditor group --delete $group1 $group2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'group_set') -eq 0 ]
}
