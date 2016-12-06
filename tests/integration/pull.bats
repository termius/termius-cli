#!/usr/bin/env bats
load test_helper


setup() {
    clean_storage || true
}

@test "pull help by arg" {
    run termius pull --help
    [ "$status" -eq 0 ]
}

@test "pull help command" {
    run termius help pull
    [ "$status" -eq 0 ]
}

@test "pull logged in" {
    login_termius

    run termius pull -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
}

@test "pull logged in incorrect password" {
    login_termius

    run termius pull -p ""
    [ "$status" -eq 1 ]
}

@test "pull not logged in" {
    termius logout
    run termius pull -p ""
    [ "$status" -eq 1 ]
}
