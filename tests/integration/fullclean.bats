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

    run serverauditor fullclean -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
    [ "$(get_models_set 'sshkeycrypt_set')" = "[]" ]
    [ "$(get_models_set 'tag_set')" = "[]" ]
    [ "$(get_models_set 'snippet_set')" = "[]" ]
    [ "$(get_models_set 'snippet_set')" = "[]" ]
    [ "$(get_models_set 'sshidentity_set')" = "[]" ]
    [ "$(get_models_set 'taghost_set')" = "[]" ]
    [ "$(get_models_set 'sshconfig_set')" = "[]" ]
    [ "$(get_models_set 'group_set')" = "[]" ]
    [ "$(get_models_set 'host_set')" = "[]" ]
    [ "$(get_models_set 'pfrule_set')" = "[]" ]
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
    rm ~/.serverauditor.storage || true
}

