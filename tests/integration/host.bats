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

@test "Update host" {
    host=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' $host
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update many hosts" {
    host1=$(serverauditor host -L test_2 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' $host1 $hots2
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Update hosts with same name" {
    host1=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' 'test_3'
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete host" {
    host=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host --delete $host --debug
    echo ${lines[*]}
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Delete many hosts" {
    host1=$(serverauditor host -L test_2 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host --delete $host1 $hots2
    [ "$status" -eq 0 ]
    ! [ -z $(cat ~/.serverauditor.storage) ]
}

@test "Create with tag" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A
    [ "$status" -eq 0 ]
}

@test "Create with 3 tags" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A,B,C
    [ "$status" -eq 0 ]
}
