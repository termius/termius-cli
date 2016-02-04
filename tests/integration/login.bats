#!/usr/bin/env bats

@test "login help by arg" {
    run serverauditor login --help
    [ "$status" -eq 0 ]
}

@test "login help command" {
    run serverauditor help login
    [ "$status" -eq 0 ]
}

@test "login by tester account" {
    if [ "$SERVERAUDITOR_USERNAME" == '' ] || [ "$SERVERAUDITOR_PASSWORD" == '' ];then
        skip '$SERVERAUDITOR_USERNAME and $SERVERAUDITOR_PASSWORD are not set!'
    fi
    rm ~/.serverauditor || true

    run serverauditor login --username $SERVERAUDITOR_USERNAME -p $SERVERAUDITOR_PASSWORD
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor) ]
}
