#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "snippets help by arg" {
    run serverauditor snippets --help
    [ "$status" -eq 0 ]
}

@test "snippets help command" {
    run serverauditor help snippets
    [ "$status" -eq 0 ]
}

@test "List snippets in table format" {
    serverauditor snippet -L test --script 'ls'
    run serverauditor snippets
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 1 ]
}
