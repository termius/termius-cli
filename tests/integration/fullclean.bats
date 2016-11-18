#!/usr/bin/env bats
load test_helper

@test "fullclean help by arg" {
    run termius fullclean --help
    [ "$status" -eq 0 ]
}

@test "fullclean help command" {
    run termius help fullclean
    [ "$status" -eq 0 ]
}

@test "fullclean logged in" {
    login_termius
    termius pull -p $SERVERAUDITOR_PASSWORD

    run termius fullclean -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
    assert_clear_storage
}

@test "fullclean logged in incorrect password" {
    login_termius

    run termius fullclean -p ""
    [ "$status" -eq 1 ]
}

@test "fullclean not logged in" {
    termius logout
    run termius fullclean -p ""
    [ "$status" -eq 1 ]
}

setup() {
    clean_storage || true
}

