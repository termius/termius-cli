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

    run serverauditor push -p $Serverauditor_password
    [ "$status" -eq 0 ]
}

@test "push logged in incorrect password" {
    login_serverauditor

    run serverauditor push -p ""
    [ "$status" -eq 0 ]
}

@test "push not logged in" {

    run serverauditor pull -p ""
    [ "$status" -eq 0 ]
}
