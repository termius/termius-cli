#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "tags help by arg" {
    run serverauditor tags --help
    [ "$status" -eq 0 ]
}

@test "tags help command" {
    run serverauditor help tags
    [ "$status" -eq 0 ]
}

@test "tags list" {
    serverauditor host -L test --port 2022 --address localhost --username root --password password -t A,B,C

    run serverauditor tags
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]
}

@test "tags filter not existed" {
    run serverauditor tags 1
    [ "$status" -eq 1 ]
}

@test "tags list filter some" {
    serverauditor host -L test --address localhost --username root --password password -t A,B,C
    serverauditor host -L test --address local2 --username root -t 1,A,B
    serverauditor host -L test --address host1 --password password -t A

    run serverauditor tags A B --debug
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'tag_set') -eq 4 ]
    [ $(get_models_set_length 'taghost_set') -eq 7 ]
}
