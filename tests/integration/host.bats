#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
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
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Add host to group" {
    group=$(serverauditor group --port 2022)
    run serverauditor host -L test --group $group --address localhost --debug
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Add many hosts" {
    run serverauditor host -L test_1 --port 2022 --address 127.0.0.1 --username root --password 'pa$$word'
    run serverauditor host -L test_2 --port 2222 --address google.com --username root --password 'password'
    run serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 3 ]
}

@test "Update host" {
    host=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Update host add to group" {
    group=$(serverauditor group --port 2022)
    host=$(serverauditor host --address localhost -L test)
    run serverauditor host --group $group $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "Update many hosts" {
    host1=$(serverauditor host -L test_2 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' $host1 $hots2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "Update hosts with same name" {
    host1=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host -L test_3 --port 22 --address google --username root --password '' 'test_3'
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
}

@test "Delete host" {
    host=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host --delete $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 0 ]
}

@test "Delete many hosts" {
    host1=$(serverauditor host -L test_2 --port 22 --address google.com --username root --password 'psswrd')
    host2=$(serverauditor host -L test_3 --port 22 --address google.com --username root --password 'psswrd')
    run serverauditor host --delete $host1 $host2
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 0 ]
}

@test "Create with tag" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 1 ]
    [ $(get_models_set_length 'taghost_set') -eq 1 ]
}

@test "Create with 3 tags" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]
}

@test "Create 2 hosts with 3 tags" {
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 2 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 6 ]
}

@test "Update host with 3 same tags" {
    host=$(serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C)
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 3 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]
}

@test "Update host with 3 diff tags" {
    host=$(serverauditor host -L test --port 2022 --address localhost --username root --password password -t A -t B -t C)
    run serverauditor host -L test --port 2022 --address localhost --username root --password password -t D -t E -t F $host
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
    [ $(get_models_set_length 'tag_set') -eq 6 ]
    [ $(get_models_set_length 'taghost_set') -eq 3 ]
}
