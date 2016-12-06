#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "tags help by arg" {
    run termius tags --help
    [ "$status" -eq 0 ]
}

@test "tags help command" {
    run termius help tags
    [ "$status" -eq 0 ]
}

@test "tags list" {
    termius host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C

    run termius tags
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]
}

@test "tags filter not existed" {
    run termius tags 1
    [ "$status" -eq 1 ]
}

@test "tags list filter some" {
    termius host -L test --address localhost --username root --password password -t A -t B -t C
    termius host -L test --address local2 --username root -t 1 -t A -t B
    termius host -L test --address host1 --password password -t A

    run termius tags A B --debug
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'tag_set') -eq 4 ]
    [ $(get_models_set_length 'taghost_set') -eq 7 ]
}
