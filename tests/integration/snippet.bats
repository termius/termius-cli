#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "Snippet help by arg" {
    run serverauditor snippet --help
    [ "$status" -eq 0 ]
}

@test "Snippet help command" {
    run serverauditor help snippet
    [ "$status" -eq 0 ]
}

@test "Add general snippet" {
    run serverauditor snippet -L test --script 'ls'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 1 ]
    snippet=${lines[1]}
    [ "$(get_model_field 'snippet_set' $snippet 'label')" = '"test"' ]
    [ "$(get_model_field 'snippet_set' $snippet 'script')" = "\"ls\"" ]
}

@test "Add many snippets" {
    run serverauditor snippet -L test_1 --script 'ls'
    run serverauditor snippet -L test_2 --script 'whoami'
    run serverauditor snippet -L test_3 --script 'exit'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 3 ]
}

@test "Update snippet" {
    snippet=$(serverauditor snippet -L test --script 'ls')
    run serverauditor snippet --script 'cd /' $snippet
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 1 ]
    [ "$(get_model_field 'snippet_set' $snippet 'label')" = '"test"' ]
    [ "$(get_model_field 'snippet_set' $snippet 'script')" = "\"cd /\"" ]
}

@test "Update many snippets" {
    snippet1=$(serverauditor snippet -L test_1 --script 'ls')
    snippet2=$(serverauditor snippet -L test_2 --script 'whoami')
    snippet3=$(serverauditor snippet -L test_3 --script 'exit')
    run serverauditor snippet --script 'cd /' $snippet1 $snippet2 $snippet3
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 3 ]
}

@test "Delete snippet" {
    snippet=$(serverauditor snippet -L test --script 'ls')
    run serverauditor snippet --delete $snippet
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 0 ]
}

@test "Delete many snippets" {
    snippet1=$(serverauditor snippet -L test_1 --script 'ls')
    snippet2=$(serverauditor snippet -L test_2 --script 'whoami')
    snippet3=$(serverauditor snippet -L test_3 --script 'exit')
    run serverauditor snippet --delete $snippet1 $snippet2 $snippet3
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'snippet_set') -eq 0 ]
}
