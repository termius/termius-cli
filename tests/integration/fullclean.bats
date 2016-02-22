#!/usr/bin/env bats
load test_helper

@test "fullclean help by arg" {
    run serverauditor fullclean --help
    [ "$status" -eq 0 ]
}

@test "fullclean help command" {
    run serverauditor help fullclean
    [ "$status" -eq 0 ]
}

@test "fullclean logged in" {
    login_serverauditor
    serverauditor pull -p $SERVERAUDITOR_PASSWORD

    run serverauditor fullclean -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
    assert_clear_storage
}

@test "fullclean logged in incorrect password" {
    login_serverauditor

    run serverauditor fullclean -p ""
    [ "$status" -eq 1 ]
}

@test "fullclean not logged in" {
    serverauditor logout
    run serverauditor fullclean -p ""
    [ "$status" -eq 1 ]
}

setup() {
    clean_storage || true
}

