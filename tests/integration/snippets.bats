#!/usr/bin/env bats

setup() {
    rm ~/.serverauditor.storage || true
}

@test "hosts help by arg" {
    run serverauditor hosts --help
    [ "$status" -eq 0 ]
}

@test "hosts help command" {
    run serverauditor help hosts
    [ "$status" -eq 0 ]
}

@test "List snippets in table format" {
    serverauditor snippet -L test --script 'ls'
    run serverauditor snippets
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
