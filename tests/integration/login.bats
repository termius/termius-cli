#!/usr/bin/env bats
load test_helper

@test "login help by arg" {
    run serverauditor login --help
    [ "$status" -eq 0 ]
}

@test "login help command" {
    run serverauditor help login
    [ "$status" -eq 0 ]
}

@test "log into tester account" {
    if [ "$SERVERAUDITOR_USERNAME" == '' ] || [ "$SERVERAUDITOR_PASSWORD" == '' ];then
        skip '$SERVERAUDITOR_USERNAME or $SERVERAUDITOR_PASSWORD are not set!'
    fi
    rm ~/.serverauditor/config || true

    run serverauditor login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
    ! [ -z "$(cat ~/.serverauditor/config)" ]
}

@test "Change tester account" {
    if [ "$SERVERAUDITOR_USERNAME" == '' ] || [ "$SERVERAUDITOR_PASSWORD" == '' ] ||
        [ "$SERVERAUDITOR_USERNAME_2" == '' ] || [ "$SERVERAUDITOR_PASSWORD_2" == '' ] ;then
        skip '$SERVERAUDITOR_USERNAME or $SERVERAUDITOR_PASSWORD or $SERVERAUDITOR_USERNAME_2 or $SERVERAUDITOR_PASSWORD_2 are not set!'
    fi
    rm ~/.serverauditor/config || true

    serverauditor login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
    populate_storage
    run serverauditor login --username $SERVERAUDITOR_USERNAME_2 -p $SERVERAUDITOR_PASSWORD_2
    [ "$status" -eq 0 ]
    ! [ -z "$(cat ~/.serverauditor/config)" ]
    assert_clear_storage
}
