#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

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

    run serverauditor pull -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
}

@test "pull logged in incorrect password" {
    login_serverauditor

    run serverauditor pull -p ""
    [ "$status" -eq 1 ]
}

@test "pull not logged in" {
    serverauditor logout
    run serverauditor pull -p ""
    [ "$status" -eq 1 ]
}
