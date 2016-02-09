#!/usr/bin/env bats
load test_helper

setup() {
    clean_storage || true
}

@test "hosts help by arg" {
    run serverauditor hosts --help
    [ "$status" -eq 0 ]
}

@test "hosts help command" {
    run serverauditor help hosts
    [ "$status" -eq 0 ]
}

@test "List hosts in table format" {
    serverauditor host -L test --port 2022 --address 123.2.3.2 --username root --password password
    run serverauditor hosts
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "List hosts filter by tag" {
    serverauditor host -L test --port 2022 --address localhost --username root --password password -t A

    run serverauditor hosts --tags A
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "List hosts in group" {
    group=$(serverauditor group --port 2022)
    serverauditor host -L test --group $group --address localhost --username root --password password

    run serverauditor hosts --group $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}

@test "List hosts in group filter by tag" {
    group=$(serverauditor group --port 2022)
    serverauditor host -L test --group $group --address localhost --username root --password password -t A

    run serverauditor hosts --tags A --group $group
    [ "$status" -eq 0 ]
    [ $(get_models_set_length 'host_set') -eq 1 ]
}
