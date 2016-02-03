#!/usr/bin/env bats

setup() {
    rm ~/.serverauditor.storage || true
    touch key
}

teardown() {
    rm key
}

@test "keys help by arg" {
    run serverauditor keys --help
    [ "$status" -eq 0 ]
}

@test "keys help command" {
    run serverauditor help keys
    [ "$status" -eq 0 ]
}

@test "List snippets in table format" {
    serverauditor key -L test -i key
    run serverauditor keys
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
