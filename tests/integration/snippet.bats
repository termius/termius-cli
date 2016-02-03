#!/usr/bin/env bats

setup() {
    rm ~/.serverauditor.storage || true
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
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add many snippets" {
    run serverauditor snippet -L test_1 --script 'ls'
    run serverauditor snippet -L test_2 --script 'whoami'
    run serverauditor snippet -L test_3 --script 'exit'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update snippet" {
    snippet=$(serverauditor snippet -L test --script 'ls')
    run serverauditor snippet --script 'cd /' $snippet
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update many snippets" {
    snippet1=$(serverauditor snippet -L test_1 --script 'ls')
    snippet2=$(serverauditor snippet -L test_2 --script 'whoami')
    snippet3=$(serverauditor snippet -L test_3 --script 'exit')
    run serverauditor snippet --script 'cd /' $snippet1 $snippet2 $snippet3
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete snippet" {
    snippet=$(serverauditor snippet -L test --script 'ls')
    run serverauditor snippet --delete $snippet
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete many snippets" {
    snippet1=$(serverauditor snippet -L test_1 --script 'ls')
    snippet2=$(serverauditor snippet -L test_2 --script 'whoami')
    snippet3=$(serverauditor snippet -L test_3 --script 'exit')
    run serverauditor snippet --delete $snippet1 $snippet2 $snippet3
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
