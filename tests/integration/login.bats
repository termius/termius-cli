#!/usr/bin/env bats
load test_helper

@test "login help by arg" {
    run termius login --help
    [ "$status" -eq 0 ]
}

@test "login help command" {
    run termius help login
    [ "$status" -eq 0 ]
}

@test "log into tester account" {
    if [ "$SERVERAUDITOR_USERNAME" == '' ] || [ "$SERVERAUDITOR_PASSWORD" == '' ];then
        skip '$SERVERAUDITOR_USERNAME or $SERVERAUDITOR_PASSWORD are not set!'
    fi
    rm ~/.termius/config || true

    run termius login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
    ! [ -z "$(cat ~/.termius/config)" ]
}

@test "Change tester account" {
    if [ "$SERVERAUDITOR_USERNAME" == '' ] || [ "$SERVERAUDITOR_PASSWORD" == '' ] ||
        [ "$SERVERAUDITOR_USERNAME_2" == '' ] || [ "$SERVERAUDITOR_PASSWORD_2" == '' ] ;then
        skip '$SERVERAUDITOR_USERNAME or $SERVERAUDITOR_PASSWORD or $SERVERAUDITOR_USERNAME_2 or $SERVERAUDITOR_PASSWORD_2 are not set!'
    fi
    rm ~/.termius/config || true

    termius login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
    populate_storage
    run termius login --username $SERVERAUDITOR_USERNAME_2 -p $SERVERAUDITOR_PASSWORD_2
    [ "$status" -eq 0 ]
    ! [ -z "$(cat ~/.termius/config)" ]
    assert_clear_storage
}
