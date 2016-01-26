#!/usr/bin/env bats

@test "pull help by arg" {
    run serverauditor pull --help
    [ "$status" -eq 0 ]
}

@test "pull help command" {
    run serverauditor help pull
    [ "$status" -eq 0 ]
}

@test "pull logged in" {

    if [ "$Serverauditor_username" == '' ] || [ "$Serverauditor_password" == '' ];then
      skip '$Serverauditor_username and $Serverauditor_password are not set!'
    fi

    serverauditor login --username $Serverauditor_username -p $Serverauditor_password

    run serverauditor pull -p $Serverauditor_password
    [ "$status" -eq 0 ]
}

@test "pull logged in incorrect password" {

    if [ "$Serverauditor_username" == '' ] || [ "$Serverauditor_password" == '' ];then
      skip '$Serverauditor_username and $Serverauditor_password are not set!'
    fi

    serverauditor login --username $Serverauditor_username -p $Serverauditor_password

    run serverauditor pull -p ""
    [ "$status" -eq 0 ]
}

@test "pull not logged in" {

    run serverauditor pull -p ""
    [ "$status" -eq 0 ]
}
