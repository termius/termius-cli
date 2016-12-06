#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "logout help by arg" {
    run termius logout --help
    [ "$status" -eq 0 ]
}

@test "logout help command" {
    run termius help logout
    [ "$status" -eq 0 ]
}

@test "login & logout by tester account" {
    if [ "$SERVERAUDITOR_USERNAME" = '' ] || [ "$SERVERAUDITOR_PASSWORD" = '' ];then
        skip '$SERVERAUDITOR_USERNAME and $SERVERAUDITOR_PASSWORD are not set!'
    fi

    rm ~/.termius/config || true
    termius login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
    populate_storage
    run termius logout
    [ "$status" -eq 0 ]
    [ -z "$(cat ~/.termius/config)" ]
    assert_clear_storage
}
