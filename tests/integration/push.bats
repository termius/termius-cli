#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "push help by arg" {
    run termius push --help
    [ "$status" -eq 0 ]
}

@test "push help command" {
    run termius help push
    [ "$status" -eq 0 ]
}

@test "push logged in" {
    login_termius

    termius pull -p $SERVERAUDITOR_PASSWORD
    run termius push -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
}

@test "push nothing logged in incorrect password" {
    login_termius

    run termius push -p "" --debug
    echo ${lines[*]}
    [ "$status" -eq 1 ]
}

@test "push not logged in" {
    termius logout
    run termius pull -p ""
    [ "$status" -eq 1 ]
}
