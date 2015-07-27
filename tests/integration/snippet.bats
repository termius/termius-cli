#!/usr/bin/env bats

setup() {
    rm ~/.serverauditor.storage || true
}

@test "Snippet help by arg" {
    run serverauditor host --help
    [ "$status" -eq 0 ]
}

@test "Snippet help command" {
    run serverauditor help host
    [ "$status" -eq 0 ]
}

@test "Add general snippet" {
    run serverauditor snippet -L test --script 'ls'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add many snippets" {
    run serverauditor snippet -L test_1 --script 'ls'
    run serverauditor snippet -L test_2 --script 'whoami'
    run serverauditor snippet -L test_3 --script 'exit'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
