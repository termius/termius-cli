#!/usr/bin/env bats

setup() {
    rm ~/.serverauditor.storage || true
}

@test "host help by arg" {
    run serverauditor host --help
    [ "$status" -eq 0 ]
}

@test "host help command" {
    run serverauditor help host
    [ "$status" -eq 0 ]
}

@test "Add general host" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add many hosts" {
    run serverauditor host -L test_1 --port 2022 --address 127.0.0.1 --username root --password 'pa$$word'
    run serverauditor host -L test_2 --port 2222 --address google.com --username root --password 'password'
    run serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
