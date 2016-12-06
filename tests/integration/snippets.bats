#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "snippets help by arg" {
    run termius snippets --help
    [ "$status" -eq 0 ]
}

@test "snippets help command" {
    run termius help snippets
    [ "$status" -eq 0 ]
}

@test "List snippets in table format" {
    termius snippet -L test --script 'ls'
    run termius snippets
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 1 ]
}
