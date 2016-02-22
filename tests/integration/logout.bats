#!/usr/bin/env bats
load test_helper

@test "logout help by arg" {
    run serverauditor logout --help
    [ "$status" -eq 0 ]
}

@test "logout help command" {
    run serverauditor help logout
    [ "$status" -eq 0 ]
}

@test "login & logout by tester account" {
    if [ "$SERVERAUDITOR_USERNAME" = '' ] || [ "$SERVERAUDITOR_PASSWORD" = '' ];then
        skip '$SERVERAUDITOR_USERNAME and $SERVERAUDITOR_PASSWORD are not set!'
    fi

    rm ~/.serverauditor/config || true
    serverauditor login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
    populate_storage
    run serverauditor logout
    [ "$status" -eq 0 ]
    [ -z "$(cat ~/.serverauditor/config)" ]
    assert_clear_storage
}
