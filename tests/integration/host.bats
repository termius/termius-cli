#!/usr/bin/env bats

@test "host help by arg" {
    run serverauditor host --help
    [ "$status" -eq 0 ]
}

@test "host help command" {
    run serverauditor help host
    [ "$status" -eq 0 ]
}

@test "Add general host" {
    rm ~/.serverauditor.storage || true
    run serverauditor host -L test --port 2022 --username root --password password
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Add 2 hosts" {
    rm ~/.serverauditor.storage || true
    run serverauditor host -L test_1 --port 2022 --username root --password 'pa$$word'
    run serverauditor host -L test_2 --port 2222 --username root --password 'password'
    run serverauditor host -L test_3 --port 22 --username root --password 'psswrd'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}
