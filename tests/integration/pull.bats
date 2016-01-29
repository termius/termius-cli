#!/usr/bin/env bats
load test_helper

@test "pull help by arg" {
    run serverauditor pull --help
    [ "$status" -eq 0 ]
}

@test "pull help command" {
    run serverauditor help pull
    [ "$status" -eq 0 ]
}

@test "pull logged in" {
    login_serverauditor

    run serverauditor pull -p $Serverauditor_password
    [ "$status" -eq 0 ]
}

@test "pull logged in incorrect password" {
    login_serverauditor

    run serverauditor pull -p ""
    [ "$status" -eq 0 ]
}

@test "pull not logged in" {

    run serverauditor pull -p ""
    [ "$status" -eq 0 ]
}
