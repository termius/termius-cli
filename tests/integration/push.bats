#!/usr/bin/env bats
load test_helper

@test "push help by arg" {
    run serverauditor push --help
    [ "$status" -eq 0 ]
}

@test "push help command" {
    run serverauditor help push
    [ "$status" -eq 0 ]
}

@test "push logged in" {
    login_serverauditor

    serverauditor pull -p $SERVERAUDITOR_PASSWORD
    run serverauditor push -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
}

@test "push nothing logged in incorrect password" {
    login_serverauditor

    run serverauditor push -p "" --debug
    echo ${lines[*]}
    [ "$status" -eq 1 ]
}

@test "push not logged in" {
    serverauditor logout
    run serverauditor pull -p ""
    [ "$status" -eq 1 ]
}

setup() {
    rm ~/.serverauditor.storage || true
}
